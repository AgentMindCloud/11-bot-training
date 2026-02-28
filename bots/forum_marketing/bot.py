"""Forum Marketing bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BotBase
from bots.forum_marketing.models import ForumDraft, ForumDraftQueue
from bots.forum_marketing.prompts import FORUM_DRAFT_PROMPT, SENSITIVITY_CHECK_PROMPT
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)

_DEFAULT_TOPICS = [
    ("reddit", "Best Italian restaurants in NYC?"),
    ("yelp_talk", "Hidden gem restaurants in East Village"),
    ("tripadvisor", "Local neighbourhood dining recommendations"),
    ("nextdoor", "Restaurant recommendations for a special dinner"),
]


class ForumMarketingBot(BotBase):
    name = "forum_marketing"
    description = "Generates human-review-required forum post drafts for community marketing"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    # ------------------------------------------------------------------

    def generate_draft(self, topic: str, platform: str, restaurant_info: dict) -> ForumDraft:
        """Generate a single forum draft."""
        prompt = FORUM_DRAFT_PROMPT.format(
            restaurant_name=restaurant_info.get("restaurant_name", "Our Restaurant"),
            city=restaurant_info.get("city", ""),
            neighborhood=restaurant_info.get("neighborhood", ""),
            cuisine=restaurant_info.get("cuisine", ""),
            platform=platform,
            topic=topic,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            result = self._llm.structured_completion(messages, ForumDraft)
            result.status = "pending_review"
            return result
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_draft(raw, platform, topic)

    def check_sensitivity(self, draft: ForumDraft) -> list[str]:
        """Run a sensitivity/spam check on a draft."""
        settings = get_settings()
        prompt = SENSITIVITY_CHECK_PROMPT.format(
            draft_content=draft.draft_content,
            platform=draft.platform,
            restaurant_name=settings.restaurant_name,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = self._llm.chat_completion(messages, temperature=0.2)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return data.get("sensitivity_flags", [])
        except Exception as exc:
            logger.error("check_sensitivity failed: %s", exc)
            return []

    def run(self, **kwargs) -> dict:
        settings = get_settings()
        restaurant_info = {
            "restaurant_name": kwargs.get("restaurant_name", settings.restaurant_name),
            "city": kwargs.get("city", settings.restaurant_city),
            "neighborhood": kwargs.get("neighborhood", settings.restaurant_neighborhood),
            "cuisine": kwargs.get("cuisine", settings.restaurant_cuisine),
        }
        topics = kwargs.get("topics", _DEFAULT_TOPICS)

        drafts: list[ForumDraft] = []
        for platform, topic in topics:
            logger.info("ForumMarketingBot: generating draft for %s / %s", platform, topic)
            draft = self.generate_draft(topic, platform, restaurant_info)
            flags = self.check_sensitivity(draft)
            draft.sensitivity_flags = flags
            draft.status = "pending_review"  # always starts as pending
            drafts.append(draft)

        queue = ForumDraftQueue(drafts=drafts, generated_at=datetime.now(timezone.utc))
        result = queue.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_draft(raw: str, platform: str, topic: str) -> ForumDraft:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            draft = ForumDraft.model_validate(data)
            draft.status = "pending_review"
            return draft
        except Exception as exc:
            logger.error("_parse_draft failed: %s", exc)
            return ForumDraft(platform=platform, topic=topic, draft_content=raw or "")
