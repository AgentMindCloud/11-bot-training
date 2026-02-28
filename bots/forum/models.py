"""Data models for the Forum & Community Marketing Bot."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class PlatformType(str, Enum):
    REDDIT = "reddit"
    FACEBOOK_GROUP = "facebook_group"
    LOCAL_FOOD_FORUM = "local_food_forum"
    YELP_TALK = "yelp_talk"
    NEXTDOOR = "nextdoor"
    OTHER = "other"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class ForumDraft(BaseModel):
    id: str
    platform: PlatformType
    topic: str
    draft_text: str
    sensitive_flags: list[str] = Field(default_factory=list)
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: datetime | None = None
    reviewer_notes: str = ""


class ForumInput(BaseModel):
    topic: str
    platform: PlatformType = PlatformType.OTHER
    context: str = ""
    num_drafts: int = 3


class ForumOutput(BaseModel):
    drafts: list[ForumDraft] = Field(default_factory=list)
    review_queue_path: str = ""
