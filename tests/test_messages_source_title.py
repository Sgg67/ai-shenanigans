"""Unit tests for source-title cleanup shared by chainlit_app and server."""
from graph.messages import clean_source_title


def test_clean_title_strips_wikipedia_suffix() -> None:
    assert clean_source_title("Super Bowl - Wikipedia") == "Super Bowl"


def test_clean_title_falls_back_when_empty() -> None:
    assert clean_source_title("") == "Source"
    assert clean_source_title("   ") == "Source"


def test_clean_title_leaves_plain_titles_unchanged() -> None:
    assert clean_source_title("National Football League") == "National Football League"
