from typing import Any, Dict
from graph.chains.generation import generation_chain
from graph.state import GraphState
from graph.debug import debug

def generate(state: GraphState) -> Dict[str, Any]:
    debug("---Generate---")
    question = state["question"]
    documents = state["documents"]

    generation = generation_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}