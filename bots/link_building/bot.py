"""Link Building bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BotBase
from bots.link_building.models import LinkBuildingOutput, LinkProspect, OutreachEmail
from bots.link_building.prompts import OUTREACH_EMAIL_PROMPT, PROSPECT_DISCOVERY_PROMPT
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)


class LinkBuildingBot(BotBase):
    name = "link_building"
    description = "Discovers link-building prospects and drafts personalised outreach emails"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    # ------------------------------------------------------------------

    def discover_prospects(
        self,
        keywords: list[str],
        city: str,
        cuisine: str,
    ) -> list[LinkProspect]:
        """Ask the LLM to suggest link-building prospects."""
        settings = get_settings()
        prompt = PROSPECT_DISCOVERY_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            city=city,
            cuisine=cuisine,
            keywords_list=", ".join(keywords),
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            from pydantic import BaseModel as PydanticBase

            class _ProspectResponse(PydanticBase):
                prospects: list[LinkProspect]

            result = self._llm.structured_completion(messages, _ProspectResponse)
            return result.prospects
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_prospects(raw)

    def generate_outreach_email(
        self, prospect: LinkProspect, restaurant_info: dict
    ) -> OutreachEmail:
        """Generate a tailored outreach email for a prospect."""
        prompt = OUTREACH_EMAIL_PROMPT.format(
            restaurant_name=restaurant_info.get("restaurant_name", ""),
            city=restaurant_info.get("city", ""),
            cuisine=restaurant_info.get("cuisine", ""),
            restaurant_website=restaurant_info.get("website", ""),
            prospect_url=prospect.url,
            prospect_notes=prospect.notes,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            result = self._llm.structured_completion(messages, OutreachEmail)
            return result
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_outreach_email(raw, prospect.url)

    def save_prospects_to_db(self, prospects: list[LinkProspect]) -> None:
        """Persist prospects to the database."""
        try:
            from common.storage.database import ProspectRepository, get_engine, init_db

            settings = get_settings()
            engine = get_engine(settings.database_url)
            init_db(engine)
            repo = ProspectRepository(engine)
            for p in prospects:
                repo.add(url=p.url, email=p.email, name=p.contact_name, notes=p.notes)
            logger.info("Saved %d prospects to DB", len(prospects))
        except Exception as exc:
            logger.error("save_prospects_to_db failed: %s", exc)

    def run(self, **kwargs) -> dict:
        settings = get_settings()
        restaurant_info = {
            "restaurant_name": kwargs.get("restaurant_name", settings.restaurant_name),
            "city": kwargs.get("city", settings.restaurant_city),
            "cuisine": kwargs.get("cuisine", settings.restaurant_cuisine),
            "website": kwargs.get("website", ""),
        }
        keywords = kwargs.get(
            "keywords",
            [f"{settings.restaurant_cuisine} restaurant {settings.restaurant_city}"],
        )

        logger.info("LinkBuildingBot: discovering prospects")
        prospects = self.discover_prospects(
            keywords, restaurant_info["city"], restaurant_info["cuisine"]
        )

        outreach_emails: list[OutreachEmail] = []
        for prospect in prospects[:5]:  # limit initial outreach batch
            logger.info("LinkBuildingBot: generating outreach for %s", prospect.url)
            email = self.generate_outreach_email(prospect, restaurant_info)
            outreach_emails.append(email)

        if kwargs.get("save_to_db", False):
            self.save_prospects_to_db(prospects)

        output = LinkBuildingOutput(
            prospects=prospects,
            outreach_emails=outreach_emails,
            generated_at=datetime.now(timezone.utc),
        )
        result = output.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_prospects(raw: str) -> list[LinkProspect]:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("prospects", data) if isinstance(data, dict) else data
            return [LinkProspect.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("_parse_prospects failed: %s", exc)
            return []

    @staticmethod
    def _parse_outreach_email(raw: str, prospect_url: str) -> OutreachEmail:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return OutreachEmail.model_validate(data)
        except Exception as exc:
            logger.error("_parse_outreach_email failed: %s", exc)
            return OutreachEmail(prospect_url=prospect_url, subject="Partnership opportunity", body=raw)
