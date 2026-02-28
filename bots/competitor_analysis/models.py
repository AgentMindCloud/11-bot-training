"""Pydantic models for the Competitor Analysis bot."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None
    category: str | None = None


class CompetitorProfile(BaseModel):
    name: str
    url: str
    cuisine: str | None = None
    price_range: str | None = None
    menu_items: list[MenuItem] = Field(default_factory=list)
    usps: list[str] = Field(default_factory=list)
    delivery_platforms: list[str] = Field(default_factory=list)
    promotions: list[str] = Field(default_factory=list)


class CompetitorComparison(BaseModel):
    our_restaurant: str
    competitor: CompetitorProfile
    comparison_axes: dict[str, str] = Field(default_factory=dict)
    summary: str = ""


class CompetitorAnalysisOutput(BaseModel):
    competitors: list[CompetitorComparison] = Field(default_factory=list)
    report_markdown: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
