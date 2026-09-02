"""Shared user-facing strings.

Lives outside graph.nodes / graph.chains so both can import it without a cycle.
"""

CAPABILITIES = (
    "NFL teams, players and coaches, the Super Bowl, game rules and scoring, "
    "positions, stadiums, the draft, the playoffs, records and history, and the "
    "Pro Football Hall of Fame"
)

GREETING_MESSAGE = (
    "Hi! I'm an NFL information chatbot. I can answer questions about "
    f"{CAPABILITIES}.\n\n"
    "Try asking something like \"Which team has won the most Super Bowls?\" or "
    "\"How many teams are in the NFL?\""
)

REFUSAL_MESSAGE = (
    "I can't answer that -- that information is not in my provided documents. "
    f"I'm an NFL chatbot, so I can help with {CAPABILITIES}."
)


def clean_source_title(raw: str) -> str:
    """Strip the ' - Wikipedia' suffix Wikipedia page titles carry as metadata."""
    return raw.replace(" - Wikipedia", "").strip() or "Source"
