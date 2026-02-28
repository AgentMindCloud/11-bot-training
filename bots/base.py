"""Abstract base class and registry for all bots."""
from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.config import get_settings

logger = logging.getLogger(__name__)


class BotBase(ABC):
    """Abstract base that every bot must extend."""

    # ------------------------------------------------------------------
    # Subclasses must define these
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique slug for this bot (used as directory name for outputs)."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the bot does."""

    @abstractmethod
    def run(self, **kwargs: Any) -> dict:
        """Execute the bot and return a result dict."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _output_dir(self) -> Path:
        settings = get_settings()
        path = Path(settings.output_dir) / self.name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_output(self, data: dict, filename: str | None = None) -> Path:
        """Persist *data* as JSON under OUTPUT_DIR/<bot_name>/<filename>."""
        if filename is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{ts}.json"
        dest = self._output_dir() / filename
        dest.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        logger.info("Saved output to %s", dest)
        return dest

    def load_input(self, filename: str) -> dict:
        """Load a JSON file from OUTPUT_DIR/<filename> (path relative to OUTPUT_DIR)."""
        settings = get_settings()
        path = Path(settings.output_dir) / filename
        if not path.exists():
            logger.warning("load_input: %s not found", path)
            return {}
        return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class BotRegistry:
    def __init__(self) -> None:
        self._bots: dict[str, type[BotBase]] = {}

    def register(self, bot_class: type[BotBase]) -> type[BotBase]:
        """Register a bot class. Can be used as a decorator."""
        self._bots[bot_class.name.fget(bot_class)] = bot_class  # type: ignore[attr-defined]
        return bot_class

    def get(self, name: str) -> type[BotBase] | None:
        return self._bots.get(name)

    def all(self) -> dict[str, type[BotBase]]:
        return dict(self._bots)


registry = BotRegistry()
