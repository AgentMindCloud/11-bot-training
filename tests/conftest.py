"""Pytest fixtures shared across all test modules."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_llm_client():
    """A LLMClient mock that returns predictable JSON responses."""
    mock = MagicMock()

    # Default chat_completion returns a minimal JSON string
    mock.chat_completion.return_value = json.dumps({"result": "ok"})

    # Default structured_completion raises so bots fall back to chat_completion
    mock.structured_completion.side_effect = Exception("use chat_completion fallback")

    return mock


@pytest.fixture
def sample_restaurant_info():
    return {
        "restaurant_name": "Test Trattoria",
        "city": "New York",
        "neighborhood": "East Village",
        "cuisine": "Italian",
        "address": "123 Test St, New York, NY 10001",
        "phone": "+1-212-555-0100",
        "hours": "Mon-Sun 11:00-22:00",
        "website": "https://testtrattoria.example.com",
    }


@pytest.fixture
def tmp_output_dir(tmp_path, monkeypatch):
    """Redirect OUTPUT_DIR to a temporary directory for tests."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    monkeypatch.setenv("OUTPUT_DIR", str(output_dir))

    # Clear the lru_cache so settings picks up new env var
    from common.config import get_settings
    get_settings.cache_clear()

    yield output_dir

    # Restore cache
    get_settings.cache_clear()


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings with test values."""
    env_vars = {
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "gpt-4o",
        "RESTAURANT_NAME": "Test Trattoria",
        "RESTAURANT_CITY": "New York",
        "RESTAURANT_NEIGHBORHOOD": "East Village",
        "RESTAURANT_CUISINE": "Italian",
        "DATABASE_URL": "sqlite:///:memory:",
        "OUTPUT_DIR": "/tmp/test_outputs",
    }
    for key, val in env_vars.items():
        monkeypatch.setenv(key, val)

    from common.config import get_settings
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()
