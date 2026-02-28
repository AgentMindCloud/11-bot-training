"""Tests for bots/base.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bots.base import BotBase, BotRegistry


class _ConcreteBot(BotBase):
    name = "test_bot"
    description = "A bot used only for testing"

    def run(self, **kwargs):
        return {"status": "ok"}


class TestBotBase:
    def test_save_output_creates_file(self, tmp_output_dir):
        bot = _ConcreteBot()
        data = {"key": "value", "number": 42}
        dest = bot.save_output(data, "test_output.json")
        assert dest.exists()
        loaded = json.loads(dest.read_text())
        assert loaded["key"] == "value"
        assert loaded["number"] == 42

    def test_save_output_auto_filename(self, tmp_output_dir):
        bot = _ConcreteBot()
        dest = bot.save_output({"auto": True})
        assert dest.exists()
        assert "test_bot" in dest.name

    def test_load_input_reads_file(self, tmp_output_dir):
        # Write a file manually
        subdir = tmp_output_dir / "some_bot"
        subdir.mkdir(parents=True, exist_ok=True)
        (subdir / "data.json").write_text(json.dumps({"loaded": True}))

        bot = _ConcreteBot()
        result = bot.load_input("some_bot/data.json")
        assert result["loaded"] is True

    def test_load_input_missing_file_returns_empty(self, tmp_output_dir):
        bot = _ConcreteBot()
        result = bot.load_input("nonexistent/file.json")
        assert result == {}


class TestBotRegistry:
    def test_register_and_retrieve(self):
        registry = BotRegistry()

        class _Reg(BotBase):
            name = "reg_bot"
            description = "registered bot"

            def run(self, **kwargs):
                return {}

        # Register manually
        registry._bots["reg_bot"] = _Reg

        retrieved = registry.get("reg_bot")
        assert retrieved is _Reg

    def test_get_unknown_returns_none(self):
        registry = BotRegistry()
        assert registry.get("does_not_exist") is None

    def test_all_returns_dict(self):
        registry = BotRegistry()
        registry._bots["a"] = _ConcreteBot
        assert "a" in registry.all()
