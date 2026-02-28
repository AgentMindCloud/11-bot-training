"""CLI entrypoint: python -m bots.local_seo.run"""
from __future__ import annotations

import logging

import click

from bots.local_seo.bot import LocalSeoBot
from bots.local_seo.models import SeoInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--city", default=None, help="City override")
@click.option("--neighborhood", default=None, help="Neighborhood override")
@click.option("--cuisine", default=None, help="Cuisine override")
def main(city: str | None, neighborhood: str | None, cuisine: str | None) -> None:
    """Run the Local SEO Optimization Bot."""
    from infra.config import settings

    seo_input = SeoInput(
        city=city or settings.restaurant_city,
        neighborhood=neighborhood or settings.restaurant_neighborhood,
        cuisine=cuisine or settings.restaurant_cuisine,
        website=settings.restaurant_website,
    )
    bot = LocalSeoBot(seo_input=seo_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
