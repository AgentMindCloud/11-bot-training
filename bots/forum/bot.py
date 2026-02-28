"""Forum & Community Marketing Bot (Bot 3) — human-in-the-loop drafts only."""
from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from bots.base import BaseBot
from bots.forum.models import ForumDraft, ForumInput, ForumOutput, PlatformType, ReviewStatus
from common.llm.client import LLMClient
from common.models.base import BotName
from infra.config import settings

logger = logging.getLogger(__name__)

FORUM_SYSTEM_PROMPT = """
You are a community manager for a local restaurant. Your task is to draft natural, helpful, non-spammy responses for online forums and community groups.

Rules:
- Sound like a real person, not a marketer
- Focus on being helpful first
- Mention the restaurant ONLY when it's genuinely relevant
- Flag any content that could be perceived as spam with [SENSITIVE: reason]

Respond ONLY with valid JSON:
{
  "draft_text": "...",
  "sensitive_flags": ["reason1", "reason2"]
}
"""

SENSITIVE_KEYWORDS = [
    "buy now", "limited offer", "click here", "dm me", "check out my",
    "follow us", "visit our website", "discount", "promo", "deal",
]


class ForumBot(BaseBot):
    """Generates draft posts/replies for forums with human review queue."""

    name = BotName.FORUM

    def __init__(self, forum_input: ForumInput | None = None, llm: LLMClient | None = None) -> None:
        super().__init__()
        self.forum_input = forum_input or ForumInput(topic="local dining recommendations")
        self.llm = llm or LLMClient()
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        logger.info(
            "ForumBot: generating %d drafts for topic: %s",
            self.forum_input.num_drafts,
            self.forum_input.topic,
        )
        drafts = [self._generate_draft(i) for i in range(self.forum_input.num_drafts)]
        output = ForumOutput(drafts=drafts)
        queue_path = self._save_review_queue(output)
        output.review_queue_path = str(queue_path)
        return output.model_dump()

    def _generate_draft(self, index: int) -> ForumDraft:
        user_prompt = (
            f"Topic: {self.forum_input.topic}\n"
            f"Platform: {self.forum_input.platform.value}\n"
            f"Context: {self.forum_input.context}\n"
            f"Restaurant: {settings.restaurant_name}, {settings.restaurant_cuisine} in {settings.restaurant_city}\n"
            f"Draft variant: {index + 1}"
        )
        raw = self.llm.chat(FORUM_SYSTEM_PROMPT, user_prompt, temperature=0.8)
        data = json.loads(raw)
        draft_text = data.get("draft_text", "")
        sensitive_flags = data.get("sensitive_flags", [])

        # Extra keyword check
        lower_text = draft_text.lower()
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in lower_text and keyword not in sensitive_flags:
                sensitive_flags.append(f"Contains potentially spammy phrase: '{keyword}'")

        return ForumDraft(
            id=str(uuid.uuid4()),
            platform=self.forum_input.platform,
            topic=self.forum_input.topic,
            draft_text=draft_text,
            sensitive_flags=sensitive_flags,
            status=ReviewStatus.PENDING,
        )

    def _save_review_queue(self, output: ForumOutput) -> Path:
        path = settings.output_dir / "forum_review_queue.json"
        drafts_json = [d.model_dump(mode="json") for d in output.drafts]
        path.write_text(json.dumps(drafts_json, indent=2, default=str))
        logger.info(
            "ForumBot: saved %d drafts to review queue at %s",
            len(output.drafts),
            path,
        )
        return path
