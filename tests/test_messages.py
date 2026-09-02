"""Unit tests for shared user-facing strings. No network access required."""
from graph.messages import CAPABILITIES, GREETING_MESSAGE, REFUSAL_MESSAGE


def test_greeting_message_mentions_capabilities() -> None:
    assert CAPABILITIES in GREETING_MESSAGE


def test_greeting_message_is_nonempty_string() -> None:
    assert isinstance(GREETING_MESSAGE, str) and GREETING_MESSAGE.strip()


def test_refusal_message_is_nonempty_string() -> None:
    assert isinstance(REFUSAL_MESSAGE, str) and REFUSAL_MESSAGE.strip()


def test_refusal_message_does_not_leak_instructions() -> None:
    lowered = REFUSAL_MESSAGE.lower()
    assert "system prompt" not in lowered
    assert "these rules" not in lowered
