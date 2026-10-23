"""
HR Policy Assistant - Document Ingestion Script
================================================
This script extracts text from 'hr_manual.pdf', splits it into semantic chunks
with preserved page numbers and section metadata, generates embeddings,
and stores them in a ChromaDB vector database.
"""

import os
import sys
from dotenv import load_dotenv
from vector_store import build_or_load_vector_store

load_dotenv()

PDF_PATH = "hr_manual.pdf"
CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

def main():
    print("=" * 70)
    print("  HR Policy Assistant - Document Ingestion & ChromaDB Indexing")
    print("=" * 70)

    if not os.path.exists(PDF_PATH):
        print(f"[ERROR] Cannot find '{PDF_PATH}' in current directory.")
        sys.exit(1)

    print(f"[1/2] Ingesting '{PDF_PATH}' into ChromaDB at '{CHROMA_DIR}'...")
    vs = build_or_load_vector_store(pdf_path=PDF_PATH, persist_directory=CHROMA_DIR, force_rebuild=True)
    
    count = vs._collection.count()
    print(f"[2/2] Ingestion complete! Successfully indexed {count} document chunks.")
    print("\nYou can now launch the web app with: streamlit run app.py")
    print("Or run the automated evaluation: python run_evaluation.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
