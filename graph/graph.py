from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from graph.chains.router import RouteQuery, question_router
from graph.consts import GENERATE, GREET, REFUSE, RETRIEVE
from graph.nodes import generate, greet, refuse, retrieve
from graph.prerouter import is_clearly_nfl, is_greeting
from graph.state import GraphState
from graph.debug import debug

load_dotenv()


def route_question(state: GraphState) -> str:
    """Decide where a question goes, using as few LLM calls as possible.

    Greetings and clearly-NFL questions are classified with string matching (0 calls);
    only ambiguous input pays for the LLM router (~0.7s). Anything that fails to
    classify refuses -- this function must never fall through to None.
    """
    question = state["question"]

    if is_greeting(question):
        debug("---ROUTE: greeting (no LLM call)---")
        return GREET

    if is_clearly_nfl(question):
        debug("---ROUTE: NFL (no LLM call)---")
        return RETRIEVE

    debug("---ROUTE: asking LLM router---")
    try:
        source: RouteQuery = question_router.invoke({"question": question})
    except Exception as exc:
        # Refusing is the safe default for anything we can't classify.
        debug(f"---ROUTER FAILED ({type(exc).__name__}), refusing---")
        return REFUSE

    if source.datasource == "vectorstore":
        debug("---ROUTE: vectorstore---")
        return RETRIEVE

    debug("---ROUTE: refuse---")
    return REFUSE


workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GENERATE, generate)
workflow.add_node(REFUSE, refuse)
workflow.add_node(GREET, greet)

workflow.set_conditional_entry_point(
    route_question,
    {
        GREET: GREET,
        REFUSE: REFUSE,
        RETRIEVE: RETRIEVE,
    },
)

# Fast path: retrieve -> generate, with no grading round-trips in between.
# The hardened generation prompt is what keeps answers grounded: it is instructed
# to refuse when the retrieved context doesn't contain the answer.
workflow.add_edge(RETRIEVE, GENERATE)
workflow.add_edge(GENERATE, END)
workflow.add_edge(REFUSE, END)
workflow.add_edge(GREET, END)

app = workflow.compile()

if __name__ == "__main__":
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    print("Wrote graph.png")
