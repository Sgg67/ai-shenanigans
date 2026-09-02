from typing import Any, Dict
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_tavily import TavilySearch
from graph.state import GraphState
from graph.debug import debug

load_dotenv()

web_search_tool = TavilySearch(max_results=3)


def web_search(state: GraphState) -> Dict[str, Any]:
    debug("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents") or []

    response = web_search_tool.invoke({"query": question})
    # TavilySearch returns {"results": [...]}; older versions returned a bare list.
    results = response.get("results", []) if isinstance(response, dict) else response
    joined = "\n".join(r["content"] for r in results)
    documents.append(Document(page_content=joined))

    return {"documents": documents, "question": question}


if __name__ == "__main__":
    print(web_search(state={"question": "who won the last Super Bowl", "documents": None}))
