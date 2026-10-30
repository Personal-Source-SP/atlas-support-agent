import os
import sys

from dotenv import load_dotenv

from src.delta import DeltaTracker
from src.scraper import fetch_zendesk_articles
from src.vector_store import VectorStoreManager


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[WARNING] GEMINI_API_KEY is not set. Embedding step will be skipped or mock-tested.")

    print("=== Step 1: Ingesting Zendesk Articles (support.optisigns.com) ===")
    articles = fetch_zendesk_articles(min_count=30, docs_dir="docs")
    print(f"Total articles fetched: {len(articles)}")

    print("=== Step 2: Checking Delta via SQLite ===")
    tracker = DeltaTracker(db_path="sync_state.db")
    delta = tracker.classify_articles(articles)

    added_count = len(delta["added"])
    updated_count = len(delta["updated"])
    skipped_count = len(delta["skipped"])
    print(
        f"Delta Result: [Added: {added_count}] | "
        f"[Updated: {updated_count}] | [Skipped: {skipped_count}]"
    )
    tracker.record_history(added_count, updated_count, skipped_count)

    need_index = delta["added"] + delta["updated"]
    if need_index:
        print(f"=== Step 3: Embedding {len(need_index)} New/Updated Articles via Gemini API ===")
        if api_key:
            v_mgr = VectorStoreManager(persist_dir="chroma_db", api_key=api_key)
            stats = v_mgr.index_articles(need_index)
            print(f"Embedded successfully: {stats['files']} files, {stats['chunks']} chunks.")
        else:
            print("[SKIPPED] Cannot embed without GEMINI_API_KEY.")
    else:
        print("=== Step 3: Knowledge Base is up-to-date. Zero delta to embed. ===")

    print("\n[SUCCESS] Daily Sync Completed.")
    print(f"Summary: added={added_count}, updated={updated_count}, skipped={skipped_count}")
    sys.exit(0)


if __name__ == "__main__":
    main()
