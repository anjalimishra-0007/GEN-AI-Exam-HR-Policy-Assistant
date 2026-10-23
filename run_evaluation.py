import json
import time
from rag_pipeline import HRPRAssistant

QUESTIONS = [
    "How many days of Privilege Leave (PL) does a permanent employee get per year?",
    "What is the probation period for employees up to Senior Manager?",
    "What is the company's health-insurance premium amount?",
    "What is the current GST rate in India?",
    "How many days of maternity leave are given?"
]

def main():
    print("=" * 80)
    print("  ENSO GROUP HR POLICY ASSISTANT - EXAM EVALUATION (PROJECT 1)")
    print("=" * 80)

    assistant = HRPRAssistant()
    results = []

    for idx, q in enumerate(QUESTIONS, start=1):
        print(f"\n--- [Question {idx}] {q} ---")
        res = assistant.ask(q)
        ans = res["answer"]
        print(f"Answer:\n{ans}\n")
        results.append({
            "question_number": idx,
            "question": q,
            "answer": ans,
            "sources": res["sources"][:2]
        })
        time.sleep(1.0)

    # Save output to JSON for documentation and evaluation
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("[SUCCESS] All 5 evaluation questions processed and saved to evaluation_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
