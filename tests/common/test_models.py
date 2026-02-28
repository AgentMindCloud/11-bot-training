"""Tests for shared base models."""
from __future__ import annotations

from datetime import datetime

import pytest

from common.models.base import (
    BotName,
    BotRunResult,
    BotRunStatus,
    ContentPiece,
    KeywordCluster,
    RestaurantProfile,
)


class TestBotRunResult:
    def test_default_status_is_success(self):
        result = BotRunResult(bot=BotName.LOCAL_SEO, status=BotRunStatus.SUCCESS)
        assert result.status == BotRunStatus.SUCCESS

    def test_errors_default_empty(self):
        result = BotRunResult(bot=BotName.CONTENT, status=BotRunStatus.SUCCESS)
        assert result.errors == []

    def test_outputs_default_empty(self):
        result = BotRunResult(bot=BotName.FORUM, status=BotRunStatus.FAILED)
        assert result.outputs == {}

    def test_started_at_auto_set(self):
        result = BotRunResult(bot=BotName.ORCHESTRATOR, status=BotRunStatus.SUCCESS)
        assert isinstance(result.started_at, datetime)


class TestKeywordCluster:
    def test_valid_priority_range(self):
        cluster = KeywordCluster(
            theme="Local dining",
            keywords=["italian restaurant austin"],
            intent="transactional",
            priority=3,
        )
        assert cluster.priority == 3

    def test_priority_below_1_rejected(self):
        with pytest.raises(Exception):
            KeywordCluster(
                theme="test",
                keywords=["kw"],
                intent="transactional",
                priority=0,
            )

    def test_priority_above_5_rejected(self):
        with pytest.raises(Exception):
            KeywordCluster(
                theme="test",
                keywords=["kw"],
                intent="transactional",
                priority=6,
            )

    def test_keywords_list_stored(self):
        cluster = KeywordCluster(
            theme="Pizza",
            keywords=["best pizza", "pizza near me"],
            intent="navigational",
            priority=2,
        )
        assert len(cluster.keywords) == 2


class TestContentPiece:
    def test_content_piece_creation(self):
        piece = ContentPiece(
            title="How to make pasta",
            body="Start with good flour...",
            content_type="blog",
            keywords=["pasta recipe"],
        )
        assert piece.content_type == "blog"
        assert isinstance(piece.created_at, datetime)

    def test_keywords_default_empty(self):
        piece = ContentPiece(
            title="FAQ",
            body="Answer here",
            content_type="faq",
        )
        assert piece.keywords == []


class TestRestaurantProfile:
    def test_required_fields(self):
        profile = RestaurantProfile(
            name="My Restaurant",
            city="Austin",
            neighborhood="East Austin",
            cuisine="Italian",
            website="https://myrestaurant.com",
        )
        assert profile.name == "My Restaurant"

    def test_optional_fields_default_empty(self):
        profile = RestaurantProfile(
            name="Test",
            city="Dallas",
            neighborhood="Downtown",
            cuisine="Mexican",
            website="https://test.com",
        )
        assert profile.phone == ""
        assert profile.hours == ""


class TestBotNameEnum:
    def test_all_eleven_bots_defined(self):
        expected = {
            "local_seo", "content", "forum", "link_building", "competitor",
            "trend_tracking", "chatbot", "orchestrator", "review_monitor",
            "reservation_funnel", "loyalty",
        }
        actual = {b.value for b in BotName}
        assert actual == expected
