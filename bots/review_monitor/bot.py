"""Review Monitor Bot (Bot 9) — stub for future implementation."""
from __future__ import annotations

import logging

from bots.base import BaseBot
from common.models.base import BotName

logger = logging.getLogger(__name__)


class ReviewMonitorBot(BaseBot):
    """
    TODO: Monitor and respond to reviews on Google, Yelp, TripAdvisor.
    Responsibilities:
    - Poll review platforms via API or scraping
    - Detect sentiment (positive/negative/neutral)
    - Draft response suggestions for management approval
    - Alert on negative reviews for immediate action
    """

    name = BotName.REVIEW_MONITOR

    def run(self) -> dict:
        logger.info("ReviewMonitorBot: not yet implemented")
        return {"status": "stub", "message": "ReviewMonitorBot is not yet implemented."}
