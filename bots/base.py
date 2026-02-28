"""Abstract base class for all bots."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from common.models.base import BotName, BotRunResult, BotRunStatus

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    """Every bot must inherit from BaseBot and implement `run()`."""

    name: BotName

    def __init__(self) -> None:
        self._result = BotRunResult(bot=self.name, status=BotRunStatus.SUCCESS)

    def execute(self) -> BotRunResult:
        """Template method: wrap run() with timing and error handling."""
        self._result.started_at = datetime.now(timezone.utc)
        try:
            outputs = self.run()
            self._result.outputs = outputs or {}
            self._result.status = BotRunStatus.SUCCESS
        except Exception as exc:
            logger.exception("Bot %s failed: %s", self.name, exc)
            self._result.errors.append(str(exc))
            self._result.status = BotRunStatus.FAILED
        finally:
            self._result.finished_at = datetime.now(timezone.utc)
        return self._result

    @abstractmethod
    def run(self) -> dict:
        """Perform the bot's work and return a dict of outputs."""
