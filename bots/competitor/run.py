"""CLI entrypoint: python -m bots.competitor.run"""
from __future__ import annotations

import logging

import click

from bots.competitor.bot import CompetitorBot
from bots.competitor.models import CompetitorInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.argument("urls", nargs=-1, required=True)
def main(urls: tuple[str, ...]) -> None:
    """Run the Competitor Website Analysis Bot on given URLs."""
    competitor_input = CompetitorInput(competitor_urls=list(urls))
    bot = CompetitorBot(competitor_input=competitor_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
