"""
haic.py: the one file you need to call an AI model in a HAIC project.

Usage:
    from haic import ask

    print(ask("What are the core courses in MS-AIM?"))            # GPT-6 Luna (default)
    print(ask("Summarize this policy...", model="haiku"))        # Claude Haiku 5.5

Setup (once):
    1. pip install -r requirements.txt
    2. Copy .env.example to .env
    3. Paste your project's HAIC key into .env (ask your project lead; never commit it)

Rules:
    * Only two models are allowed: "luna" (GPT-6 Luna) and "haiku" (Claude Haiku 5.5).
      Any other model is blocked by the club account.
    * Your project has a spending cap. When it is reached, calls fail until the next month.
    * Reasoning effort defaults to "low" because higher effort costs much more.
      Raise it only when a task truly needs it.
    * Never put an API key in code, notebooks, screenshots, or chat. It lives only in .env.
"""

from __future__ import annotations

import os
import warnings
from typing import Any

from openai import OpenAI

try:  # python-dotenv is optional; without it, set environment variables yourself.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BASE_URL = "https://openrouter.ai/api/v1"

# Short names members use -> OpenRouter model IDs.
# Defaults can be overridden in .env if OpenRouter renames a model.
MODELS: dict[str, str] = {
    "luna": os.getenv("HAIC_MODEL_LUNA", "openai/gpt-6-luna"),
    "haiku": os.getenv("HAIC_MODEL_HAIKU", "anthropic/claude-haiku-5.5"),
}

DEFAULT_MODEL = "luna"
DEFAULT_EFFORT = "low"  # one of: "none", "low", "medium", "high", "xhigh", "max" ("none" works for both Luna and Haiku)

# Claude Haiku 5.5 costs about 5x more per token on prompts over 100,000 tokens.
# Roughly 4 characters per token; warn well before that point.
_HAIKU_LONG_PROMPT_CHARS = 300_000

_client: OpenAI | None = None


class HAICConfigError(RuntimeError):
    """Raised when the key or model name is missing or not allowed."""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("HAIC_API_KEY")
        if not key:
            raise HAICConfigError(
                "HAIC_API_KEY is not set. Copy .env.example to .env and paste your "
                "project's key (ask your project lead)."
            )
        _client = OpenAI(base_url=BASE_URL, api_key=key)
    return _client


def _resolve_model(model: str) -> str:
    if model not in MODELS:
        allowed = ", ".join(sorted(MODELS))
        raise HAICConfigError(f"Unknown model '{model}'. Use one of: {allowed}.")
    return MODELS[model]


def _check_length(model: str, messages: list[dict[str, Any]]) -> None:
    if model != "haiku":
        return
    total = sum(len(str(m.get("content", ""))) for m in messages)
    if total > _HAIKU_LONG_PROMPT_CHARS:
        warnings.warn(
            "This prompt is very long. Claude Haiku 5.5 charges about 5x more on prompts "
            "over 100,000 tokens. Send less context (fewer or shorter documents).",
            stacklevel=3,
        )


def chat(
    messages: list[dict[str, Any]],
    model: str = DEFAULT_MODEL,
    *,
    effort: str | None = DEFAULT_EFFORT,
    max_tokens: int = 1024,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | dict[str, Any] | None = None,
    temperature: float | None = None,
    **kwargs: Any,
):
    """
    Full chat call. Returns the raw response object.

    Use this when you need the whole conversation, tool calling, or token usage
    (response.usage). For a simple question and answer, use ask().
    """
    model_id = _resolve_model(model)
    _check_length(model, messages)

    request: dict[str, Any] = {
        "model": model_id,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if tools is not None:
        request["tools"] = tools
    if tool_choice is not None:
        request["tool_choice"] = tool_choice
    if temperature is not None:
        request["temperature"] = temperature

    extra_body = dict(kwargs.pop("extra_body", {}) or {})
    if effort is not None:
        extra_body["reasoning"] = {"effort": effort}
    if extra_body:
        request["extra_body"] = extra_body

    request.update(kwargs)
    return _get_client().chat.completions.create(**request)


def ask(
    prompt: str,
    model: str = DEFAULT_MODEL,
    *,
    system: str | None = None,
    effort: str | None = DEFAULT_EFFORT,
    max_tokens: int = 1024,
    **kwargs: Any,
) -> str:
    """Ask one question and get the answer text back."""
    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = chat(messages, model, effort=effort, max_tokens=max_tokens, **kwargs)
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    # Quick connection test: python haic.py
    print(ask("Reply with exactly: HAIC connection OK", effort="low", max_tokens=20))
