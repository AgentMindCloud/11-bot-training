"""Pydantic models for the Local SEO bot."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class KeywordCluster(BaseModel):
    keyword: str
    variations: list[str] = Field(default_factory=list)
    search_intent: str = ""
    monthly_volume_estimate: int = 0


class SeoMeta(BaseModel):
    page_type: str
    title_tag: str
    meta_description: str
    h1: str
    target_keywords: list[str] = Field(default_factory=list)


class InternalLinkSuggestion(BaseModel):
    source_page: str
    target_page: str
    anchor_text: str
    reason: str


class LocalSeoOutput(BaseModel):
    restaurant_name: str
    city: str
    neighborhood: str
    cuisine: str
    keyword_clusters: list[KeywordCluster] = Field(default_factory=list)
    seo_metas: list[SeoMeta] = Field(default_factory=list)
    internal_links: list[InternalLinkSuggestion] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
