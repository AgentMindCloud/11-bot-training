"""Unit tests for ForumBot sensitive keyword detection."""
from __future__ import annotations

import json

import pytest

from bots.forum.bot import ForumBot, SENSITIVE_KEYWORDS
from bots.forum.models import ForumInput, PlatformType, ReviewStatus
from common.models.base import BotRunStatus


MOCK_CLEAN_DRAFT = json.dumps({
    "draft_text": "I've been going to My Restaurant for years and the pasta is fantastic. Highly recommend!",
    "sensitive_flags": [],
})

MOCK_SPAMMY_DRAFT = json.dumps({
    "draft_text": "Check out my favorite Italian place! Limited offer on pasta this week, buy now!",
    "sensitive_flags": [],
})

MOCK_FLAGGED_DRAFT = json.dumps({
    "draft_text": "Great food here.",
    "sensitive_flags": ["Might appear self-promotional"],
})


class TestForumBot:
    def _make_bot(self, mock_llm, topic="best Italian restaurants", num_drafts=1):
        forum_input = ForumInput(
            topic=topic,
            platform=PlatformType.REDDIT,
            num_drafts=num_drafts,
        )
        return ForumBot(forum_input=forum_input, llm=mock_llm)

    def test_run_generates_drafts(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_CLEAN_DRAFT
        bot = self._make_bot(mock_llm, num_drafts=2)
        result = bot.execute()

        assert result.status == BotRunStatus.SUCCESS
        assert len(result.outputs["drafts"]) == 2

    def test_drafts_start_as_pending(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_CLEAN_DRAFT
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        draft = result.outputs["drafts"][0]
        assert draft["status"] == ReviewStatus.PENDING.value

    def test_spammy_keywords_are_flagged(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_SPAMMY_DRAFT
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        draft = result.outputs["drafts"][0]
        assert len(draft["sensitive_flags"]) > 0
        # "buy now" and "limited offer" should be detected
        flags_text = " ".join(draft["sensitive_flags"]).lower()
        assert "buy now" in flags_text or "limited offer" in flags_text

    def test_clean_draft_has_no_flags(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_CLEAN_DRAFT
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        draft = result.outputs["drafts"][0]
        assert draft["sensitive_flags"] == []

    def test_llm_flags_are_preserved(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_FLAGGED_DRAFT
        bot = self._make_bot(mock_llm)
        result = bot.execute()

        draft = result.outputs["drafts"][0]
        assert "Might appear self-promotional" in draft["sensitive_flags"]

    def test_review_queue_file_created(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_CLEAN_DRAFT
        bot = self._make_bot(mock_llm)
        bot.execute()

        queue_file = tmp_path / "forum_review_queue.json"
        assert queue_file.exists()

    def test_draft_has_unique_ids(self, mocker, tmp_path, monkeypatch):
        monkeypatch.setattr("infra.config.settings.output_dir", tmp_path)
        mock_llm = mocker.MagicMock()
        mock_llm.chat.return_value = MOCK_CLEAN_DRAFT
        bot = self._make_bot(mock_llm, num_drafts=3)
        result = bot.execute()

        ids = [d["id"] for d in result.outputs["drafts"]]
        assert len(set(ids)) == 3  # all unique

    def test_sensitive_keywords_list_is_not_empty(self):
        assert len(SENSITIVE_KEYWORDS) > 0
