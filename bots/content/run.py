"""CLI entrypoint: python -m bots.content.run"""
from __future__ import annotations

import json
import logging

import click

from bots.content.bot import ContentBot
from bots.content.models import ContentInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--topics", default=None, help="Comma-separated topics")
@click.option(
    "--platform",
    default="all",
    type=click.Choice(["all", "blog", "facebook", "tiktok"]),
)
@click.option("--seo-file", default=None, help="Path to local_seo_output.json")
def main(topics: str | None, platform: str, seo_file: str | None) -> None:
    """Run the Content Creation & Distribution Bot."""
    from common.models.base import KeywordCluster

    clusters: list[KeywordCluster] = []
    if seo_file:
        with open(seo_file) as f:
            data = json.load(f)
        clusters = [KeywordCluster(**c) for c in data.get("keyword_clusters", [])]

    content_input = ContentInput(
        keyword_clusters=clusters,
        topics=topics.split(",") if topics else [],
        target_platform=platform,
    )
    bot = ContentBot(content_input=content_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
