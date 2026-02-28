"""CLI entrypoint: python -m bots.forum.run"""
from __future__ import annotations

import logging

import click

from bots.forum.bot import ForumBot
from bots.forum.models import ForumInput, PlatformType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--topic", required=True, help="Forum topic or question to respond to")
@click.option(
    "--platform",
    default="other",
    type=click.Choice([p.value for p in PlatformType]),
)
@click.option("--context", default="", help="Additional context about the thread")
@click.option("--num-drafts", default=3, type=int, help="Number of draft variants to generate")
def main(topic: str, platform: str, context: str, num_drafts: int) -> None:
    """Run the Forum & Community Marketing Bot (human-in-the-loop)."""
    forum_input = ForumInput(
        topic=topic,
        platform=PlatformType(platform),
        context=context,
        num_drafts=num_drafts,
    )
    bot = ForumBot(forum_input=forum_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
