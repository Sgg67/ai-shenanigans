"""Opt-in trace logging for the graph.

Node/routing traces are noise during normal chat, so they are silent by default.
Set GRAPH_DEBUG=1 to print them when troubleshooting.
"""
import os

DEBUG = os.environ.get("GRAPH_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def debug(message: str) -> None:
    if DEBUG:
        print(message)
