"""LLM client wrapping OpenAI."""
from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel

from common.config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin wrapper around the OpenAI client."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.openai_api_key
        self._default_model = model or settings.openai_model
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import openai

                self._client = openai.OpenAI(api_key=self._api_key)
            except ImportError as exc:
                raise RuntimeError("openai package is required") from exc
        return self._client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat_completion(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Return the assistant's text reply."""
        client = self._get_client()
        used_model = model or self._default_model
        try:
            response = client.chat.completions.create(
                model=used_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("chat_completion failed: %s", exc)
            raise

    def structured_completion(
        self,
        messages: list[dict],
        response_format: type[BaseModel],
        model: str | None = None,
    ) -> BaseModel:
        """Return a parsed Pydantic model from the LLM response.

        Tries OpenAI's beta structured-output endpoint first; falls back to
        asking for JSON in the prompt and parsing manually.
        """
        client = self._get_client()
        used_model = model or self._default_model

        # Attempt 1: openai.beta.chat.completions.parse (SDK >= 1.40)
        try:
            response = client.beta.chat.completions.parse(
                model=used_model,
                messages=messages,
                response_format=response_format,
            )
            parsed = response.choices[0].message.parsed
            if parsed is not None:
                return parsed
        except Exception as exc:
            logger.debug("structured_completion (beta.parse) failed: %s – falling back", exc)

        # Attempt 2: JSON mode + manual parsing
        json_messages = list(messages) + [
            {
                "role": "system",
                "content": (
                    "Respond with valid JSON only that matches the requested schema. "
                    "Do not include markdown fences or extra text."
                ),
            }
        ]
        try:
            raw = self.chat_completion(json_messages, model=used_model, temperature=0.2)
            # Strip possible ```json fences
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1]
                raw = raw.rsplit("```", 1)[0]
            data = json.loads(raw)
            return response_format.model_validate(data)
        except Exception as exc:
            logger.error("structured_completion fallback failed: %s", exc)
            raise
