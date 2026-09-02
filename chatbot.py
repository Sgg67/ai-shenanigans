"""NFL chatbot: Gemini embeddings for retrieval, Ollama for generation."""
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from graph.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import sys

# Wikipedia text contains characters cp1252 cannot encode; force UTF-8 output on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

INDEX_NAME = os.environ.get("PINECONE_INDEX", "nfl")

llm = get_llm()

# Embeddings must match what ingestion.py wrote into the index.
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.environ["GEMINI_API_KEY"],
    output_dimensionality=1024,
)

vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
    pinecone_api_key=os.environ.get("PINECONE_API_KEY"),
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an NFL expert assistant. Answer using only the context below. "
     "If the context does not contain the answer, say you don't know.\n\nContext:\n{context}"),
    ("human", "{question}"),
])


def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    print("NFL chatbot ready. Ctrl-C to quit.\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q:
            print(f"\nBot: {chain.invoke(q)}\n")
