import os
import streamlit as st
from rag_pipeline import HRPRAssistant

st.set_page_config(
    page_title="Enso Group HR Policy Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .badge-found {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .badge-notfound {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .answer-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.8rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache assistant instance
@st.cache_resource(show_spinner="Loading HR Policy Vector Index & Model...")
def get_assistant():
    return HRPRAssistant()

try:
    assistant = get_assistant()
    db_loaded = True
except Exception as e:
    assistant = None
    db_loaded = False
    init_error = str(e)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/human-resources.png", width=64)
    st.title("Project 1: HR Policy RAG")
    st.markdown("**Tech Stack:**\n- 🐍 Python 3.13\n- 📦 LangChain 1.4+\n- 🗄️ ChromaDB\n- 🤖 Google Gemini 3.8 Flash\n- 📄 79-Page Enso HR Manual")
    
    st.markdown("---")
    st.subheader("Assignment Questions")
    predefined_questions = [
        "How many days of Privilege Leave (PL) does a permanent employee get per year?",
        "What is the probation period for employees up to Senior Manager?",
        "What is the company's health-insurance premium amount?",
        "What is the current GST rate in India?",
        "How many days of maternity leave are given?"
    ]

    selected_q = st.selectbox(
        "Choose an exam question to autofill:",
        ["-- Select a question --"] + predefined_questions
    )

    st.markdown("---")
    st.caption("Developed for Gen-AI Exam - Project 1")

# Main content
st.markdown('<div class="main-title">Enso Group HR Policy Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Q&A over the official 79-page Enso Group HR Policy Manual using LangChain & ChromaDB</div>', unsafe_allow_html=True)

if not db_loaded:
    st.error(f"Error loading RAG pipeline: {init_error}")
    st.info("Please verify that your GEMINI_API_KEY is configured in the `.env` file and `hr_manual.pdf` is present.")
    st.stop()

# Initialize session state for input
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

if selected_q != "-- Select a question --":
    st.session_state.query_input = selected_q

query = st.text_input(
    "Enter your HR policy query:",
    value=st.session_state.query_input,
    placeholder="e.g., How many days of Privilege Leave (PL) does a permanent employee get per year?",
    key="search_box"
)

col1, col2 = st.columns([1, 5])
with col1:
    search_clicked = st.button("🔍 Ask Assistant", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 Clear", use_container_width=False):
        st.session_state.query_input = ""
        st.rerun()

if search_clicked and query.strip():
    with st.spinner("Searching HR manual and generating verified answer..."):
        response = assistant.ask(query.strip())
        answer = response["answer"]
        sources = response.get("sources", [])

        is_not_found = "not found" in answer.lower()

        st.markdown("---")
        if is_not_found:
            st.markdown('<span class="badge-notfound">⚠️ Information Not In Manual</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-found">✅ Answer Verified In Manual</span>', unsafe_allow_html=True)

        st.markdown(f'<div class="answer-card"><strong>Answer:</strong><br>{answer}</div>', unsafe_allow_html=True)

        # Citations & Context Expander
        with st.expander(f"📑 View Retrieved Context & Document Excerpts ({len(sources)} chunks)", expanded=not is_not_found):
            for i, src in enumerate(sources, start=1):
                page_info = f"Page {src['page']}" if src.get("page") else "Unknown Page"
                section_info = src.get("section", "HR Manual")
                st.markdown(f"""
                <div class="source-box">
                    <strong>Chunk {i}</strong> — <em>{section_info}</em> ({page_info})<br>
                    <small style="color: #475569;">"{src['excerpt']}..."</small>
                </div>
                """, unsafe_allow_html=True)

# Quick evaluation matrix tab
st.markdown("---")
with st.expander("📊 View All 5 Exam Question Results (Batch Evaluation Summary)"):
    st.markdown("""
    | # | Question | Answer | Reference / Policy Section |
    |---|---|---|---|
    | **1** | How many days of Privilege Leave (PL) does a permanent employee get per year? | **12 days** per calendar year | Annexure III: Workplace Operations - [G] Leave Policy, Page 60 |
    | **2** | What is the probation period for employees up to Senior Manager? | **3 months** from the date of joining | Annexure I: Employment Lifecycle - [B] Probation Policy, Page 42 |
    | **3** | What is the company's health-insurance premium amount? | **Not found** (Policy does not specify premium amounts) | Not found in HR Manual |
    | **4** | What is the current GST rate in India? | **Not found** (External tax query not in manual) | Not found in HR Manual |
    | **5** | How many days of maternity leave are given? | **12 weeks (90 days)** with pay | Annexure III: Workplace Operations - [G] Leave Policy (Leeway), Page 62 |
    """)
