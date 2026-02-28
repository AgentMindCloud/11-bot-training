"""Pydantic models for the Chatbot bot."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatSession(BaseModel):
    session_id: str
    messages: list[ChatMessage] = Field(default_factory=list)
    user_email: str | None = None
    user_tags: list[str] = Field(default_factory=list)
    opted_in: bool = False


class MarketingTrigger(BaseModel):
    trigger_type: str
    user_data: dict = Field(default_factory=dict)
    message_template: str
    scheduled_at: datetime | None = None


class ChatbotOutput(BaseModel):
    sessions: list[ChatSession] = Field(default_factory=list)
    marketing_triggers: list[MarketingTrigger] = Field(default_factory=list)
