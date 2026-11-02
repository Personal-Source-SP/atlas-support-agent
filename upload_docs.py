import argparse
import os
import re
import sys
from typing import Any

from dotenv import load_dotenv

from src.vector_store import VectorStoreManager


def parse_markdown_file(file_path: str) -> dict[str, Any] | None:
    """Parse a Markdown document, extracting title, source URL, article ID, and content."""
    if not os.path.isfile(file_path) or not file_path.endswith(".md"):
        return None

    filename = os.path.basename(file_path)
    # Extract ID from filename prefix e.g., '360051014713-how-to-add-a-youtube-video.md'
    id_match = re.match(r"^(\d+)-", filename)
    article_id = int(id_match.group(1)) if id_match else abs(hash(filename)) % 1000000

    with open(file_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    title = filename.replace(".md", "")
    source_url = ""
    body_lines = []

    # Parse metadata header if present
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if idx == 0 and stripped.startswith("# "):
            title = stripped[2:].strip()
        elif stripped.startswith("Source: "):
            source_url = stripped.replace("Source: ", "").strip()
        else:
            body_lines.append(line)

    body_md = "\n".join(body_lines).strip()
    if not body_md:
        body_md = content.strip()

    return {
        "id": article_id,
        "title": title,
        "url": source_url or f"https://support.optisigns.com/hc/en-us/articles/{article_id}",
        "body_md": body_md,
        "file_path": file_path,
        "slug": filename.replace(".md", ""),
    }


def upload_markdown_directory(
    docs_dir: str = "docs",
    persist_dir: str = "chroma_db",
    api_key: str | None = None,
) -> dict[str, int]:
    """Load all Markdown files from docs_dir and ingest into Gemini Vector Store."""
    if not os.path.isdir(docs_dir):
        raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")

    files = sorted([os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith(".md")])
    if not files:
        print(f"[WARNING] No Markdown (.md) files found in '{docs_dir}'.")
        return {"files": 0, "chunks": 0}

    print(f"=== [Step 1] Discovered {len(files)} Markdown files in '{docs_dir}' ===")
    articles = []
    for f in files:
        art = parse_markdown_file(f)
        if art and art["body_md"]:
            articles.append(art)

    print(f"=== [Step 2] Chunking and Ingesting {len(articles)} documents via Gemini API ===")
    v_mgr = VectorStoreManager(persist_dir=persist_dir, api_key=api_key)
    stats = v_mgr.index_articles(articles)

    print(
        f"[SUCCESS] Ingestion Complete: {stats['files']} Markdown files ingested, "
        f"{stats['chunks']} vector chunks embedded into ChromaDB collection 'optisigns_support'."
    )
    return stats


def main(argv=None):
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Ingest local Markdown documentation into Google Gemini ChromaDB Vector Store."
    )
    parser.add_argument(
        "--docs-dir",
        "-d",
        type=str,
        default="docs",
        help="Path to directory containing .md files (default: docs)",
    )
    parser.add_argument(
        "--persist-dir",
        "-p",
        type=str,
        default="chroma_db",
        help="Path to ChromaDB persistence directory (default: chroma_db)",
    )
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        default=None,
        help="Google Gemini API key (defaults to GEMINI_API_KEY environment variable)",
    )
    args = parser.parse_args(argv)

    api_key = args.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print(
            "[ERROR] GEMINI_API_KEY is not set. Please provide via --api-key or set in .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        stats = upload_markdown_directory(
            docs_dir=args.docs_dir,
            persist_dir=args.persist_dir,
            api_key=api_key,
        )
        if stats["files"] == 0:
            sys.exit(1)
        sys.exit(0)
    except Exception as exc:
        print(f"[FATAL] Upload failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
