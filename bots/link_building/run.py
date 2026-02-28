"""CLI entrypoint: python -m bots.link_building.run"""
from __future__ import annotations

import logging

import click

from bots.link_building.bot import LinkBuildingBot
from bots.link_building.models import LinkBuildingInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--keywords", default=None, help="Comma-separated keywords")
@click.option("--location", default=None, help="Location override")
@click.option("--seed-urls", default=None, help="Comma-separated seed URLs to process")
def main(keywords: str | None, location: str | None, seed_urls: str | None) -> None:
    """Run the Link-Building Outreach Bot."""
    from infra.config import settings

    link_input = LinkBuildingInput(
        keywords=keywords.split(",") if keywords else [settings.restaurant_cuisine, settings.restaurant_city],
        location=location or settings.restaurant_city,
        seed_urls=seed_urls.split(",") if seed_urls else [],
    )
    bot = LinkBuildingBot(link_input=link_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
