"""Pydantic models for the Trend Tracking bot."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TrendItem(BaseModel):
    topic: str
    source: str
    summary: str
    relevance_score: float = 0.0
    actionable_ideas: list[str] = Field(default_factory=list)


class WeeklyTrendReport(BaseModel):
    week_of: str
    trends: list[TrendItem] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
