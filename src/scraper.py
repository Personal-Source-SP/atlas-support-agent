import os
import re
from typing import Any, Dict, List

import markdownify
import requests
from bs4 import BeautifulSoup

BASE_API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"


def generate_slug(title: str, article_id: int) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9\s-]", "", title).strip().lower()
    slug_body = re.sub(r"[\s-]+", "-", normalized)
    return f"{article_id}-{slug_body}"


def clean_html_to_markdown(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "iframe"]):
        tag.decompose()
    md = markdownify.markdownify(str(soup), heading_style="ATX", strip=["script", "style"])
    md_clean = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md_clean


def fetch_zendesk_articles(min_count: int = 30, docs_dir: str = "docs") -> List[Dict[str, Any]]:
    os.makedirs(docs_dir, exist_ok=True)
    articles: List[Dict[str, Any]] = []
    url = f"{BASE_API_URL}?per_page=100"

    headers = {"User-Agent": "OptiBot-Collector/1.0"}

    while url and len(articles) < min_count:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("articles", []):
            if item.get("draft") or not item.get("body"):
                continue
            slug = generate_slug(item["title"], item["id"])
            body_md = clean_html_to_markdown(item["body"])

            file_path = os.path.join(docs_dir, f"{slug}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {item['title']}\n\nSource: {item['html_url']}\n\n{body_md}\n")

            articles.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "slug": slug,
                    "url": item["html_url"],
                    "body_md": body_md,
                    "file_path": file_path,
                }
            )
            if len(articles) >= min_count:
                break

        url = data.get("next_page")

    return articles
