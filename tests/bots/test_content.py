"""Unit tests for ContentBot with mocked LLM."""
from __future__ import annotations

import json

import pytest

from bots.content.bot import ContentBot
from bots.content.models import ContentInput
from common.models.base import BotRunStatus


MOCK_BLOG_POST = json.dumps({
    "title": "5 Reasons to Try Italian Food in Austin",
    "outline": ["Introduction", "Fresh Ingredients", "Authentic Recipes"],
    "body_markdown": "# 5 Reasons to Try Italian Food in Austin\n\nAustin's Italian scene is thriving...",
    "slug": "5-reasons-italian-food-austin",
    "seo_keywords": ["italian food austin", "best pasta austin"],
})

MOCK_FACEBOOK_POST = json.dumps({
    "platform": "facebook",
    "text": "Weekend vibes at My Restaurant! Join us for handmade pasta and great wine.",
    "hashtags": ["#ItalianFood", "#AustinEats"],
    "call_to_action": "Book your table now!",
})

MOCK_TIKTOK_POST = json.dumps({
    "platform": "tiktok",
    "text": "POV: You just found Austin's best kept Italian secret 🍝",
    "hashtags": ["#FoodTok", "#AustinFood", "#ItalianRestaurant"],
    "call_to_action": "Follow for daily specials!",
})

MOCK_FAQ = json.dumps([
    {
        "title": "Do you offer gluten-free pasta?",
        "body": "Yes, we offer gluten-free pasta options on request.",
        "content_type": "faq",
        "keywords": ["gluten free pasta austin"],
    }
])


class TestContentBot:
    def _make_bot(self, mock_llm, platform="all", topics=None):
        content_input = ContentInput(
            topics=topics or ["Italian food Austin"],
            target_platform=platform,
        )
        return ContentBot(content_input=content_input, llm=mock_llm)

    def test_blog_platform_generates_blog_posts(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_BLOG_POST
        bot = self._make_bot(mock_llm, platform="blog")
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert len(result.outputs["blog_posts"]) == 1
        assert result.outputs["blog_posts"][0]["slug"] == "5-reasons-italian-food-austin"

    def test_blog_post_saved_as_markdown(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_BLOG_POST
        bot = self._make_bot(mock_llm, platform="blog")
        bot.execute()

        md_file = tmp_path / "blog" / "5-reasons-italian-food-austin.md"
        assert md_file.exists()

    def test_facebook_platform_generates_social_snippets(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_FACEBOOK_POST
        bot = self._make_bot(mock_llm, platform="facebook")
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        snippets = result.outputs["social_snippets"]
        assert len(snippets) == 1
        assert snippets[0]["platform"] == "facebook"

    def test_all_platform_generates_all_content_types(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        # blog + facebook + tiktok + faq calls
        mock_llm.chat.side_effect = [
            MOCK_BLOG_POST,
            MOCK_FACEBOOK_POST,
            MOCK_TIKTOK_POST,
            MOCK_FAQ,
        ]
        bot = self._make_bot(mock_llm, platform="all")
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert len(result.outputs["blog_posts"]) >= 1
        assert len(result.outputs["social_snippets"]) >= 1
        assert len(result.outputs["faq_items"]) >= 1

    def test_llm_failure_returns_failed_status(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = Exception("LLM unavailable")
        bot = self._make_bot(mock_llm, platform="blog")
        result = bot.execute()

        assert result.status == BotRunStatus.FAILED
