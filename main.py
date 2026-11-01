import json
import os
import sys
from datetime import UTC, datetime

from dotenv import load_dotenv

from src.delta import DeltaTracker
from src.scraper import fetch_zendesk_articles
from src.vector_store import VectorStoreManager


def generate_reports(report_data: dict, report_dir: str = "reports") -> None:
    os.makedirs(report_dir, exist_ok=True)

    # 1. Export JSON artifact
    json_path = os.path.join(report_dir, "daily_sync_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # 2. Export Markdown report
    md_path = os.path.join(report_dir, "daily_sync_report.md")
    total = report_data["total_fetched"]
    added = report_data["added_count"]
    updated = report_data["updated_count"]
    skipped = report_data["skipped_count"]
    chunks = report_data["embedded_chunks"]

    md_content = f"""# 📊 OptiBot Daily Ingestion & Delta Sync Report

- **Execution Timestamp**: `{report_data["timestamp"]}`
- **Source Endpoint**: `https://support.optisigns.com` (Zendesk API v2)
- **Status**: **{report_data["status"]}**

## 📈 Summary Metrics

| Metric | Count | Description |
| :--- | :---: | :--- |
| **Total Articles** | **{total}** | Total articles scraped and validated from Help Center |
| **Added (New)** | **{added}** | New articles ingested and embedded into Vector Store |
| **Updated** | **{updated}** | Existing articles with modified SHA-256 hash |
| **Skipped** | **{skipped}** | Articles with identical content hashes (delta optimization) |
| **Embedded Chunks** | **{chunks}** | Total vector chunks embedded via Gemini API |

## ⚙️ Operational Details
- **Embedding Model**: Google Gemini `text-embedding-004` (768 dimensions)
- **Vector Database**: ChromaDB (Cosine Distance Indexing)
- **Delta Tracking**: SQLite (`sync_state.db`) with SHA-256 Content Hashing
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 3. Publish to GitHub Actions Step Summary if running in CI/CD
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path and os.path.exists(os.path.dirname(summary_path)):
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(md_content + "\n")
        except Exception as e:
            print(f"[WARNING] Could not write to GITHUB_STEP_SUMMARY: {e}")


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("[WARNING] GEMINI_API_KEY is not set. Embedding will be skipped or mock-tested.")

    print("=== Step 1: Ingesting Zendesk Articles (support.optisigns.com) ===")
    articles = fetch_zendesk_articles(min_count=30, docs_dir="docs")
    total_fetched = len(articles)
    print(f"Total articles fetched: {total_fetched}")

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
    embedded_chunks = 0
    if need_index:
        print(f"=== Step 3: Embedding {len(need_index)} New/Updated Articles via Gemini API ===")
        if api_key:
            v_mgr = VectorStoreManager(persist_dir="chroma_db", api_key=api_key)
            stats = v_mgr.index_articles(need_index)
            embedded_chunks = stats["chunks"]
            print(f"Embedded successfully: {stats['files']} files, {embedded_chunks} chunks.")
        else:
            print("[SKIPPED] Cannot embed without GEMINI_API_KEY.")
    else:
        print("=== Step 3: Knowledge Base is up-to-date. Zero delta to embed. ===")

    # Prepare report data
    report_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "SUCCESS",
        "total_fetched": total_fetched,
        "added_count": added_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "embedded_chunks": embedded_chunks,
        "added_articles": [a["slug"] for a in delta["added"]],
        "updated_articles": [a["slug"] for a in delta["updated"]],
    }

    generate_reports(report_data, report_dir="reports")

    print("\n[SUCCESS] Daily Sync Completed.")
    print(f"Summary: added={added_count}, updated={updated_count}, skipped={skipped_count}")
    print("Reports generated: reports/daily_sync_report.json, reports/daily_sync_report.md")
    sys.exit(0)


if __name__ == "__main__":
    main()
