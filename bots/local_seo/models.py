"""Data models for the Local SEO Optimization Bot."""
from __future__ import annotations

from pydantic import BaseModel, Field

from common.models.base import KeywordCluster


class SeoInput(BaseModel):
    city: str
    neighborhood: str
    cuisine: str
    website: str
    extra_topics: list[str] = Field(default_factory=list)


class TitleTagSuggestion(BaseModel):
    page: str  # e.g., "homepage", "menu", "about"
    title: str
    meta_description: str
    h1: str


class InternalLinkSuggestion(BaseModel):
    anchor_text: str
    from_page: str
    to_page: str
    rationale: str


class SeoOutput(BaseModel):
    keyword_clusters: list[KeywordCluster] = Field(default_factory=list)
    title_tags: list[TitleTagSuggestion] = Field(default_factory=list)
    internal_links: list[InternalLinkSuggestion] = Field(default_factory=list)
