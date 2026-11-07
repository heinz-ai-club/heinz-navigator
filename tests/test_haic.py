"""Tests for haic.py with the OpenAI client mocked. No real AI calls."""

from unittest.mock import MagicMock

import pytest

import haic


@pytest.fixture
def fake_client(monkeypatch):
    client = MagicMock()
    client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="hello"))
    ]
    monkeypatch.setattr(haic, "_get_client", lambda: client)
    return client


def test_ask_sends_model_and_low_effort(fake_client):
    assert haic.ask("hi") == "hello"
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == haic.MODELS["luna"]
    assert kwargs["extra_body"] == {"reasoning": {"effort": "low"}}


def test_haiku_uses_haiku_model_id(fake_client):
    haic.ask("hi", model="haiku")
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == haic.MODELS["haiku"]


def test_default_model_ids():
    assert haic.MODELS["luna"] == "openai/gpt-6-luna"
    assert haic.MODELS["haiku"] == "anthropic/claude-haiku-5.5"


def test_unknown_model_raises(fake_client):
    with pytest.raises(haic.HAICConfigError):
        haic.ask("hi", model="gpt-4")


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("HAIC_API_KEY", raising=False)
    monkeypatch.setattr(haic, "_client", None)
    with pytest.raises(haic.HAICConfigError):
        haic.ask("hi")
