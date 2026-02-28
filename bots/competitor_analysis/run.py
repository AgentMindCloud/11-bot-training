"""CLI entry-point for the Competitor Analysis bot."""
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
@click.option("--competitor-url", "competitor_urls", multiple=True, help="Competitor website URLs")
def main(restaurant_name: str, city: str, cuisine: str, competitor_urls: tuple) -> None:
    """Run the Competitor Analysis bot."""
    from bots.competitor_analysis.bot import CompetitorAnalysisBot

    bot = CompetitorAnalysisBot()
    console.print(f"[bold green]Running CompetitorAnalysisBot for {restaurant_name}[/bold green]")
    result = bot.run(
        restaurant_name=restaurant_name,
        city=city,
        cuisine=cuisine,
        competitor_urls=list(competitor_urls),
    )
    console.print(f"Analysed {len(result['competitors'])} competitors.")
    if result.get("report_markdown"):
        console.print("\n[bold]Report Preview:[/bold]")
        console.print(result["report_markdown"][:500])


if __name__ == "__main__":
    main()
