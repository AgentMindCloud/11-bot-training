"""Tests for the Orchestrator bot."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from bots.orchestrator.bot import OrchestratorBot
from bots.orchestrator.models import BotSummary, ExecutiveSummary


_SUMMARY_RESPONSE = json.dumps({
    "bot_name": "local_seo",
    "last_run": None,
    "key_findings": [
        "Identified 8 keyword clusters",
        "Generated SEO metas for 6 pages",
        "Suggested 6 internal links",
    ],
    "tasks": [
        {
            "title": "Implement keyword-optimised title tags",
            "description": "Update all page title tags based on recommendations",
            "priority": "high",
            "source_bot": "local_seo",
            "estimated_effort": "2 hours",
        }
    ],
})

_EXEC_SUMMARY_RESPONSE = "# Marketing Summary\n\n## Executive Summary\n\nAll systems operational.\n\n## Top Actions\n\n1. Implement SEO recommendations\n"

_PRIORITIZE_RESPONSE = json.dumps({
    "top_tasks": [
        {
            "title": "Implement keyword-optimised title tags",
            "description": "Update page titles",
            "priority": "high",
            "source_bot": "local_seo",
            "estimated_effort": "2 hours",
        }
    ]
})


class TestOrchestratorBot:
    def test_load_bot_outputs_loads_json_files(self, tmp_output_dir):
        # Create fake bot output files
        for bot_name in ["local_seo", "content_creation"]:
            bot_dir = tmp_output_dir / bot_name
            bot_dir.mkdir(parents=True)
            (bot_dir / "latest.json").write_text(
                json.dumps({"bot": bot_name, "generated_at": "2024-01-01T00:00:00"}),
                encoding="utf-8",
            )

        bot = OrchestratorBot.__new__(OrchestratorBot)
        bot._llm = None  # won't be used for this test
        outputs = bot.load_bot_outputs()

        assert "local_seo" in outputs
        assert "content_creation" in outputs
        assert outputs["local_seo"]["bot"] == "local_seo"

    def test_load_bot_outputs_ignores_missing_bots(self, tmp_output_dir):
        # Only create one bot output
        bot_dir = tmp_output_dir / "trend_tracking"
        bot_dir.mkdir(parents=True)
        (bot_dir / "latest.json").write_text(json.dumps({"test": True}))

        bot = OrchestratorBot.__new__(OrchestratorBot)
        bot._llm = None
        outputs = bot.load_bot_outputs()
        assert "trend_tracking" in outputs
        assert "local_seo" not in outputs

    def test_generate_executive_summary_returns_executive_summary(
        self, mock_llm_client, tmp_output_dir, mock_settings
    ):
        mock_llm_client.chat_completion.side_effect = [
            _PRIORITIZE_RESPONSE,
            _EXEC_SUMMARY_RESPONSE,
        ]
        bot = OrchestratorBot(llm=mock_llm_client)
        summaries = [
            BotSummary(
                bot_name="local_seo",
                last_run=datetime.now(timezone.utc),
                key_findings=["Found 8 keyword clusters"],
                tasks=[],
            )
        ]
        result = bot.generate_executive_summary(summaries)
        assert isinstance(result, ExecutiveSummary)
        assert result.period
        assert result.report_markdown
        assert isinstance(result.overall_health_score, float)

    def test_summarize_bot_output_uses_llm(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _SUMMARY_RESPONSE
        bot = OrchestratorBot(llm=mock_llm_client)
        summary = bot.summarize_bot_output("local_seo", {"keyword_clusters": [], "generated_at": "2024-01-01"})
        assert isinstance(summary, BotSummary)
        assert summary.bot_name == "local_seo"
        assert len(summary.key_findings) > 0
