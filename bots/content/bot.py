"""Content Creation & Distribution Bot (Bot 2)."""
from __future__ import annotations

import json
import logging

from bots.base import BaseBot
from bots.content.models import BlogPost, ContentInput, ContentOutput, SocialSnippet
from common.llm.client import LLMClient
from common.models.base import BotName, ContentPiece
from infra.config import settings

logger = logging.getLogger(__name__)

BLOG_SYSTEM_PROMPT = """
You are an expert content writer for a local restaurant blog.
Write engaging, SEO-optimized blog content that attracts local customers.
Respond ONLY with valid JSON:
{
  "title": "...",
  "outline": ["Section 1", "Section 2"],
  "body_markdown": "# Title\\n\\n...",
  "slug": "url-friendly-slug",
  "seo_keywords": ["keyword1", "keyword2"]
}
"""

FACEBOOK_SYSTEM_PROMPT = """
You are a social media manager for a local restaurant.
Write engaging Facebook posts that feel authentic, not salesy.
Respond ONLY with valid JSON:
{
  "platform": "facebook",
  "text": "...",
  "hashtags": ["#food", "#local"],
  "call_to_action": "Reserve your table today!"
}
"""

TIKTOK_SYSTEM_PROMPT = """
You are a TikTok content strategist for a local restaurant.
Write punchy TikTok hooks and captions (under 150 chars for hook).
Respond ONLY with valid JSON:
{
  "platform": "tiktok",
  "text": "Hook + caption...",
  "hashtags": ["#foodtok", "#restaurant"],
  "call_to_action": "Follow for daily specials!"
}
"""

FAQ_SYSTEM_PROMPT = """
You are writing FAQ content for a restaurant website.
Generate 5 FAQ items for the given topic.
Respond ONLY with valid JSON array:
[
  {
    "title": "Question?",
    "body": "Answer...",
    "content_type": "faq",
    "keywords": ["keyword1"]
  }
]
"""


class ContentBot(BaseBot):
    """Generates blog posts, social snippets, and FAQ content."""

    name = BotName.CONTENT

    def __init__(self, content_input: ContentInput | None = None, llm: LLMClient | None = None) -> None:
        super().__init__()
        self.content_input = content_input or ContentInput()
        self.llm = llm or LLMClient()
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        logger.info("ContentBot: generating content")
        output = ContentOutput()

        topics = self.content_input.topics or self._topics_from_clusters()

        platform = self.content_input.target_platform
        if platform in ("blog", "all"):
            output.blog_posts = [self._generate_blog_post(t) for t in topics[:3]]
        if platform in ("facebook", "all"):
            output.social_snippets += [self._generate_facebook_post(t) for t in topics[:3]]
        if platform in ("tiktok", "all"):
            output.social_snippets += [self._generate_tiktok_hook(t) for t in topics[:3]]
        if platform == "all":
            output.faq_items = self._generate_faq(topics[0] if topics else "restaurant")

        self._save_output(output)
        return output.model_dump()

    def _topics_from_clusters(self) -> list[str]:
        return [
            cluster.keywords[0]
            for cluster in self.content_input.keyword_clusters
            if cluster.keywords
        ] or [f"{settings.restaurant_cuisine} restaurant in {settings.restaurant_city}"]

    def _generate_blog_post(self, topic: str) -> BlogPost:
        user_prompt = (
            f"Topic: {topic}\n"
            f"Restaurant: {settings.restaurant_name} ({settings.restaurant_cuisine} in {settings.restaurant_city})"
        )
        raw = self.llm.chat(BLOG_SYSTEM_PROMPT, user_prompt, temperature=0.7)
        return BlogPost(**json.loads(raw))

    def _generate_facebook_post(self, topic: str) -> SocialSnippet:
        user_prompt = (
            f"Topic: {topic}\n"
            f"Restaurant: {settings.restaurant_name}, {settings.restaurant_city}"
        )
        raw = self.llm.chat(FACEBOOK_SYSTEM_PROMPT, user_prompt, temperature=0.8)
        return SocialSnippet(**json.loads(raw))

    def _generate_tiktok_hook(self, topic: str) -> SocialSnippet:
        user_prompt = (
            f"Topic: {topic}\n"
            f"Restaurant: {settings.restaurant_name}, {settings.restaurant_cuisine}"
        )
        raw = self.llm.chat(TIKTOK_SYSTEM_PROMPT, user_prompt, temperature=0.9)
        return SocialSnippet(**json.loads(raw))

    def _generate_faq(self, topic: str) -> list[ContentPiece]:
        user_prompt = (
            f"Topic: {topic}\n"
            f"Restaurant: {settings.restaurant_name}, {settings.restaurant_cuisine}, {settings.restaurant_city}"
        )
        raw = self.llm.chat(FAQ_SYSTEM_PROMPT, user_prompt, temperature=0.6)
        items_data = json.loads(raw)
        return [ContentPiece(**item) for item in items_data]

    def _save_output(self, output: ContentOutput) -> None:
        path = settings.output_dir / "content_output.json"
        path.write_text(output.model_dump_json(indent=2))
        logger.info("ContentBot: saved output to %s", path)

        # Also save blog posts as markdown files
        blog_dir = settings.output_dir / "blog"
        blog_dir.mkdir(parents=True, exist_ok=True)
        for post in output.blog_posts:
            md_path = blog_dir / f"{post.slug}.md"
            md_path.write_text(post.body_markdown)
