import argparse
import sys
from rag_pipeline import HRPRAssistant

def main():
    parser = argparse.ArgumentParser(description="Enso Group HR Policy Assistant (RAG)")
    parser.add_argument("--query", "-q", type=str, help="Question to ask the HR assistant")
    args = parser.parse_args()

    assistant = HRPRAssistant()

    if args.query:
        result = assistant.ask(args.query)
        print(f"\nQuestion: {result['question']}")
        print(f"\nAnswer:\n{result['answer']}\n")
        return

    print("=" * 70)
    print("  Enso Group HR Policy Assistant - Interactive CLI")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 70)

    while True:
        try:
            q = input("\nEnter your HR query: ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            res = assistant.ask(q)
            print("\n" + "=" * 50)
            print(res["answer"])
            print("=" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
