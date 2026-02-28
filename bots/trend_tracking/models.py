"""Data models for the Industry/Trend Tracking Bot."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class TrendSource(BaseModel):
    url: str
    title: str = ""
    snippet: str = ""
    published_at: datetime | None = None


class TrendItem(BaseModel):
    topic: str
    summary: str
    actionable_ideas: list[str] = Field(default_factory=list)
    sources: list[TrendSource] = Field(default_factory=list)
    relevance_score: int = Field(default=3, ge=1, le=5)


class TrendReport(BaseModel):
    week_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trends: list[TrendItem] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)
    executive_summary: str = ""


class TrendInput(BaseModel):
    seed_urls: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    location: str = ""
