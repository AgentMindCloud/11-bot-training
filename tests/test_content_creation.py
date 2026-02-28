"""Tests for the Content Creation bot."""
from __future__ import annotations

import json

import pytest

from bots.content_creation.bot import ContentCreationBot
from bots.content_creation.models import BlogPost, SocialSnippet


_BLOG_RESPONSE = json.dumps({
    "title": "5 Reasons Why East Village Has NYC's Best Italian Food",
    "slug": "east-village-best-italian-food-nyc",
    "outline": ["Introduction", "Fresh Ingredients", "Authentic Recipes", "Conclusion"],
    "body_markdown": "## Introduction\n\nNew York City is famous for its food scene...\n\n## Fresh Ingredients\n\nOur kitchen sources fresh ingredients daily...",
    "meta_description": "Discover why East Village is home to NYC's best Italian restaurants. Fresh pasta, authentic recipes, and warm hospitality await.",
    "target_keywords": ["Italian restaurant East Village", "NYC Italian food"],
    "word_count": 42,
})

_SNIPPETS_RESPONSE = json.dumps({
    "social_snippets": [
        {
            "platform": "facebook",
            "content": "Craving authentic Italian? We have the perfect table waiting for you in East Village! 🍝",
            "hashtags": ["ItalianFood", "NYCRestaurants", "EastVillage"],
            "character_count": 85,
        },
        {
            "platform": "instagram",
            "content": "Fresh pasta, handcrafted daily. Come taste the difference 🇮🇹✨",
            "hashtags": ["PastaLover", "ItalianNYC", "EastVillage"],
            "character_count": 63,
        },
        {
            "platform": "tiktok",
            "content": "POV: You found NYC's hidden Italian gem 🍕🔥 Come visit us!",
            "hashtags": ["NYCFood", "ItalianFood", "FoodTok"],
            "character_count": 60,
        },
    ]
})


class TestContentCreationBot:
    def test_create_blog_post_returns_blog_post(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _BLOG_RESPONSE
        bot = ContentCreationBot(llm=mock_llm_client)
        cluster = {"keyword": "Italian restaurant East Village", "variations": [], "search_intent": "local"}
        post = bot.create_blog_post(cluster, {"restaurant_name": "Test Trattoria", "city": "New York", "neighborhood": "East Village", "cuisine": "Italian"})
        assert isinstance(post, BlogPost)
        assert post.title == "5 Reasons Why East Village Has NYC's Best Italian Food"
        assert post.slug == "east-village-best-italian-food-nyc"
        assert len(post.outline) == 4

    def test_create_blog_post_has_required_fields(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _BLOG_RESPONSE
        bot = ContentCreationBot(llm=mock_llm_client)
        post = bot.create_blog_post({}, {"restaurant_name": "R", "city": "C", "neighborhood": "N", "cuisine": "Italian"})
        assert post.title
        assert post.slug
        assert post.body_markdown

    def test_create_social_snippets_returns_all_platforms(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _SNIPPETS_RESPONSE
        bot = ContentCreationBot(llm=mock_llm_client)
        post = BlogPost(
            title="Test Post",
            slug="test-post",
            meta_description="A test post",
            body_markdown="Content",
            word_count=1,
        )
        snippets = bot.create_social_snippets(post)
        assert len(snippets) == 3
        platforms = {s.platform for s in snippets}
        assert platforms == {"facebook", "instagram", "tiktok"}

    def test_create_social_snippets_are_social_snippet_type(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _SNIPPETS_RESPONSE
        bot = ContentCreationBot(llm=mock_llm_client)
        post = BlogPost(title="T", slug="t", body_markdown="B", word_count=1)
        snippets = bot.create_social_snippets(post)
        assert all(isinstance(s, SocialSnippet) for s in snippets)
