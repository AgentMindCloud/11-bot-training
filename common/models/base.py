"""Shared base data models used across all bots."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BotName(str, Enum):
    LOCAL_SEO = "local_seo"
    CONTENT = "content"
    FORUM = "forum"
    LINK_BUILDING = "link_building"
    COMPETITOR = "competitor"
    TREND_TRACKING = "trend_tracking"
    CHATBOT = "chatbot"
    ORCHESTRATOR = "orchestrator"
    REVIEW_MONITOR = "review_monitor"
    RESERVATION_FUNNEL = "reservation_funnel"
    LOYALTY = "loyalty"


class BotRunStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class BotRunResult(BaseModel):
    bot: BotName
    status: BotRunStatus
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    outputs: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class RestaurantProfile(BaseModel):
    name: str
    city: str
    neighborhood: str
    cuisine: str
    website: str
    phone: str = ""
    hours: str = ""


class KeywordCluster(BaseModel):
    theme: str
    keywords: list[str]
    intent: str  # e.g. "informational", "transactional", "navigational"
    priority: int = Field(default=1, ge=1, le=5)


class ContentPiece(BaseModel):
    title: str
    body: str
    content_type: str  # "blog", "faq", "facebook_post", "tiktok_hook"
    keywords: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
