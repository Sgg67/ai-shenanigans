# BLITZ NFL Desk

**Live app:** https://ai-shenanigans.onrender.com

A self-corrective RAG chatbot that answers questions about the NFL. Built with
[LangGraph](https://github.com/langchain-ai/langgraph), [Pinecone](https://www.pinecone.io/)
for vector search, Google Gemini for embeddings, and Ollama (cloud or local) for generation.

The corpus is a set of NFL-related Wikipedia pages (`ingestion.py`). Questions are routed,
retrieved against, and answered through a small graph (`graph/graph.py`):

- Greetings and "what can you do" questions are answered instantly, with no LLM call.
- Clearly NFL-flavored questions skip straight to retrieval.
- Anything ambiguous goes through an LLM router, which also acts as the first line of
  defense against prompt injection.
- Off-topic questions and injection attempts get a fixed refusal string -- never the LLM's
  own words -- so nothing in a malicious prompt can leak into a reply.

## Interfaces

The same graph is exposed three ways:

| Interface | File | Use |
|---|---|---|
| Chainlit chat UI | `chainlit_app.py` | Primary web frontend (see below) |
| FastAPI + static HTML | `server.py`, `static/` | Lightweight JSON API + hand-rolled UI |
| CLI | `main.py` / `chatbot.py` | Terminal chat loop |

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=...
PINECONE_INDEX=nfl
GEMINI_API_KEY=...
OLLAMA_API=...                 # Ollama Cloud key; omit + set OLLAMA_LOCAL=1 to use a local Ollama instead
TAVILY_API_KEY=...             # optional, used by graph/nodes/web_search.py
```

Ingest the corpus into Pinecone once, before first use:

```bash
python ingestion.py
```

## Running the Chainlit UI locally

```bash
chainlit run chainlit_app.py -w
```

This opens the chat UI at `http://localhost:8000`. Answers include the source Wikipedia
pages as inline reference chips.

## Running the other interfaces

```bash
python main.py           # CLI chat loop
uvicorn server:api        # FastAPI + static HTML frontend, http://localhost:8000
```

## Tests

Fast, network-free unit tests live in `tests/` and run in CI on every push/PR:

```bash
pytest tests/ -v -m "not integration"
```

`graph/chains/tests/test_chains.py` contains integration tests that call live Pinecone,
Gemini, and Ollama APIs. They require real credentials in `.env` and are excluded from CI
by default (marked `integration`):

```bash
pytest graph/chains/tests/ -v -m integration
```

## CI

`.github/workflows/ci.yml` installs dependencies and runs the unit test suite (Python 3.11
and 3.13) on every push and pull request to `main`.

## Deployment

Chainlit is a stateful app served over WebSockets, which doesn't fit Vercel's stateless
serverless function model well (no persistent connections, cold starts interrupt
sessions). Instead this app deploys to **[Render](https://render.com)**, which runs it as
a long-lived web service:

1. Push this repo to GitHub.
2. In Render, create a new **Web Service** from the repo (or run `render blueprint launch`
   with the included [`render.yaml`](render.yaml)).
3. Set the environment variables listed in `render.yaml` (`PINECONE_API_KEY`,
   `GEMINI_API_KEY`, `OLLAMA_API`, etc.) in the Render dashboard -- they are marked
   `sync: false` so they must be entered manually rather than committed.
4. Render builds with `pip install -r requirements.txt` and starts the service with:

   ```bash
   chainlit run chainlit_app.py --host 0.0.0.0 --port $PORT --headless
   ```

Every push to `main` that passes CI can then be auto-deployed by Render's GitHub
integration.

## Project layout

```
chainlit_app.py       Chainlit chat UI (primary frontend)
server.py             FastAPI JSON API + static HTML frontend
main.py / chatbot.py  CLI interfaces
ingestion.py          Loads, chunks, embeds and upserts the NFL corpus into Pinecone
graph/                LangGraph nodes, chains, routing, and shared state
tests/                Fast unit tests (no network calls) -- run in CI
graph/chains/tests/   Integration tests against live Pinecone/Gemini/Ollama
render.yaml           Render deployment blueprint
.github/workflows/    CI pipeline
```
