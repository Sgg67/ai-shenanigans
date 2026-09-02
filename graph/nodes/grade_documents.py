from typing import Any, Dict
from graph.state import GraphState
from graph.chains.retrieval_grader import retrieval_grader
from graph.debug import debug
def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines wether the retrieved are relevant to the question
    If any document is not relevant, we will set a flag to run web search
    
    Args:
        state (dict): The current graph state

    Returns:
        state(dict): Filtered out irrelevant documents and updated web_search state
    """
    debug("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            debug("---Grade: document relevant---")
            filtered_docs.append(d)
        else:
            debug("---Grade: document not relevant---")
            web_search = True
            continue
    return {"documents": filtered_docs, "question":question, "web_search":web_search}