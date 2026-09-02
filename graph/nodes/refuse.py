from typing import Any, Dict

from graph.messages import REFUSAL_MESSAGE
from graph.state import GraphState
from graph.debug import debug


def refuse(state: GraphState) -> Dict[str, Any]:
    """Terminal node for off-topic questions and prompt-injection attempts.

    Returns a fixed string rather than calling the LLM, so nothing in the user's
    message can influence the reply.
    """
    debug("---REFUSE (off-topic or unsafe)---")
    return {
        "documents": [],
        "question": state["question"],
        "generation": REFUSAL_MESSAGE,
    }
