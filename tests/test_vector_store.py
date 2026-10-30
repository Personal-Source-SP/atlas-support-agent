from src.vector_store import chunk_text


def test_chunk_text_preserves_metadata():
    content = "A" * 1500
    article = {
        "id": 101,
        "title": "YouTube Setup",
        "slug": "101-youtube-setup",
        "url": "https://support.optisigns.com/hc/en-us/articles/101",
        "body_md": content,
    }
    chunks = chunk_text(article, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 1
    for c in chunks:
        assert c["metadata"]["url"] == article["url"]
        assert c["metadata"]["title"] == article["title"]
        assert len(c["text"]) <= 600


def test_chunk_text_small_content():
    article = {
        "id": 102,
        "title": "Short Article",
        "url": "https://example.com/short",
        "body_md": "Short text here.",
    }
    chunks = chunk_text(article, chunk_size=500, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Short text here."
