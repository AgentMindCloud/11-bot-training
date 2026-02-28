"""Pydantic models for the Content Creation bot."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class BlogPost(BaseModel):
    title: str
    slug: str
    outline: list[str] = Field(default_factory=list)
    body_markdown: str = ""
    meta_description: str = ""
    target_keywords: list[str] = Field(default_factory=list)
    word_count: int = 0

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        if not self.word_count and self.body_markdown:
            self.word_count = len(self.body_markdown.split())


class SocialSnippet(BaseModel):
    platform: Literal["facebook", "tiktok", "instagram"]
    content: str
    hashtags: list[str] = Field(default_factory=list)
    character_count: int = 0

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        if not self.character_count:
            self.character_count = len(self.content)


class ContentOutput(BaseModel):
    blog_posts: list[BlogPost] = Field(default_factory=list)
    social_snippets: list[SocialSnippet] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
