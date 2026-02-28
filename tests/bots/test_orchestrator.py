"""Unit tests for OrchestratorBot report building."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bots.orchestrator.bot import OrchestratorBot
from bots.orchestrator.models import OrchestratorInput
from common.models.base import BotRunStatus


MOCK_INSIGHTS = json.dumps(["Insight A", "Insight B", "Insight C"])

MOCK_SYNTHESIS = json.dumps({
    "executive_summary": "The restaurant's marketing is performing well with strong SEO opportunities.",
    "actionable_tasks": [
        {
            "title": "Update meta descriptions",
            "description": "Apply SEO bot recommendations to homepage and menu pages.",
            "source_bot": "local_seo",
            "priority": "high",
            "tags": ["seo"],
        },
        {
            "title": "Publish blog posts",
            "description": "Schedule the 3 generated blog posts for the next 2 weeks.",
            "source_bot": "content",
            "priority": "medium",
            "tags": ["content"],
        },
    ],
})


class TestOrchestratorBot:
    def _write_fake_output(self, output_dir: Path, filename: str, data: dict) -> None:
        (output_dir / filename).write_text(json.dumps(data))

    def test_run_with_no_outputs_returns_empty_report(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        monkeypatch.setattr("infra.config.settings.reports_dir", tmp_path / "reports")
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_SYNTHESIS

        bot = OrchestratorBot(
            orchestrator_input=OrchestratorInput(output_dir=tmp_path),
            llm=mock_llm,
        )
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert result.outputs["bot_summaries"] == []

    def test_run_collects_existing_bot_outputs(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        monkeypatch.setattr("infra.config.settings.reports_dir", tmp_path / "reports")
        (tmp_path / "reports").mkdir()

        self._write_fake_output(
            tmp_path,
            "local_seo_output.json",
            {"keyword_clusters": [{"theme": "test", "keywords": ["kw1"], "intent": "transactional", "priority": 1}]},
        )

        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [MOCK_INSIGHTS, MOCK_SYNTHESIS]

        bot = OrchestratorBot(
            orchestrator_input=OrchestratorInput(output_dir=tmp_path),
            llm=mock_llm,
        )
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        summaries = result.outputs["bot_summaries"]
        assert len(summaries) == 1
        assert summaries[0]["bot_name"] == "local_seo"

    def test_run_generates_actionable_tasks(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        monkeypatch.setattr("infra.config.settings.reports_dir", tmp_path / "reports")
        (tmp_path / "reports").mkdir()

        self._write_fake_output(tmp_path, "content_output.json", {"blog_posts": []})

        mock_llm = mocker.MagicMock()
        mock_llm.chat.side_effect = [MOCK_INSIGHTS, MOCK_SYNTHESIS]

        bot = OrchestratorBot(
            orchestrator_input=OrchestratorInput(output_dir=tmp_path),
            llm=mock_llm,
        )
        result = bot.execute()

        tasks = result.outputs["actionable_tasks"]
        assert len(tasks) == 2
        assert tasks[0]["priority"] == "high"
        assert tasks[0]["title"] == "Update meta descriptions"

    def test_report_files_are_saved(self, mocker, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        monkeypatch.setattr("infra.config.settings.reports_dir", reports_dir)
        reports_dir.mkdir()

        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_SYNTHESIS

        bot = OrchestratorBot(
            orchestrator_input=OrchestratorInput(output_dir=tmp_path),
            llm=mock_llm,
        )
        bot.execute()

        report_files = list(reports_dir.glob("weekly_report_*.json"))
        md_files = list(reports_dir.glob("weekly_report_*.md"))
        assert len(report_files) == 1
        assert len(md_files) == 1

    def test_report_markdown_contains_summary(self, mocker, tmp_path, monkeypatch):
        reports_dir = tmp_path / "reports"
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        monkeypatch.setattr("infra.config.settings.reports_dir", reports_dir)
        reports_dir.mkdir()

        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_SYNTHESIS

        bot = OrchestratorBot(
            orchestrator_input=OrchestratorInput(output_dir=tmp_path),
            llm=mock_llm,
        )
        result = bot.execute()

        assert "performing well" in result.outputs["report_markdown"]
