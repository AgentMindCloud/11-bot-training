"""LLM client abstraction. Supports OpenAI chat completion."""
from __future__ import annotations

import logging
from typing import Any

import openai

from infra.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin wrapper around the OpenAI chat completions API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._client = openai.OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_model
        self.max_tokens = max_tokens or settings.openai_max_tokens

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Single-turn chat completion. Returns assistant message text."""
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def chat_with_history(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Multi-turn chat completion with full message history."""
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=temperature,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content or ""
