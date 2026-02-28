"""CLI entry-point for the Chatbot bot."""
from __future__ import annotations

import logging

import click
from rich.console import Console

console = Console()
logging.basicConfig(level=logging.INFO)


@click.command()
@click.option("--demo", is_flag=True, default=True, help="Run demo conversation")
def main(demo: bool) -> None:
    """Run the Chatbot bot in demo mode."""
    from bots.chatbot.bot import ChatbotBot

    bot = ChatbotBot()
    console.print("[bold green]Running ChatbotBot (demo mode)[/bold green]")
    result = bot.run()
    sessions = result.get("sessions", [])
    if sessions:
        console.print(f"\n[bold]Demo conversation ({len(sessions[0]['messages'])} messages):[/bold]")
        for msg in sessions[0]["messages"]:
            role = msg["role"].upper()
            console.print(f"[{'blue' if role == 'USER' else 'green'}]{role}:[/] {msg['content']}\n")
    triggers = result.get("marketing_triggers", [])
    if triggers:
        console.print(f"[bold yellow]{len(triggers)} marketing trigger(s) detected.[/bold yellow]")


if __name__ == "__main__":
    main()
