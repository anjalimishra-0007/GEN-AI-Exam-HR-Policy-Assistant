import os
from typing import List
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf_with_metadata(pdf_path: str = "hr_manual.pdf") -> List[Document]:
    """
    Extracts text from each page of the HR manual PDF and attaches
    structured metadata including page numbers and detected sections.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    reader = PdfReader(pdf_path)
    documents = []

    # Map of key sections by page ranges in the Enso Group HR Manual
    # Derived from document Table of Contents & page headers
    def infer_section(page_num: int, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        header = " | ".join(lines[:3]) if lines else ""

        if 5 <= page_num <= 15:
            return f"Section 1: Employing Staff (Standards of Business Conduct / IT & Email Policy) - Page {page_num}"
        elif 16 <= page_num <= 21:
            return f"Section 2: Managing Employee Performance (Appraisal, Absence & Disciplinary) - Page {page_num}"
        elif 22 <= page_num <= 27:
            return f"Section 3: Dealing with Employee Concerns (Grievance, Anti-Bullying, Whistleblowing) - Page {page_num}"
        elif 28 <= page_num <= 33:
            return f"Section 4: Supporting Our Staff (Equality, Drug & Alcohol, Health & Safety) - Page {page_num}"
        elif 34 <= page_num <= 38:
            return f"Company Rules & Regulations (Conduct, Assets, Outside Employment) - Page {page_num}"
        elif 39 <= page_num <= 47:
            return f"Annexure I: Employment Lifecycle (Onboarding, Probation, Training, Relocation, Offboarding) - Page {page_num}"
        elif 48 <= page_num <= 51:
            return f"Annexure II: Employee Recognition & Communications Policy - Page {page_num}"
        elif 52 <= page_num <= 65:
            return f"Annexure III: Workplace Operations (Dress Code, Timings, Compensation, Leave Policy, Anti-Harassment) - Page {page_num}"
        elif 66 <= page_num <= 79:
            return f"Annexure IV: Travel Policies (Long Distance & Short Distance Travel) - Page {page_num}"
        else:
            return f"Enso Group HR Manual - Page {page_num}"

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        page_text = page.extract_text() or ""
        page_text = page_text.strip()
        if not page_text:
            continue

        section_name = infer_section(page_num, page_text)

        doc = Document(
            page_content=page_text,
            metadata={
                "source": os.path.basename(pdf_path),
                "page": page_num,
                "section": section_name
            }
        )
        documents.append(doc)

    return documents

def get_text_chunks(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 150) -> List[Document]:
    """
    Splits documents into overlapping chunks while preserving page & section metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

if __name__ == "__main__":
    docs = load_pdf_with_metadata("hr_manual.pdf")
    print(f"Loaded {len(docs)} pages from hr_manual.pdf")
    chunks = get_text_chunks(docs)
    print(f"Generated {len(chunks)} text chunks.")
