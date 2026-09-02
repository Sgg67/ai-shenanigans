from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import hashlib
import os

load_dotenv()

INDEX_NAME = os.environ.get("PINECONE_INDEX", "nfl")
EMBED_DIM = 1024  # must match the Pinecone index dimension

urls = [
    "https://en.wikipedia.org/wiki/National_Football_League",
    "https://en.wikipedia.org/wiki/History_of_the_National_Football_League",
    "https://en.wikipedia.org/wiki/Super_Bowl",
    "https://en.wikipedia.org/wiki/List_of_Super_Bowl_champions",
    "https://en.wikipedia.org/wiki/American_football_rules",
    "https://en.wikipedia.org/wiki/American_football_positions",
    "https://en.wikipedia.org/wiki/List_of_current_National_Football_League_stadiums",
    "https://en.wikipedia.org/wiki/National_Football_League_Draft",
    "https://en.wikipedia.org/wiki/NFL_playoffs",
    "https://en.wikipedia.org/wiki/Pro_Football_Hall_of_Fame",
]

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.environ["GEMINI_API_KEY"],
    output_dimensionality=EMBED_DIM,
)

vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
    pinecone_api_key=os.environ.get("PINECONE_API_KEY"),
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


def ingest() -> None:
    """Load, split, embed and upsert the NFL corpus.

    Kept behind a function so `from ingestion import retriever` stays cheap --
    importing this module must not re-ingest the whole corpus.
    """
    # WebBaseLoader parses pages locally with BeautifulSoup (no Unstructured API key needed).
    loader = WebBaseLoader(urls, requests_per_second=2)
    loader.requests_kwargs = {"headers": {"User-Agent": "nfl-chatbot-ingestion/1.0"}}
    docs_list = loader.load()
    print(f"Loaded {len(docs_list)} documents")

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=30
    )
    doc_splits = text_splitter.split_documents(docs_list)
    print(f"Split into {len(doc_splits)} chunks")

    # Batched upserts stay under Pinecone's payload limit and give progress output.
    # Content-hash IDs make re-running idempotent instead of duplicating every chunk.
    BATCH = 100
    for i in range(0, len(doc_splits), BATCH):
        batch = doc_splits[i : i + BATCH]
        ids = [hashlib.sha256(d.page_content.encode("utf-8")).hexdigest() for d in batch]
        vectorstore.add_documents(batch, ids=ids)
        print(f"Upserted {i + len(batch)}/{len(doc_splits)}")


if __name__ == "__main__":
    ingest()

    hits = retriever.invoke("Which team has won the most Super Bowls?")
    print(f"\nRetrieval check -- {len(hits)} hits:")
    for h in hits:
        print(f"  [{h.metadata.get('title', '?')}] {h.page_content[:120]}...")
