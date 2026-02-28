"""CLI entry-point for the Trend Tracking bot."""
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
def main(restaurant_name: str, city: str, cuisine: str) -> None:
    """Run the Trend Tracking bot."""
    from bots.trend_tracking.bot import TrendTrackingBot

    bot = TrendTrackingBot()
    console.print(f"[bold green]Running TrendTrackingBot for {restaurant_name}[/bold green]")
    result = bot.run(restaurant_name=restaurant_name, city=city, cuisine=cuisine)
    console.print(f"Identified {len(result['trends'])} trends.")
    if result.get("top_opportunities"):
        console.print("[bold]Top opportunities:[/bold]")
        for opp in result["top_opportunities"][:3]:
            console.print(f"  • {opp}")


if __name__ == "__main__":
    main()
