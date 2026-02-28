"""CLI entrypoint: python -m bots.orchestrator.run"""
from __future__ import annotations

import logging
from pathlib import Path

import click

from bots.orchestrator.bot import OrchestratorBot
from bots.orchestrator.models import OrchestratorInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--output-dir", default=None, help="Directory containing bot outputs")
def main(output_dir: str | None) -> None:
    """Run the Manager/Analytics Orchestrator Bot."""
    from infra.config import settings

    orchestrator_input = OrchestratorInput(
        output_dir=Path(output_dir) if output_dir else settings.output_dir,
    )
    bot = OrchestratorBot(orchestrator_input=orchestrator_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
