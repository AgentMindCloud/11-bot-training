"""Tests for the Forum Marketing bot."""
from __future__ import annotations

import json

import pytest

from bots.forum_marketing.bot import ForumMarketingBot
from bots.forum_marketing.models import ForumDraft


_DRAFT_RESPONSE = json.dumps({
    "platform": "reddit",
    "topic": "Best Italian restaurants in NYC?",
    "draft_content": "I've been exploring the East Village food scene lately and stumbled upon some incredible spots. Has anyone tried the handmade pasta places around 1st Ave? The quality is really something special - fresh ingredients and traditional techniques. Would love to hear other recommendations too!",
    "sensitivity_flags": [],
    "status": "pending_review",
})

_SENSITIVITY_RESPONSE = json.dumps({
    "sensitivity_flags": []
})


class TestForumMarketingBot:
    def test_generate_draft_returns_forum_draft(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _DRAFT_RESPONSE
        bot = ForumMarketingBot(llm=mock_llm_client)
        draft = bot.generate_draft(
            topic="Best Italian restaurants in NYC?",
            platform="reddit",
            restaurant_info={"restaurant_name": "Test Trattoria", "city": "New York", "neighborhood": "East Village", "cuisine": "Italian"},
        )
        assert isinstance(draft, ForumDraft)
        assert draft.platform == "reddit"
        assert draft.draft_content

    def test_generate_draft_status_is_pending_review(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _DRAFT_RESPONSE
        bot = ForumMarketingBot(llm=mock_llm_client)
        draft = bot.generate_draft(
            topic="Restaurant recommendation",
            platform="nextdoor",
            restaurant_info={"restaurant_name": "Test", "city": "NYC", "neighborhood": "EV", "cuisine": "Italian"},
        )
        assert draft.status == "pending_review"

    def test_all_drafts_start_as_pending_review(self, mock_llm_client, tmp_output_dir, mock_settings):
        """Human-in-the-loop: all drafts must start as pending_review."""
        mock_llm_client.chat_completion.side_effect = [
            _DRAFT_RESPONSE,
            _SENSITIVITY_RESPONSE,
            _DRAFT_RESPONSE,
            _SENSITIVITY_RESPONSE,
        ]
        bot = ForumMarketingBot(llm=mock_llm_client)
        result = bot.run(
            restaurant_name="Test Trattoria",
            city="New York",
            neighborhood="East Village",
            cuisine="Italian",
            topics=[("reddit", "Best Italian?"), ("nextdoor", "Dinner recommendation")],
        )
        assert all(d["status"] == "pending_review" for d in result["drafts"])

    def test_check_sensitivity_returns_list(self, mock_llm_client, mock_settings):
        mock_llm_client.chat_completion.return_value = json.dumps({
            "sensitivity_flags": ["mentions restaurant name twice"]
        })
        bot = ForumMarketingBot(llm=mock_llm_client)
        draft = ForumDraft(
            platform="reddit",
            topic="test",
            draft_content="Visit Test Trattoria! Test Trattoria is great!",
        )
        flags = bot.check_sensitivity(draft)
        assert isinstance(flags, list)
        assert len(flags) > 0
