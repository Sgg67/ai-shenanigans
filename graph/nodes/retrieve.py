from typing import Any, Dict
from graph.state import GraphState
from ingestion import retriever
from graph.debug import debug

def retrieve(state: GraphState) -> Dict[str, Any]:
    debug("---RETRIEVE---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents" : documents, "question": question}
    
