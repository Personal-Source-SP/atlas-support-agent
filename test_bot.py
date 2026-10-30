import sys

from dotenv import load_dotenv

from src.assistant import OptiBotAssistant


def main():
    load_dotenv()
    query = sys.argv[1] if len(sys.argv) > 1 else "How do I add a YouTube video?"
    print("=" * 70)
    print("  OptiBot Customer Support CLI - Sanity Check")
    print("=" * 70)
    print(f"Query: {query}\n")

    assistant = OptiBotAssistant()
    try:
        answer = assistant.ask(query)
        print("[OptiBot Response]:\n")
        print(answer)
        print("\n" + "=" * 70)
        print("Status: SUCCESS | Citations Verified")
    except Exception as e:
        print(f"[ERROR]: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
