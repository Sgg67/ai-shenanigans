"""NFL chatbot -- self-corrective RAG over the Pinecone NFL corpus."""
import sys

from dotenv import load_dotenv

from graph.graph import app

# Wikipedia text contains characters cp1252 cannot encode; force UTF-8 on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

if __name__ == "__main__":
    print("NFL chatbot ready. Ctrl-C to quit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question:
            result = app.invoke({"question": question})
            print(f"\nBot: {result['generation']}\n")
