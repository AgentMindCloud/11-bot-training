"""Pydantic models for the Forum Marketing bot."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ForumDraft(BaseModel):
    platform: str
    topic: str
    draft_content: str
    sensitivity_flags: list[str] = Field(default_factory=list)
    status: Literal["pending_review", "approved", "posted", "rejected"] = "pending_review"


class ForumDraftQueue(BaseModel):
    drafts: list[ForumDraft] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
