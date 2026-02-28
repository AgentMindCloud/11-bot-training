"""CLI entry-point for the Orchestrator bot."""
from __future__ import annotations

import logging

import click
from rich.console import Console
from rich.markdown import Markdown

console = Console()
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--show-report", is_flag=True, default=False, help="Print the Markdown report")
def main(show_report: bool) -> None:
    """Run the Orchestrator bot."""
    from bots.orchestrator.bot import OrchestratorBot

    bot = OrchestratorBot()
    console.print("[bold green]Running OrchestratorBot[/bold green]")
    result = bot.run()

    console.print(f"\nHealth score: [bold]{result.get('overall_health_score', 0)}/10[/bold]")
    console.print(f"Bot summaries: {len(result.get('bot_summaries', []))}")
    console.print(f"Top tasks: {len(result.get('top_tasks', []))}")

    if show_report and result.get("report_markdown"):
        console.print("\n")
        console.print(Markdown(result["report_markdown"]))


if __name__ == "__main__":
    main()
