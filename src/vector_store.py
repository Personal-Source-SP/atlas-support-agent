import os
import time
from typing import Any

import chromadb
from google import genai

EMBEDDING_MODEL = "gemini-embedding-001"


def chunk_text(
    article: dict[str, Any], chunk_size: int = 1000, chunk_overlap: int = 150
) -> list[dict[str, Any]]:
    text = article.get("body_md", "")
    if not text:
        return []
    chunks = []
    start = 0
    chunk_idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_slice = text[start:end].strip()
        if chunk_slice:
            chunks.append(
                {
                    "id": f"{article['id']}_{chunk_idx}",
                    "text": chunk_slice,
                    "metadata": {
                        "article_id": str(article["id"]),
                        "title": article["title"],
                        "url": article["url"],
                    },
                }
            )
            chunk_idx += 1
        if end >= len(text):
            break
        start += chunk_size - chunk_overlap
    return chunks


class VectorStoreManager:
    def __init__(self, persist_dir: str = "chroma_db", api_key: str | None = None):
        self.persist_dir = persist_dir
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name="optisigns_support", metadata={"hnsw:space": "cosine"}
        )

    def embed_texts(self, texts: list[str], batch_size: int = 15) -> list[list[float]]:
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured.")
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    res = self.client.models.embed_content(model=EMBEDDING_MODEL, contents=batch)
                    embeddings.extend([e.values for e in res.embeddings])
                    time.sleep(0.5)
                    break
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        wait_seconds = 15 * (attempt + 1)
                        print(
                            f"[THROTTLE] Rate limit reached. Backing off {wait_seconds}s "
                            f"(attempt {attempt + 1}/{max_retries})..."
                        )
                        time.sleep(wait_seconds)
                    else:
                        raise e
        return embeddings

    def index_articles(self, articles: list[dict[str, Any]]) -> dict[str, int]:
        all_chunks: list[dict[str, Any]] = []
        for art in articles:
            all_chunks.extend(chunk_text(art))
        if not all_chunks:
            return {"files": 0, "chunks": 0}

        texts = [c["text"] for c in all_chunks]
        ids = [c["id"] for c in all_chunks]
        metadatas = [c["metadata"] for c in all_chunks]

        embeddings = self.embed_texts(texts)
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
        return {"files": len(articles), "chunks": len(all_chunks)}

    def query(self, query_text: str, top_k: int = 3) -> list[dict[str, Any]]:
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured.")
        res = self.client.models.embed_content(model=EMBEDDING_MODEL, contents=query_text)
        query_vector = res.embeddings[0].values
        results = self.collection.query(query_embeddings=[query_vector], n_results=top_k)
        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        return [{"text": doc, "metadata": meta} for doc, meta in zip(docs, metas, strict=False)]
