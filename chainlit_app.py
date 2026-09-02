"""Chainlit frontend for the BLITZ NFL chatbot.

Runs the same LangGraph self-corrective RAG pipeline used by server.py / main.py,
behind Chainlit's chat UI instead of the static HTML page or the CLI.
"""
import sys

import chainlit as cl
from dotenv import load_dotenv

from graph.graph import app as graph_app
from graph.messages import GREETING_MESSAGE, clean_source_title

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()


@cl.on_chat_start
async def on_chat_start() -> None:
    await cl.Message(content=GREETING_MESSAGE, author="BLITZ").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    question = (message.content or "").strip()
    if not question:
        return

    result = await graph_app.ainvoke({"question": question})
    answer = result.get("generation", "")

    # Deduplicate by URL -- the retriever often returns several chunks of one page.
    elements = []
    seen = set()
    for doc in result.get("documents") or []:
        url = doc.metadata.get("source", "")
        if url and url not in seen:
            seen.add(url)
            title = clean_source_title(doc.metadata.get("title", ""))
            elements.append(cl.Text(name=title, content=url, display="inline"))

    reply = cl.Message(content=answer, author="BLITZ")
    if elements and answer != GREETING_MESSAGE and "not in my provided documents" not in answer:
        reply.elements = elements
    await reply.send()
