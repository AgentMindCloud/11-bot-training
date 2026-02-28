"""Review Monitoring bot (future implementation).

TODO: This bot should:
- Monitor Google My Business, Yelp, TripAdvisor, and other review platforms
- Alert the team to new negative reviews
- Suggest templated response drafts for negative reviews
- Track review sentiment trends over time
- Identify recurring complaints for operational improvement
"""
from __future__ import annotations

from bots.base import BotBase


class ReviewMonitoringBot(BotBase):
    name = "review_monitoring"
    description = "Monitors online reviews and generates response drafts (not yet implemented)"

    def run(self, **kwargs) -> dict:
        raise NotImplementedError(
            "ReviewMonitoringBot is planned for a future release. "
            "It will monitor Google, Yelp, and TripAdvisor reviews and "
            "generate response drafts for negative feedback."
        )
