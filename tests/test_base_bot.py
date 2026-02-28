"""Tests for BaseBot template method pattern."""
from __future__ import annotations

import pytest

from bots.base import BaseBot
from common.models.base import BotName, BotRunStatus


class SuccessBot(BaseBot):
    name = BotName.LOCAL_SEO

    def run(self) -> dict:
        return {"result": "success", "count": 42}


class FailingBot(BaseBot):
    name = BotName.CONTENT

    def run(self) -> dict:
        raise ValueError("Intentional failure")


class TestBaseBot:
    def test_execute_success_sets_status(self):
        bot = SuccessBot()
        result = bot.execute()
        assert result.status == BotRunStatus.SUCCESS

    def test_execute_success_stores_outputs(self):
        bot = SuccessBot()
        result = bot.execute()
        assert result.outputs == {"result": "success", "count": 42}

    def test_execute_records_timing(self):
        bot = SuccessBot()
        result = bot.execute()
        assert result.started_at is not None
        assert result.finished_at is not None
        assert result.finished_at >= result.started_at

    def test_execute_failure_sets_failed_status(self):
        bot = FailingBot()
        result = bot.execute()
        assert result.status == BotRunStatus.FAILED

    def test_execute_failure_records_error(self):
        bot = FailingBot()
        result = bot.execute()
        assert len(result.errors) == 1
        assert "Intentional failure" in result.errors[0]

    def test_execute_failure_still_records_timing(self):
        bot = FailingBot()
        result = bot.execute()
        assert result.finished_at is not None
