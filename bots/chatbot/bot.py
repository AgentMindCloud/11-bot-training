"""Chatbot bot implementation."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from bots.base import BotBase
from bots.chatbot.models import ChatMessage, ChatSession, ChatbotOutput, MarketingTrigger
from bots.chatbot.prompts import INTENT_DETECTION_PROMPT, MARKETING_TRIGGER_PROMPT, SYSTEM_PROMPT
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SAMPLE_CONVERSATION = [
    "Hi! What are your opening hours?",
    "Do you have any vegetarian options?",
    "I'd like to make a reservation for my birthday dinner next Saturday for 4 people.",
    "What's your most popular dish?",
]


class ChatbotBot(BotBase):
    name = "chatbot"
    description = "Restaurant FAQ chatbot with marketing trigger detection"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()
        settings = get_settings()
        self._system_prompt = SYSTEM_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            cuisine=settings.restaurant_cuisine,
            neighborhood=settings.restaurant_neighborhood,
            city=settings.restaurant_city,
            address=settings.restaurant_address or "Contact us for address",
            phone=settings.restaurant_phone or "Contact us for phone",
            hours=settings.restaurant_hours or "Please call for current hours",
        )

    # ------------------------------------------------------------------

    def respond(self, session: ChatSession, user_message: str) -> ChatSession:
        """Add user message, generate assistant response, return updated session."""
        user_msg = ChatMessage(
            role="user",
            content=user_message,
            timestamp=datetime.now(timezone.utc),
        )
        session.messages.append(user_msg)

        # Build message history for LLM
        messages = [{"role": "system", "content": self._system_prompt}]
        for msg in session.messages:
            messages.append({"role": msg.role, "content": msg.content})

        try:
            response_text = self._llm.chat_completion(messages, temperature=0.6, max_tokens=500)
        except Exception as exc:
            logger.error("chatbot respond failed: %s", exc)
            response_text = "I'm sorry, I'm having trouble responding right now. Please call us directly."

        assistant_msg = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now(timezone.utc),
        )
        session.messages.append(assistant_msg)
        return session

    def detect_intent(self, message: str) -> str:
        """Classify the intent of a user message."""
        prompt = INTENT_DETECTION_PROMPT.format(message=message)
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = self._llm.chat_completion(messages, temperature=0.1)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return data.get("intent", "general")
        except Exception as exc:
            logger.error("detect_intent failed: %s", exc)
            return "general"

    def check_marketing_triggers(self, session: ChatSession) -> list[MarketingTrigger]:
        """Determine if any marketing triggers should fire for this session."""
        if len(session.messages) < 2:
            return []

        conversation_text = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in session.messages
        )
        prompt = MARKETING_TRIGGER_PROMPT.format(conversation_text=conversation_text)
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = self._llm.chat_completion(messages, temperature=0.2)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return [MarketingTrigger.model_validate(t) for t in data.get("triggers", [])]
        except Exception as exc:
            logger.error("check_marketing_triggers failed: %s", exc)
            return []

    def run(self, **kwargs) -> dict:
        """Demo mode: run a sample conversation."""
        session = ChatSession(session_id=str(uuid.uuid4()))
        sample_messages = kwargs.get("sample_messages", _SAMPLE_CONVERSATION)

        for user_msg in sample_messages:
            logger.info("ChatbotBot: user says: %s", user_msg)
            session = self.respond(session, user_msg)

        triggers = self.check_marketing_triggers(session)

        output = ChatbotOutput(sessions=[session], marketing_triggers=triggers)
        result = output.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result
