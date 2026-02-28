"""Local SEO bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BotBase
from bots.local_seo.models import (
    InternalLinkSuggestion,
    KeywordCluster,
    LocalSeoOutput,
    SeoMeta,
)
from bots.local_seo.prompts import (
    INTERNAL_LINKS_PROMPT,
    KEYWORD_RESEARCH_PROMPT,
    SEO_META_PROMPT,
)
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)

_DEFAULT_PAGES = [
    "Homepage",
    "Menu",
    "About Us",
    "Reservations",
    "Contact",
    "Blog",
]


class LocalSeoBot(BotBase):
    name = "local_seo"
    description = "Generates keyword clusters and SEO metadata for a local restaurant"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    # ------------------------------------------------------------------
    # Core methods
    # ------------------------------------------------------------------

    def generate_keywords(
        self,
        restaurant_name: str,
        city: str,
        neighborhood: str,
        cuisine: str,
    ) -> list[KeywordCluster]:
        """Ask the LLM to generate keyword clusters."""
        prompt = KEYWORD_RESEARCH_PROMPT.format(
            restaurant_name=restaurant_name,
            city=city,
            neighborhood=neighborhood,
            cuisine=cuisine,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            from pydantic import BaseModel as PydanticBase

            class _KwResponse(PydanticBase):
                keyword_clusters: list[KeywordCluster]

            result = self._llm.structured_completion(messages, _KwResponse)
            return result.keyword_clusters
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back to chat", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_keyword_clusters(raw)

    def generate_seo_metas(
        self,
        keyword_clusters: list[KeywordCluster],
        pages: list[str] | None = None,
    ) -> list[SeoMeta]:
        """Generate title tags, meta descriptions, and H1s for each page."""
        pages = pages or _DEFAULT_PAGES
        settings = get_settings()
        prompt = SEO_META_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            city=settings.restaurant_city,
            neighborhood=settings.restaurant_neighborhood,
            cuisine=settings.restaurant_cuisine,
            keyword_clusters_json=json.dumps(
                [kc.model_dump() for kc in keyword_clusters], indent=2
            ),
            pages_list="\n".join(f"- {p}" for p in pages),
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            from pydantic import BaseModel as PydanticBase

            class _MetaResponse(PydanticBase):
                seo_metas: list[SeoMeta]

            result = self._llm.structured_completion(messages, _MetaResponse)
            return result.seo_metas
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_seo_metas(raw)

    def generate_internal_links(
        self,
        pages: list[str] | None = None,
        content_map: dict[str, str] | None = None,
    ) -> list[InternalLinkSuggestion]:
        """Suggest internal linking opportunities."""
        pages = pages or _DEFAULT_PAGES
        content_map = content_map or {p: f"{p} page content" for p in pages}
        settings = get_settings()
        prompt = INTERNAL_LINKS_PROMPT.format(
            restaurant_name=settings.restaurant_name,
            cuisine=settings.restaurant_cuisine,
            city=settings.restaurant_city,
            content_map_json=json.dumps(content_map, indent=2),
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            from pydantic import BaseModel as PydanticBase

            class _LinkResponse(PydanticBase):
                internal_links: list[InternalLinkSuggestion]

            result = self._llm.structured_completion(messages, _LinkResponse)
            return result.internal_links
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_internal_links(raw)

    def run(self, **kwargs) -> dict:
        settings = get_settings()
        restaurant_name = kwargs.get("restaurant_name", settings.restaurant_name)
        city = kwargs.get("city", settings.restaurant_city)
        neighborhood = kwargs.get("neighborhood", settings.restaurant_neighborhood)
        cuisine = kwargs.get("cuisine", settings.restaurant_cuisine)
        pages = kwargs.get("pages", _DEFAULT_PAGES)

        logger.info("LocalSeoBot: generating keywords for %s", restaurant_name)
        keyword_clusters = self.generate_keywords(restaurant_name, city, neighborhood, cuisine)

        logger.info("LocalSeoBot: generating SEO metas")
        seo_metas = self.generate_seo_metas(keyword_clusters, pages)

        logger.info("LocalSeoBot: generating internal links")
        internal_links = self.generate_internal_links(pages)

        output = LocalSeoOutput(
            restaurant_name=restaurant_name,
            city=city,
            neighborhood=neighborhood,
            cuisine=cuisine,
            keyword_clusters=keyword_clusters,
            seo_metas=seo_metas,
            internal_links=internal_links,
            generated_at=datetime.now(timezone.utc),
        )
        result = output.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_keyword_clusters(raw: str) -> list[KeywordCluster]:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("keyword_clusters", data) if isinstance(data, dict) else data
            return [KeywordCluster.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("_parse_keyword_clusters failed: %s", exc)
            return []

    @staticmethod
    def _parse_seo_metas(raw: str) -> list[SeoMeta]:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("seo_metas", data) if isinstance(data, dict) else data
            return [SeoMeta.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("_parse_seo_metas failed: %s", exc)
            return []

    @staticmethod
    def _parse_internal_links(raw: str) -> list[InternalLinkSuggestion]:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("internal_links", data) if isinstance(data, dict) else data
            return [InternalLinkSuggestion.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("_parse_internal_links failed: %s", exc)
            return []
