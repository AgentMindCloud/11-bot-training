"""Unit tests for CompetitorBot with mocked crawler and LLM."""
from __future__ import annotations

import json

import pytest

from bots.competitor.bot import CompetitorBot
from bots.competitor.models import CompetitorInput
from common.crawling.crawler import CrawledPage
from common.models.base import BotRunStatus


MOCK_EXTRACT = json.dumps({
    "name": "Pizza Palace",
    "cuisines": ["italian", "pizza"],
    "price_range": "$$$",
    "menu_items": [
        {"name": "Margherita", "price": "$18", "description": "Classic pizza", "category": "Pizza"}
    ],
    "delivery_platforms": ["DoorDash"],
    "promotions": ["Happy Hour Mon-Fri"],
    "usps": ["wood-fired oven"],
})

MOCK_COMPARE = json.dumps({
    "comparisons": [
        {
            "axis": "price_range",
            "our_value": "$$",
            "competitor_value": "$$$",
            "advantage": "ours",
            "notes": "We are more affordable",
        }
    ],
    "opportunities": ["Introduce wood-fired dishes"],
    "threats": ["Competitor has delivery on DoorDash"],
})


class TestCompetitorBot:
    def _make_bot(self, mock_llm, mock_crawler, urls=None):
        competitor_input = CompetitorInput(
            competitor_urls=urls or ["https://pizzapalace.com"],
        )
        return CompetitorBot(competitor_input=competitor_input, llm=mock_llm, crawler=mock_crawler)

    def _make_crawled_page(self, url="https://pizzapalace.com"):
        return CrawledPage(
            url=url,
            status_code=200,
            title="Pizza Palace - Austin",
            text="Welcome to Pizza Palace. We serve authentic Italian pizza in Austin.",
            links=[],
            emails=["info@pizzapalace.com"],
        )

    def test_run_analyzes_competitor(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [MOCK_EXTRACT, MOCK_COMPARE]
        mock_crawler = mocker.MagicMock()
        mock_crawler.fetch.return_value = self._make_crawled_page()

        bot = self._make_bot(mock_llm, mock_crawler)
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert result.outputs["total_analyzed"] == 1

    def test_run_extracts_competitor_profile(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [MOCK_EXTRACT, MOCK_COMPARE]
        mock_crawler = mocker.MagicMock()
        mock_crawler.fetch.return_value = self._make_crawled_page()

        bot = self._make_bot(mock_llm, mock_crawler)
        result = bot.execute()

        report = result.outputs["reports"][0]
        assert report["competitor"]["name"] == "Pizza Palace"
        assert report["competitor"]["price_range"] == "$$$"

    def test_run_generates_comparison(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [MOCK_EXTRACT, MOCK_COMPARE]
        mock_crawler = mocker.MagicMock()
        mock_crawler.fetch.return_value = self._make_crawled_page()

        bot = self._make_bot(mock_llm, mock_crawler)
        result = bot.execute()

        report = result.outputs["reports"][0]
        assert len(report["comparisons"]) == 1
        assert report["comparisons"][0]["axis"] == "price_range"

    def test_unreachable_url_is_skipped(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_crawler = mocker.MagicMock()
        mock_crawler.fetch.return_value = CrawledPage(
            url="https://down.com", status_code=0
        )

        bot = self._make_bot(mock_llm, mock_crawler, urls=["https://down.com"])
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert result.outputs["total_analyzed"] == 0

    def test_output_file_saved(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [MOCK_EXTRACT, MOCK_COMPARE]
        mock_crawler = mocker.MagicMock()
        mock_crawler.fetch.return_value = self._make_crawled_page()

        bot = self._make_bot(mock_llm, mock_crawler)
        bot.execute()

        output_file = tmp_path / "competitor_output.json"
        assert output_file.exists()
