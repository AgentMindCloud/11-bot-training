"""Reservation Funnel bot (future implementation).

TODO: This bot should:
- Track reservation intent signals from chatbot conversations
- Send automated follow-up emails to users who showed reservation intent
- Integrate with OpenTable, Resy, or other reservation platforms
- A/B test different reservation CTAs
- Report on reservation conversion rates
"""
from __future__ import annotations

from bots.base import BotBase


class ReservationFunnelBot(BotBase):
    name = "reservation_funnel"
    description = "Manages reservation conversion funnel and follow-ups (not yet implemented)"

    def run(self, **kwargs) -> dict:
        raise NotImplementedError(
            "ReservationFunnelBot is planned for a future release. "
            "It will track reservation intent and automate follow-up "
            "communications to convert interested visitors into bookings."
        )
