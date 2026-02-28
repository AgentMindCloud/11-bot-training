"""Local SEO Optimization Bot (Bot 1)."""
from __future__ import annotations

import json
import logging

from bots.base import BaseBot
from bots.local_seo.models import (
    InternalLinkSuggestion,
    SeoInput,
    SeoOutput,
    TitleTagSuggestion,
)
from common.llm.client import LLMClient
from common.models.base import BotName, KeywordCluster
from infra.config import settings

logger = logging.getLogger(__name__)

KEYWORD_SYSTEM_PROMPT = """
You are an expert local SEO strategist for restaurants.
Given a restaurant's city, neighborhood, and cuisine, generate keyword clusters.
Each cluster has a theme, a list of 5-8 keywords, an intent (informational/transactional/navigational), and a priority 1-5.
Respond ONLY with valid JSON matching this schema:
[
  {
    "theme": "...",
    "keywords": ["...", "..."],
    "intent": "transactional",
    "priority": 1
  }
]
"""

TITLE_TAG_SYSTEM_PROMPT = """
You are an expert local SEO copywriter.
Given restaurant info, generate SEO-optimized title tags, meta descriptions, and H1s for these pages: homepage, menu, about, contact, reservations.
Respond ONLY with valid JSON:
[
  {
    "page": "homepage",
    "title": "...",
    "meta_description": "...",
    "h1": "..."
  }
]
"""

INTERNAL_LINKS_SYSTEM_PROMPT = """
You are an expert in website internal linking strategy.
Given a restaurant website's pages, suggest 5-7 internal link opportunities.
Respond ONLY with valid JSON:
[
  {
    "anchor_text": "...",
    "from_page": "...",
    "to_page": "...",
    "rationale": "..."
  }
]
"""


class LocalSeoBot(BaseBot):
    """Generates keyword clusters, title tags, meta descriptions, and internal link suggestions."""

    name = BotName.LOCAL_SEO

    def __init__(self, seo_input: SeoInput | None = None, llm: LLMClient | None = None) -> None:
        super().__init__()
        self.seo_input = seo_input or SeoInput(
            city=settings.restaurant_city,
            neighborhood=settings.restaurant_neighborhood,
            cuisine=settings.restaurant_cuisine,
            website=settings.restaurant_website,
        )
        self.llm = llm or LLMClient()
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        logger.info("LocalSeoBot: generating SEO assets for %s", self.seo_input.city)
        output = SeoOutput(
            keyword_clusters=self._generate_keywords(),
            title_tags=self._generate_title_tags(),
            internal_links=self._generate_internal_links(),
        )
        self._save_output(output)
        return output.model_dump()

    def _generate_keywords(self) -> list[KeywordCluster]:
        user_prompt = (
            f"City: {self.seo_input.city}\n"
            f"Neighborhood: {self.seo_input.neighborhood}\n"
            f"Cuisine: {self.seo_input.cuisine}\n"
            f"Extra topics: {', '.join(self.seo_input.extra_topics)}"
        )
        raw = self.llm.chat(KEYWORD_SYSTEM_PROMPT, user_prompt, temperature=0.5)
        clusters_data = json.loads(raw)
        return [KeywordCluster(**c) for c in clusters_data]

    def _generate_title_tags(self) -> list[TitleTagSuggestion]:
        user_prompt = (
            f"Restaurant: {settings.restaurant_name}\n"
            f"City: {self.seo_input.city}, {self.seo_input.neighborhood}\n"
            f"Cuisine: {self.seo_input.cuisine}\n"
            f"Website: {self.seo_input.website}"
        )
        raw = self.llm.chat(TITLE_TAG_SYSTEM_PROMPT, user_prompt, temperature=0.4)
        tags_data = json.loads(raw)
        return [TitleTagSuggestion(**t) for t in tags_data]

    def _generate_internal_links(self) -> list[InternalLinkSuggestion]:
        user_prompt = (
            f"Pages: homepage, menu, about, contact, reservations, blog\n"
            f"Website: {self.seo_input.website}\n"
            f"Cuisine: {self.seo_input.cuisine}, City: {self.seo_input.city}"
        )
        raw = self.llm.chat(INTERNAL_LINKS_SYSTEM_PROMPT, user_prompt, temperature=0.4)
        links_data = json.loads(raw)
        return [InternalLinkSuggestion(**lnk) for lnk in links_data]

    def _save_output(self, output: SeoOutput) -> None:
        path = settings.output_dir / "local_seo_output.json"
        path.write_text(output.model_dump_json(indent=2))
        logger.info("LocalSeoBot: saved output to %s", path)
