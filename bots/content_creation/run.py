"""CLI entry-point for the Content Creation bot."""
from __future__ import annotations

import logging

import click
from rich.console import Console

console = Console()
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--restaurant-name", envvar="RESTAURANT_NAME", default="My Restaurant")
@click.option("--city", envvar="RESTAURANT_CITY", default="New York")
@click.option("--neighborhood", envvar="RESTAURANT_NEIGHBORHOOD", default="East Village")
@click.option("--cuisine", envvar="RESTAURANT_CUISINE", default="Italian")
def main(restaurant_name: str, city: str, neighborhood: str, cuisine: str) -> None:
    """Run the Content Creation bot."""
    from bots.content_creation.bot import ContentCreationBot

    bot = ContentCreationBot()
    console.print(f"[bold green]Running ContentCreationBot for {restaurant_name}[/bold green]")
    result = bot.run(
        restaurant_name=restaurant_name,
        city=city,
        neighborhood=neighborhood,
        cuisine=cuisine,
    )
    console.print(f"Created {len(result['blog_posts'])} blog posts and {len(result['social_snippets'])} social snippets.")


if __name__ == "__main__":
    main()
