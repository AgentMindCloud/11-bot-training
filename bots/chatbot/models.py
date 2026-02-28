"""Data models for the Restaurant Chatbot & Marketing Automation Bot."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class UserIntent(str, Enum):
    HOURS = "hours"
    RESERVATION = "reservation"
    MENU = "menu"
    DIETARY = "dietary"
    LOCATION = "location"
    PRICING = "pricing"
    PROMOTIONS = "promotions"
    OTHER = "other"


class UserProfile(BaseModel):
    session_id: str
    name: str = ""
    email: str = ""
    phone: str = ""
    interests: list[str] = Field(default_factory=list)
    opted_in: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketingTrigger(BaseModel):
    trigger_type: str  # e.g., "follow_up", "offer", "reminder"
    user_session_id: str
    message: str
    scheduled_at: datetime | None = None
    webhook_url: str = ""


class ChatbotInput(BaseModel):
    session_id: str
    message: str
    user_profile: UserProfile | None = None
    history: list[ChatMessage] = Field(default_factory=list)


class ChatbotOutput(BaseModel):
    reply: str
    intent_detected: UserIntent = UserIntent.OTHER
    data_captured: dict = Field(default_factory=dict)
    marketing_triggers: list[MarketingTrigger] = Field(default_factory=list)
