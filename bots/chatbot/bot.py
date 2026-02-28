"""Restaurant Chatbot & Marketing Automation Bot (Bot 7)."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from bots.base import BaseBot
from bots.chatbot.models import (
    ChatbotInput,
    ChatbotOutput,
    MarketingTrigger,
    UserIntent,
)
from common.llm.client import LLMClient
from common.models.base import BotName
from infra.config import settings

logger = logging.getLogger(__name__)

CHATBOT_SYSTEM_PROMPT = """
You are a friendly, helpful assistant for {restaurant_name}, a {cuisine} restaurant in {city}.

Key information:
- Hours: {hours}
- Phone: {phone}
- Website: {website}

Guidelines:
- Be warm and welcoming
- Answer questions accurately based on the info provided
- If you don't know something, offer to connect them with the restaurant directly
- Gently capture user info (name, email) only with explicit opt-in
- Detect intent and include it in your response

Respond ONLY with valid JSON:
{{
  "reply": "Your friendly response here",
  "intent": "hours|reservation|menu|dietary|location|pricing|promotions|other",
  "data_captured": {{"name": "...", "email": "...", "opted_in": false}},
  "suggest_marketing": false,
  "marketing_trigger_type": "none"
}}
"""


class ChatbotBot(BaseBot):
    """Multi-turn restaurant chatbot with marketing automation triggers."""

    name = BotName.CHATBOT

    def __init__(self, chatbot_input: ChatbotInput | None = None, llm: LLMClient | None = None) -> None:
        super().__init__()
        self.chatbot_input = chatbot_input or ChatbotInput(
            session_id=str(uuid.uuid4()),
            message="Hello! What are your hours?",
        )
        self.llm = llm or LLMClient()

    def run(self) -> dict:
        response = self._generate_response()
        output = ChatbotOutput(
            reply=response.get("reply", ""),
            intent_detected=UserIntent(response.get("intent", "other")),
            data_captured=response.get("data_captured", {}),
        )

        if response.get("suggest_marketing") and response.get("data_captured", {}).get("opted_in"):
            trigger = MarketingTrigger(
                trigger_type=response.get("marketing_trigger_type", "follow_up"),
                user_session_id=self.chatbot_input.session_id,
                message=f"Thanks for your interest in {settings.restaurant_name}! Here's a special offer...",
                scheduled_at=datetime.now(timezone.utc),
            )
            output.marketing_triggers.append(trigger)

        return output.model_dump(mode="json")

    def _generate_response(self) -> dict:
        system_prompt = CHATBOT_SYSTEM_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            cuisine=settings.restaurant_cuisine,
            city=settings.restaurant_city,
            hours=settings.restaurant_hours,
            phone=settings.restaurant_phone,
            website=settings.restaurant_website,
        )

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for msg in self.chatbot_input.history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": self.chatbot_input.message})

        raw = self.llm.chat_with_history(messages, temperature=0.7)
        return json.loads(raw)
