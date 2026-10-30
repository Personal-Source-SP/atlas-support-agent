import hashlib
import sqlite3
from typing import Any, Dict, List


class DeltaTracker:
    def __init__(self, db_path: str = "sync_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY,
                    slug TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_history (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_count INTEGER NOT NULL,
                    updated_count INTEGER NOT NULL,
                    skipped_count INTEGER NOT NULL
                )
            """)
            conn.commit()

    @staticmethod
    def compute_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def classify_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        delta: Dict[str, List[Dict[str, Any]]] = {"added": [], "updated": [], "skipped": []}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for art in articles:
                content_hash = self.compute_hash(art["body_md"])
                art_record = {**art, "content_hash": content_hash}
                cursor.execute("SELECT content_hash FROM articles WHERE id = ?", (art["id"],))
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(
                        """
                        INSERT INTO articles (id, slug, title, url, content_hash)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (art["id"], art["slug"], art["title"], art["url"], content_hash),
                    )
                    delta["added"].append(art_record)
                elif row[0] != content_hash:
                    cursor.execute(
                        """
                        UPDATE articles
                        SET slug = ?, title = ?, url = ?, content_hash = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (art["slug"], art["title"], art["url"], content_hash, art["id"]),
                    )
                    delta["updated"].append(art_record)
                else:
                    delta["skipped"].append(art_record)
            conn.commit()
        return delta

    def record_history(self, added: int, updated: int, skipped: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO sync_history (added_count, updated_count, skipped_count)
                VALUES (?, ?, ?)
                """,
                (added, updated, skipped),
            )
            conn.commit()
