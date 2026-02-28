"""Tests for the Local SEO bot."""
from __future__ import annotations

import json

import pytest

from bots.local_seo.bot import LocalSeoBot
from bots.local_seo.models import KeywordCluster, LocalSeoOutput


_KEYWORD_RESPONSE = json.dumps({
    "keyword_clusters": [
        {
            "keyword": "Italian restaurant New York",
            "variations": ["NYC Italian food", "best Italian NYC"],
            "search_intent": "local",
            "monthly_volume_estimate": 5000,
        },
        {
            "keyword": "East Village pasta",
            "variations": ["pasta near me", "East Village dinner"],
            "search_intent": "transactional",
            "monthly_volume_estimate": 800,
        },
    ]
})

_SEO_META_RESPONSE = json.dumps({
    "seo_metas": [
        {
            "page_type": "Homepage",
            "title_tag": "Test Trattoria | Italian Restaurant East Village NYC",
            "meta_description": "Authentic Italian cuisine in the heart of East Village, New York. Book your table today.",
            "h1": "Authentic Italian Restaurant in East Village, NYC",
            "target_keywords": ["Italian restaurant NYC", "East Village Italian"],
        }
    ]
})

_LINKS_RESPONSE = json.dumps({
    "internal_links": [
        {
            "source_page": "Homepage",
            "target_page": "Menu",
            "anchor_text": "authentic Italian pasta",
            "reason": "Drives traffic to high-converting menu page",
        }
    ]
})


class TestLocalSeoBot:
    def test_generate_keywords_calls_llm(self, mock_llm_client, tmp_output_dir):
        mock_llm_client.chat_completion.return_value = _KEYWORD_RESPONSE
        bot = LocalSeoBot(llm=mock_llm_client)
        clusters = bot.generate_keywords("Test Trattoria", "New York", "East Village", "Italian")
        assert len(clusters) == 2
        assert isinstance(clusters[0], KeywordCluster)
        assert clusters[0].keyword == "Italian restaurant New York"
        mock_llm_client.chat_completion.assert_called_once()

    def test_generate_keywords_returns_list(self, mock_llm_client, tmp_output_dir):
        mock_llm_client.chat_completion.return_value = _KEYWORD_RESPONSE
        bot = LocalSeoBot(llm=mock_llm_client)
        result = bot.generate_keywords("R", "C", "N", "Italian")
        assert isinstance(result, list)
        assert all(isinstance(kc, KeywordCluster) for kc in result)

    def test_generate_seo_metas(self, mock_llm_client, tmp_output_dir):
        mock_llm_client.chat_completion.return_value = _SEO_META_RESPONSE
        bot = LocalSeoBot(llm=mock_llm_client)
        clusters = [KeywordCluster(keyword="Italian NYC", variations=[], search_intent="local", monthly_volume_estimate=100)]
        metas = bot.generate_seo_metas(clusters, ["Homepage"])
        assert len(metas) == 1
        assert "East Village" in metas[0].title_tag

    def test_run_returns_local_seo_output_compatible_dict(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.side_effect = [
            _KEYWORD_RESPONSE,
            _SEO_META_RESPONSE,
            _LINKS_RESPONSE,
        ]
        bot = LocalSeoBot(llm=mock_llm_client)
        result = bot.run(
            restaurant_name="Test Trattoria",
            city="New York",
            neighborhood="East Village",
            cuisine="Italian",
        )
        # Should be parseable as LocalSeoOutput
        output = LocalSeoOutput.model_validate(result)
        assert output.restaurant_name == "Test Trattoria"
        assert len(output.keyword_clusters) == 2
        assert len(output.seo_metas) == 1
        assert len(output.internal_links) == 1

    def test_parse_keyword_clusters_fallback(self):
        raw = json.dumps([
            {"keyword": "pizza NYC", "variations": [], "search_intent": "local", "monthly_volume_estimate": 100}
        ])
        clusters = LocalSeoBot._parse_keyword_clusters(raw)
        assert len(clusters) == 1
        assert clusters[0].keyword == "pizza NYC"

    def test_parse_keyword_clusters_handles_bad_json(self):
        clusters = LocalSeoBot._parse_keyword_clusters("not json at all")
        assert clusters == []
