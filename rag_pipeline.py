"""
HR Policy Assistant - RAG Pipeline Module
==========================================
Coordinates document retrieval from ChromaDB and answer generation
via Google Gemini LLM with strict grounding and citation requirements.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from vector_store import load_vector_store

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

RAG_PROMPT_TEMPLATE = """You are the official HR Policy Assistant for Enso Group. Your sole task is to answer employee HR policy questions strictly and accurately based ONLY on the provided manual excerpts below.

STRICT INSTRUCTIONS:
1. Use ONLY the facts directly mentioned in the provided Context. Do NOT use outside knowledge, general assumptions, or external information.
2. If the provided context does NOT contain enough information to fully support the answer, or if the question is about an external/unrelated topic, you must respond with EXACTLY and ONLY:
Not found.
Do not add any additional words, apologies, or explanations if not found.
3. If the answer IS supported by the context:
   - Answer clearly, accurately, and concisely.
   - Explicitly cite the source page number and policy section at the end of your answer in the following format:
     Source: [Policy Section / Title], Page [Page Number]

Context from HR Policy Manual:
================================
{context}
================================

Question: {question}

Answer:"""


class HRPolicyAssistant:
    def __init__(self, k: int = 4):
        """
        Initializes the ChromaDB retriever and Google Gemini LLM.
        """
        if not API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please add it to your .env file."
            )

        self.vector_store = load_vector_store()
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=API_KEY,
            temperature=0.0
        )
        self.prompt = PromptTemplate(
            template=RAG_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )

    def _format_context(self, docs) -> str:
        """
        Formats retrieved document chunks into structured context with page numbers.
        """
        formatted = []
        for d in docs:
            page = d.metadata.get("page", "Unknown")
            section = d.metadata.get("section", "General")
            formatted.append(f"[Section: {section} | Page {page}]\n{d.page_content.strip()}")
        return "\n\n---\n\n".join(formatted)

    def _extract_text(self, response: Any) -> str:
        """
        Safely extracts string content from LangChain / Gemini response.
        """
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        elif isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts).strip()
        return str(content).strip()

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Executes the RAG pipeline:
        1. Retrieves top-k relevant chunks from ChromaDB
        2. Constructs grounded prompt with context
        3. Generates grounded answer using Google Gemini
        4. Validates strict 'Not found.' requirement
        """
        docs = self.retriever.invoke(question)
        context_str = self._format_context(docs)

        prompt_val = self.prompt.format(context=context_str, question=question)
        raw_response = self.llm.invoke(prompt_val)
        answer = self._extract_text(raw_response)

        # Enforce exact requirement: If answer is not supported, return exactly 'Not found.'
        cleaned_lower = answer.lower().strip().rstrip(".")
        if cleaned_lower in ["not found", "not found in the manual", "not found in the hr manual", "not found."]:
            answer = "Not found."

        # Compile structured sources for transparency and Streamlit UI display
        sources = []
        for d in docs:
            sources.append({
                "page": d.metadata.get("page"),
                "section": d.metadata.get("section"),
                "content": d.page_content.strip()
            })

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }


if __name__ == "__main__":
    assistant = HRPolicyAssistant()
    
    test_queries = [
        "How many days of Privilege Leave (PL) does a permanent employee get per year?",
        "What is the probation period for employees up to Senior Manager?",
        "What is the current GST rate in India?"
    ]

    for q in test_queries:
        print(f"\nQ: {q}")
        res = assistant.ask(q)
        print(f"A:\n{res['answer']}")
