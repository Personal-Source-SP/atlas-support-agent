import argparse
import os
import sys
import time

from dotenv import load_dotenv

from src.assistant import OptiBotAssistant


def parse_cli_args(args=None):
    parser = argparse.ArgumentParser(
        description="OptiBot CLI Interactive Runner & Citation Inspector",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "positional_query",
        nargs="?",
        default=None,
        help="Optional positional question to ask OptiBot",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default="How do I add a YouTube video?",
        help="Question to ask OptiBot",
    )
    parser.add_argument(
        "--top-k",
        "-k",
        type=int,
        default=3,
        help="Number of chunks to retrieve",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display detailed context chunks and similarity scores",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start an interactive multi-turn terminal session",
    )
    parsed = parser.parse_args(args)
    if parsed.positional_query:
        parsed.query = parsed.positional_query
    return parsed


def format_terminal_box(title: str, content: str, width: int = 80) -> str:
    border = "+" + "-" * (width - 2) + "+"
    lines = [border, f"|  {title.ljust(width - 5)}|", border]
    for paragraph in content.splitlines():
        if not paragraph.strip():
            lines.append(f"|{' ' * (width - 2)}|")
            continue
        while len(paragraph) > (width - 4):
            lines.append(f"|  {paragraph[: width - 4].ljust(width - 4)}|")
            paragraph = paragraph[width - 4 :]
        lines.append(f"|  {paragraph.ljust(width - 4)}|")
    lines.append(border)
    return "\n".join(lines)


def execute_query(assistant: OptiBotAssistant, query: str, top_k: int, verbose: bool):
    start_time = time.time()
    if verbose:
        print("\n[INFO] Retrieving top chunks from Vector Store...")
        matches = assistant.vector_store.query(query, top_k=top_k)
        for idx, m in enumerate(matches, 1):
            meta = m.get("metadata", {})
            print(f"  Chunk {idx}: Article {meta.get('article_id')} | Title: {meta.get('title')}")
            print(f"  Source URL: {meta.get('url')}")
            preview = m["text"][:120].replace("\n", " ")
            print(f"  Snippet: {preview}...\n")

    answer = assistant.ask(query)
    latency = time.time() - start_time

    header = f"OptiBot Support Assistant (Latency: {latency:.2f}s)"
    print("\n" + format_terminal_box(header, f"Question: {query}\n\n[Response]:\n{answer}"))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("\n[ERROR] GEMINI_API_KEY / API_KEY is missing from environment.")
        print("Please copy .env.sample to .env and set your Gemini API key:")
        print("  cp .env.sample .env\n")
        sys.exit(1)

    args = parse_cli_args(sys.argv[1:])
    try:
        assistant = OptiBotAssistant(api_key=api_key)
        if args.interactive:
            print("\n" + "=" * 65)
            print("  OptiBot Interactive Terminal Session (Type 'exit' to quit)")
            print("=" * 65)
            while True:
                try:
                    user_input = input("\noptibot> ").strip()
                    if not user_input:
                        continue
                    if user_input.lower() in ("exit", "quit", "q"):
                        print("Exiting OptiBot session. Goodbye!")
                        break
                    execute_query(assistant, user_input, args.top_k, args.verbose)
                except (KeyboardInterrupt, EOFError):
                    print("\nSession interrupted. Exiting.")
                    break
        else:
            execute_query(assistant, args.query, args.top_k, args.verbose)
    except Exception as e:
        print(f"\n[EXECUTION ERROR]: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
