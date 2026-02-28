"""CLI entrypoint: python -m bots.chatbot.run"""
from __future__ import annotations

import logging
import uuid

import click

from bots.chatbot.bot import ChatbotBot
from bots.chatbot.models import ChatbotInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@click.command()
@click.option("--message", required=True, help="User message to the chatbot")
@click.option("--session-id", default=None, help="Session ID for conversation continuity")
def main(message: str, session_id: str | None) -> None:
    """Run the Restaurant Chatbot (single turn)."""
    chatbot_input = ChatbotInput(
        session_id=session_id or str(uuid.uuid4()),
        message=message,
    )
    bot = ChatbotBot(chatbot_input=chatbot_input)
    result = bot.execute()
    click.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
