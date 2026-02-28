"""CLI entrypoint: python -m bots.trend_tracking.run"""
from __future__ import annotations

import logging

import click

from bots.trend_tracking.bot import DEFAULT_TREND_URLS, TrendTrackingBot
from bots.trend_tracking.models import TrendInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--urls", default=None, help="Comma-separated news source URLs")
@click.option("--topics", default=None, help="Comma-separated topics to track")
def main(urls: str | None, topics: str | None) -> None:
    """Run the Industry/Trend Tracking Bot."""
    trend_input = TrendInput(
        seed_urls=urls.split(",") if urls else DEFAULT_TREND_URLS,
        topics=topics.split(",") if topics else ["restaurant trends", "food delivery"],
    )
    bot = TrendTrackingBot(trend_input=trend_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
