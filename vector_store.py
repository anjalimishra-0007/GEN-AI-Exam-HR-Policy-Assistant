"""
HR Policy Assistant - ChromaDB Vector Store Module
===================================================
Provides utilities to load or query the ChromaDB vector store
using Google Gemini Embeddings.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
API_KEY = os.getenv("GEMINI_API_KEY")


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    """
    Returns GoogleGenerativeAIEmbeddings configured with the project settings.
    """
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=API_KEY
    )


def load_vector_store(persist_directory: str = CHROMA_DIR) -> Chroma:
    """
    Loads an existing Chroma vector store from disk.
    If it doesn't exist, alerts the user to run ingest.py first.
    """
    if not os.path.exists(persist_directory) or not os.listdir(persist_directory):
        raise FileNotFoundError(
            f"ChromaDB directory '{persist_directory}' is empty or does not exist. "
            "Please run 'python ingest.py' first to build the vector index."
        )

    embeddings = get_embedding_function()
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="hr_policy_docs"
    )
    return vector_store


if __name__ == "__main__":
    vs = load_vector_store()
    query = "How many days of Privilege Leave (PL) does a permanent employee get per year?"
    results = vs.similarity_search_with_relevance_scores(query, k=3)
    print(f"\nTop search results for: '{query}'")
    for doc, score in results:
        print(f"\n[Score: {score:.4f}] [Page: {doc.metadata.get('page')}] {doc.metadata.get('section')}")
        print(doc.page_content[:250].strip() + "...\n")
