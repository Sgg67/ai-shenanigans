from typing import Any, Dict

from graph.messages import GREETING_MESSAGE
from graph.state import GraphState
from graph.debug import debug


def greet(state: GraphState) -> Dict[str, Any]:
    """Terminal node for greetings and 'what can you do' questions.

    Like refuse(), this returns a fixed string with no LLM call -- it is both
    instant and immune to anything embedded in the user's message.
    """
    debug("---GREET---")
    return {
        "documents": [],
        "question": state["question"],
        "generation": GREETING_MESSAGE,
    }
