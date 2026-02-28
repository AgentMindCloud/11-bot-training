"""Content Creation bot implementation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bots.base import BotBase
from bots.content_creation.models import BlogPost, ContentOutput, SocialSnippet
from bots.content_creation.prompts import BLOG_POST_PROMPT, SOCIAL_SNIPPET_PROMPT
from common.config import get_settings
from common.llm.client import LLMClient

logger = logging.getLogger(__name__)

_DEFAULT_PLATFORMS = ["facebook", "tiktok", "instagram"]


class ContentCreationBot(BotBase):
    name = "content_creation"
    description = "Creates blog posts and social media snippets based on SEO keyword clusters"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    # ------------------------------------------------------------------

    def load_seo_output(self):
        """Load the latest output from the local_seo bot."""
        try:
            from bots.local_seo.models import LocalSeoOutput

            data = self.load_input("local_seo/latest.json")
            if data:
                return LocalSeoOutput.model_validate(data)
        except Exception as exc:
            logger.warning("Could not load local_seo output: %s", exc)
        return None

    def create_blog_post(self, keyword_cluster: dict, restaurant_info: dict) -> BlogPost:
        """Generate a full blog post for a given keyword cluster."""
        prompt = BLOG_POST_PROMPT.format(
            restaurant_name=restaurant_info.get("restaurant_name", "Our Restaurant"),
            city=restaurant_info.get("city", ""),
            neighborhood=restaurant_info.get("neighborhood", ""),
            cuisine=restaurant_info.get("cuisine", ""),
            keyword_cluster_json=json.dumps(keyword_cluster, indent=2),
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            result = self._llm.structured_completion(messages, BlogPost)
            return result
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_blog_post(raw)

    def create_social_snippets(
        self,
        blog_post: BlogPost,
        platforms: list[str] | None = None,
    ) -> list[SocialSnippet]:
        """Generate platform-specific social snippets for a blog post."""
        platforms = platforms or _DEFAULT_PLATFORMS
        settings = get_settings()
        prompt = SOCIAL_SNIPPET_PROMPT.format(
            blog_title=blog_post.title,
            meta_description=blog_post.meta_description,
            restaurant_name=settings.restaurant_name,
            city=settings.restaurant_city,
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            from pydantic import BaseModel as PydanticBase

            class _SnippetResponse(PydanticBase):
                social_snippets: list[SocialSnippet]

            result = self._llm.structured_completion(messages, _SnippetResponse)
            return result.social_snippets
        except Exception as exc:
            logger.debug("structured_completion failed (%s), falling back", exc)
            raw = self._llm.chat_completion(messages)
            return self._parse_social_snippets(raw)

    def run(self, **kwargs) -> dict:
        settings = get_settings()
        restaurant_info = {
            "restaurant_name": kwargs.get("restaurant_name", settings.restaurant_name),
            "city": kwargs.get("city", settings.restaurant_city),
            "neighborhood": kwargs.get("neighborhood", settings.restaurant_neighborhood),
            "cuisine": kwargs.get("cuisine", settings.restaurant_cuisine),
        }

        # Try to load keyword clusters from local_seo output
        seo_output = self.load_seo_output()
        if seo_output and seo_output.keyword_clusters:
            clusters = [kc.model_dump() for kc in seo_output.keyword_clusters[:3]]
        else:
            clusters = kwargs.get(
                "keyword_clusters",
                [{"keyword": restaurant_info["cuisine"] + " restaurant " + restaurant_info["city"]}],
            )

        blog_posts: list[BlogPost] = []
        social_snippets: list[SocialSnippet] = []

        for cluster in clusters:
            logger.info("ContentCreationBot: creating blog post for keyword: %s", cluster.get("keyword"))
            post = self.create_blog_post(cluster, restaurant_info)
            blog_posts.append(post)
            snippets = self.create_social_snippets(post)
            social_snippets.extend(snippets)

        output = ContentOutput(
            blog_posts=blog_posts,
            social_snippets=social_snippets,
            generated_at=datetime.now(timezone.utc),
        )
        result = output.model_dump(mode="json")
        self.save_output(result, "latest.json")
        return result

    # ------------------------------------------------------------------
    # Fallback parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_blog_post(raw: str) -> BlogPost:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return BlogPost.model_validate(data)
        except Exception as exc:
            logger.error("_parse_blog_post failed: %s", exc)
            return BlogPost(title="Untitled", slug="untitled")

    @staticmethod
    def _parse_social_snippets(raw: str) -> list[SocialSnippet]:
        try:
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            items = data.get("social_snippets", data) if isinstance(data, dict) else data
            return [SocialSnippet.model_validate(item) for item in items]
        except Exception as exc:
            logger.error("_parse_social_snippets failed: %s", exc)
            return []
