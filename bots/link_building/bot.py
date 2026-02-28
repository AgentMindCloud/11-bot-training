"""Link-Building Outreach Bot (Bot 4)."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BaseBot
from bots.link_building.models import (
    LinkBuildingInput,
    OutreachProspect,
    ProspectStatus,
    ProspectSummary,
)
from common.crawling.crawler import WebCrawler
from common.db.database import get_session
from common.llm.client import LLMClient
from common.models.base import BotName
from infra.config import settings

logger = logging.getLogger(__name__)

PROSPECT_DISCOVERY_PROMPT = """
You are an SEO link-building expert. Given keywords and a location, suggest 5-8 types of websites that would be good link prospects for a local restaurant (food blogs, local directories, city guides, food critics, community sites).
Respond ONLY with valid JSON:
[
  {
    "site_type": "local food blog",
    "example_query": "Austin food blog site:blogspot.com OR site:wordpress.com",
    "rationale": "High DA local blogs pass good link equity"
  }
]
"""

OUTREACH_EMAIL_PROMPT = """
You are writing a personalized outreach email for link building for a local restaurant.
Be genuine, concise, and specific about why you're reaching out.
Respond ONLY with valid JSON:
{
  "subject": "...",
  "body": "Hi [Name],\\n\\n..."
}
"""


class LinkBuildingBot(BaseBot):
    """Discovers link prospects, generates outreach emails, tracks status in DB."""

    name = BotName.LINK_BUILDING

    def __init__(
        self,
        link_input: LinkBuildingInput | None = None,
        llm: LLMClient | None = None,
        crawler: WebCrawler | None = None,
    ) -> None:
        super().__init__()
        self.link_input = link_input or LinkBuildingInput(
            keywords=[settings.restaurant_cuisine, settings.restaurant_city],
            location=settings.restaurant_city,
        )
        self.llm = llm or LLMClient()
        self.crawler = crawler or WebCrawler()
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        logger.info("LinkBuildingBot: discovering prospects")
        prospect_types = self._discover_prospect_types()
        prospects: list[ProspectSummary] = []

        for seed_url in self.link_input.seed_urls:
            prospect = self._process_seed_url(seed_url)
            if prospect:
                self._save_prospect(prospect)
                prospects.append(
                    ProspectSummary(
                        url=prospect.url,
                        site_name=prospect.site_name or "",
                        contact_email=prospect.contact_email or "",
                        status=ProspectStatus(prospect.status),
                        outreach_subject=prospect.outreach_email_subject or "",
                    )
                )

        output = {
            "prospect_types": prospect_types,
            "prospects_processed": [p.model_dump() for p in prospects],
            "total_prospects": len(prospects),
        }
        self._save_output(output)
        return output

    def _discover_prospect_types(self) -> list[dict]:
        user_prompt = (
            f"Keywords: {', '.join(self.link_input.keywords)}\n"
            f"Location: {self.link_input.location}\n"
            f"Restaurant: {settings.restaurant_name}, {settings.restaurant_cuisine}"
        )
        raw = self.llm.chat(PROSPECT_DISCOVERY_PROMPT, user_prompt, temperature=0.5)
        return json.loads(raw)

    def _process_seed_url(self, url: str) -> OutreachProspect | None:
        page = self.crawler.fetch(url)
        if page.status_code == 0:
            return None

        outreach = self._generate_outreach_email(url, page.title)
        prospect = OutreachProspect(
            url=url,
            site_name=page.title[:200],
            contact_email=page.emails[0] if page.emails else "",
            status=ProspectStatus.PROSPECT.value,
            outreach_email_subject=outreach.get("subject", ""),
            outreach_email_body=outreach.get("body", ""),
            discovered_at=datetime.now(timezone.utc),
        )
        return prospect

    def _generate_outreach_email(self, url: str, site_name: str) -> dict:
        user_prompt = (
            f"Target site: {site_name} ({url})\n"
            f"Our restaurant: {settings.restaurant_name}, {settings.restaurant_cuisine} in {settings.restaurant_city}\n"
            f"Website: {settings.restaurant_website}"
        )
        raw = self.llm.chat(OUTREACH_EMAIL_PROMPT, user_prompt, temperature=0.6)
        return json.loads(raw)

    def _save_prospect(self, prospect: OutreachProspect) -> None:
        try:
            with get_session() as session:
                session.add(prospect)
                session.commit()
        except Exception as exc:
            logger.warning("Could not save prospect to DB: %s", exc)

    def _save_output(self, output: dict) -> None:
        path = settings.output_dir / "link_building_output.json"
        path.write_text(json.dumps(output, indent=2, default=str))
        logger.info("LinkBuildingBot: saved output to %s", path)
