"""Data models for the Competitor Website Analysis Bot."""
from __future__ import annotations

from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    name: str
    price: str = ""
    description: str = ""
    category: str = ""


class CompetitorProfile(BaseModel):
    url: str
    name: str = ""
    cuisines: list[str] = Field(default_factory=list)
    price_range: str = ""
    menu_items: list[MenuItem] = Field(default_factory=list)
    delivery_platforms: list[str] = Field(default_factory=list)
    promotions: list[str] = Field(default_factory=list)
    usps: list[str] = Field(default_factory=list)
    summary: str = ""


class ComparisonAxis(BaseModel):
    axis: str
    our_value: str
    competitor_value: str
    advantage: str  # "ours", "theirs", "neutral"
    notes: str = ""


class CompetitorReport(BaseModel):
    competitor: CompetitorProfile
    comparisons: list[ComparisonAxis] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)


class CompetitorInput(BaseModel):
    competitor_urls: list[str] = Field(default_factory=list)
    our_profile: dict = Field(default_factory=dict)
