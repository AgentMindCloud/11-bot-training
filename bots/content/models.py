"""Data models for the Content Creation & Distribution Bot."""
from __future__ import annotations

from pydantic import BaseModel, Field

from common.models.base import ContentPiece, KeywordCluster


class ContentInput(BaseModel):
    keyword_clusters: list[KeywordCluster] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    target_platform: str = "all"  # "blog", "facebook", "tiktok", "all"


class BlogPost(BaseModel):
    title: str
    outline: list[str]
    body_markdown: str
    slug: str
    seo_keywords: list[str] = Field(default_factory=list)


class SocialSnippet(BaseModel):
    platform: str  # "facebook" or "tiktok"
    text: str
    hashtags: list[str] = Field(default_factory=list)
    call_to_action: str = ""


class ContentOutput(BaseModel):
    blog_posts: list[BlogPost] = Field(default_factory=list)
    social_snippets: list[SocialSnippet] = Field(default_factory=list)
    faq_items: list[ContentPiece] = Field(default_factory=list)
