"""Unit tests for LocalSeoBot with mocked LLM."""
from __future__ import annotations

import json

import pytest

from bots.local_seo.bot import LocalSeoBot
from bots.local_seo.models import SeoInput
from common.models.base import BotRunStatus


MOCK_KEYWORDS = json.dumps([
    {
        "theme": "Italian dining Austin",
        "keywords": ["italian restaurant austin", "pasta austin tx", "best italian food austin"],
        "intent": "transactional",
        "priority": 1,
    }
])

MOCK_TITLE_TAGS = json.dumps([
    {
        "page": "homepage",
        "title": "My Restaurant | Best Italian in Austin",
        "meta_description": "Authentic Italian cuisine in East Austin. Fresh pasta, wood-fired pizza.",
        "h1": "Authentic Italian Cuisine in Austin",
    }
])

MOCK_INTERNAL_LINKS = json.dumps([
    {
        "anchor_text": "view our menu",
        "from_page": "homepage",
        "to_page": "menu",
        "rationale": "Drives traffic to high-conversion menu page",
    }
])


class TestLocalSeoBot:
    def _make_bot(self, mock_llm):
        seo_input = SeoInput(
            city="Austin",
            neighborhood="East Austin",
            cuisine="Italian",
            website="https://myrestaurant.com",
        )
        return LocalSeoBot(seo_input=seo_input, llm=mock_llm)

    def test_run_returns_keyword_clusters(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [
            MOCK_KEYWORDS,
            MOCK_TITLE_TAGS,
            MOCK_INTERNAL_LINKS,
        ]
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert len(result.outputs["keyword_clusters"]) == 1
        assert result.outputs["keyword_clusters"][0]["theme"] == "Italian dining Austin"

    def test_run_returns_title_tags(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [
            MOCK_KEYWORDS,
            MOCK_TITLE_TAGS,
            MOCK_INTERNAL_LINKS,
        ]
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        assert len(result.outputs["title_tags"]) == 1
        assert result.outputs["title_tags"][0]["page"] == "homepage"

    def test_run_returns_internal_links(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [
            MOCK_KEYWORDS,
            MOCK_TITLE_TAGS,
            MOCK_INTERNAL_LINKS,
        ]
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        assert len(result.outputs["internal_links"]) == 1
        assert result.outputs["internal_links"][0]["anchor_text"] == "view our menu"

    def test_run_saves_output_file(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [
            MOCK_KEYWORDS,
            MOCK_TITLE_TAGS,
            MOCK_INTERNAL_LINKS,
        ]
        bot = self._make_bot(mock_llm)
        bot.execute()

        output_file = tmp_path / "local_seo_output.json"
        assert output_file.exists()

    def test_llm_failure_returns_failed_status(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = Exception("API error")
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        assert result.status == BotRunStatus.FAILED
        assert len(result.errors) > 0
