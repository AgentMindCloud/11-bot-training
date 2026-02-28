"""Tests for the Competitor Analysis bot."""
from __future__ import annotations

import json

import pytest

from bots.competitor_analysis.bot import CompetitorAnalysisBot
from bots.competitor_analysis.models import CompetitorProfile, CompetitorComparison


_PROFILE_RESPONSE = json.dumps({
    "name": "Rival Ristorante",
    "url": "https://rival.example.com",
    "cuisine": "Italian",
    "price_range": "$$",
    "menu_items": [
        {"name": "Spaghetti Carbonara", "description": "Classic Roman pasta", "price": 18.0, "category": "Pasta"},
        {"name": "Margherita Pizza", "description": "Wood-fired", "price": 16.0, "category": "Pizza"},
    ],
    "usps": ["Wood-fired oven", "100-year-old family recipes"],
    "delivery_platforms": ["UberEats", "DoorDash"],
    "promotions": ["Happy hour 5-7pm", "Free dessert on birthdays"],
})

_COMPARISON_RESPONSE = json.dumps({
    "our_restaurant": "Test Trattoria",
    "competitor": {
        "name": "Rival Ristorante",
        "url": "https://rival.example.com",
        "cuisine": "Italian",
        "price_range": "$$",
        "menu_items": [],
        "usps": ["Wood-fired oven"],
        "delivery_platforms": ["UberEats"],
        "promotions": [],
    },
    "comparison_axes": {
        "pricing": "Both are mid-range $$",
        "cuisine_overlap": "High overlap - both Italian",
        "differentiators": "We focus on handmade pasta; they focus on wood-fired",
        "delivery_presence": "Both on UberEats",
        "promotions": "Rival has happy hour; we should consider this",
        "opportunities": "We could differentiate on private dining and events",
    },
    "summary": "Rival Ristorante is our closest competitor with similar price point and cuisine. We should emphasise our handmade pasta and personal service as differentiators.",
})

_REPORT_RESPONSE = "# Competitor Analysis Report\n\n## Executive Summary\n\nTest Trattoria operates in a competitive Italian dining market.\n"


class TestCompetitorAnalysisBot:
    def test_extract_competitor_profile_parses_correctly(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _PROFILE_RESPONSE
        bot = CompetitorAnalysisBot(llm=mock_llm_client)
        profile = bot.extract_competitor_profile(
            url="https://rival.example.com",
            html="<html><body>Rival Ristorante - Italian restaurant in NYC</body></html>",
            restaurant_name="Test Trattoria",
        )
        assert isinstance(profile, CompetitorProfile)
        assert profile.name == "Rival Ristorante"
        assert profile.cuisine == "Italian"
        assert len(profile.menu_items) == 2
        assert profile.price_range == "$$"

    def test_extract_competitor_profile_has_url(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _PROFILE_RESPONSE
        bot = CompetitorAnalysisBot(llm=mock_llm_client)
        profile = bot.extract_competitor_profile("https://rival.example.com", "html text", "Our Restaurant")
        assert profile.url == "https://rival.example.com"

    def test_generate_report_returns_markdown(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _REPORT_RESPONSE
        bot = CompetitorAnalysisBot(llm=mock_llm_client)
        profile = CompetitorProfile(name="Rival", url="https://rival.example.com")
        comparison = CompetitorComparison(
            our_restaurant="Test Trattoria",
            competitor=profile,
            summary="Test summary",
        )
        report = bot.generate_report([comparison])
        assert isinstance(report, str)
        assert len(report) > 0
        assert "#" in report  # contains markdown heading

    def test_generate_report_empty_comparisons_still_returns_string(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _REPORT_RESPONSE
        bot = CompetitorAnalysisBot(llm=mock_llm_client)
        report = bot.generate_report([])
        assert isinstance(report, str)
