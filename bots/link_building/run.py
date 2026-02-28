"""CLI entry-point for the Link Building bot."""
from __future__ import annotations

import logging

import click
from rich.console import Console

console = Console()
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--restaurant-name", envvar="RESTAURANT_NAME", default="My Restaurant")
@click.option("--city", envvar="RESTAURANT_CITY", default="New York")
@click.option("--cuisine", envvar="RESTAURANT_CUISINE", default="Italian")
@click.option("--save-to-db", is_flag=True, default=False, help="Persist prospects to database")
def main(restaurant_name: str, city: str, cuisine: str, save_to_db: bool) -> None:
    """Run the Link Building bot."""
    from bots.link_building.bot import LinkBuildingBot

    bot = LinkBuildingBot()
    console.print(f"[bold green]Running LinkBuildingBot for {restaurant_name}[/bold green]")
    result = bot.run(
        restaurant_name=restaurant_name,
        city=city,
        cuisine=cuisine,
        save_to_db=save_to_db,
    )
    console.print(
        f"Found {len(result['prospects'])} prospects, "
        f"drafted {len(result['outreach_emails'])} outreach emails."
    )


if __name__ == "__main__":
    main()
