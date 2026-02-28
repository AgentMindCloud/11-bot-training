"""CLI entry-point for the Local SEO bot."""
from __future__ import annotations

import logging

import click
from rich.console import Console
from rich.json import JSON

console = Console()
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--restaurant-name", envvar="RESTAURANT_NAME", default="My Restaurant", show_default=True)
@click.option("--city", envvar="RESTAURANT_CITY", default="New York", show_default=True)
@click.option("--neighborhood", envvar="RESTAURANT_NEIGHBORHOOD", default="East Village", show_default=True)
@click.option("--cuisine", envvar="RESTAURANT_CUISINE", default="Italian", show_default=True)
def main(restaurant_name: str, city: str, neighborhood: str, cuisine: str) -> None:
    """Run the Local SEO bot."""
    from bots.local_seo.bot import LocalSeoBot

    bot = LocalSeoBot()
    console.print(f"[bold green]Running LocalSeoBot for {restaurant_name}[/bold green]")
    result = bot.run(
        restaurant_name=restaurant_name,
        city=city,
        neighborhood=neighborhood,
        cuisine=cuisine,
    )
    console.print(JSON.from_data(result))


if __name__ == "__main__":
    main()
