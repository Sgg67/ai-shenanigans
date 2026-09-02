"""Unit tests for chainlit_app helpers that don't require a running LLM/Chainlit server."""
from chainlit_app import _clean_title


def test_clean_title_strips_wikipedia_suffix() -> None:
    assert _clean_title("Super Bowl - Wikipedia") == "Super Bowl"


def test_clean_title_falls_back_when_empty() -> None:
    assert _clean_title("") == "Source"
    assert _clean_title("   ") == "Source"


def test_clean_title_leaves_plain_titles_unchanged() -> None:
    assert _clean_title("National Football League") == "National Football League"
