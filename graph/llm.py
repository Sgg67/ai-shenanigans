"""Shared Ollama LLM factory for the graph.

Ollama Cloud models do not honor plain JSON-mode structured output -- they reply
in prose and parsing fails. They DO emit proper tool calls, so every structured
chain here uses method="function_calling" plus a system-prompt instruction to
call the tool. See TOOL_NOTE below.
"""
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

OLLAMA_KEY = os.environ.get("OLLAMA_API")
CLOUD_URL = "https://ollama.com"
LOCAL_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Cloud is the default; set OLLAMA_LOCAL=1 to run everything against local Ollama.
USE_LOCAL = os.environ.get("OLLAMA_LOCAL") == "1" or not OLLAMA_KEY

CLOUD_MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b")
LOCAL_MODEL = os.environ.get("OLLAMA_LOCAL_MODEL", "llama3.2:latest")

# Appended to the system prompt of every structured chain.
TOOL_NOTE = " You must respond by calling the provided tool."


def get_llm(temperature: float = 0) -> ChatOllama:
    """Return a ChatOllama pointed at Ollama Cloud, or local if configured."""
    if USE_LOCAL:
        return ChatOllama(model=LOCAL_MODEL, base_url=LOCAL_URL, temperature=temperature)
    return ChatOllama(
        model=CLOUD_MODEL,
        base_url=CLOUD_URL,
        client_kwargs={"headers": {"Authorization": f"Bearer {OLLAMA_KEY}"}},
        temperature=temperature,
        reasoning=False,  # gpt-oss emits thinking tokens that pollute tool-call parsing
    )


def structured(schema, temperature: float = 0):
    """LLM constrained to `schema` via tool calling (the reliable path on Ollama)."""
    return get_llm(temperature).with_structured_output(schema, method="function_calling")
