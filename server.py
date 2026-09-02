"""FastAPI backend for the BLITZ NFL chatbot UI."""
import sys
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graph.graph import app as graph_app
from graph.messages import GREETING_MESSAGE, clean_source_title
from graph.prerouter import is_greeting

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

api = FastAPI(title="BLITZ NFL Desk")


class AskRequest(BaseModel):
    question: str


class Source(BaseModel):
    title: str
    url: str


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    kind: str  # "greeting" | "refusal" | "answer" -- lets the UI style the reply


@api.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    question = (req.question or "").strip()

    result = graph_app.invoke({"question": question})
    answer = result.get("generation", "")

    # Deduplicate by URL -- the retriever often returns several chunks of one page.
    sources: List[Source] = []
    seen = set()
    for doc in result.get("documents") or []:
        url = doc.metadata.get("source", "")
        if url and url not in seen:
            seen.add(url)
            sources.append(Source(title=clean_source_title(doc.metadata.get("title", "")), url=url))

    if answer == GREETING_MESSAGE or is_greeting(question):
        kind = "greeting"
    elif "not in my provided documents" in answer:
        kind = "refusal"
        sources = []  # a refusal cites nothing
    else:
        kind = "answer"

    return AskResponse(answer=answer, sources=sources, kind=kind)


@api.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")


api.mount("/", StaticFiles(directory="static"), name="static")
