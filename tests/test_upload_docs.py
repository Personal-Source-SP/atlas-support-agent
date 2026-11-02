import os
import tempfile
from unittest.mock import MagicMock, patch

from upload_docs import parse_markdown_file, upload_markdown_directory


def test_parse_markdown_file_valid():
    sample_content = (
        "# How to Use YouTube App\n\n"
        "Source: https://support.optisigns.com/hc/en-us/articles/999\n\n"
        "Step 1: Open app.\nStep 2: Paste link."
    )
    with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(sample_content)
        temp_path = f.name

    try:
        data = parse_markdown_file(temp_path)
        assert data is not None
        assert data["title"] == "How to Use YouTube App"
        assert data["url"] == "https://support.optisigns.com/hc/en-us/articles/999"
        assert "Step 1: Open app." in data["body_md"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_parse_markdown_file_non_markdown():
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
        f.write("Some text")
        temp_path = f.name

    try:
        assert parse_markdown_file(temp_path) is None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@patch("upload_docs.VectorStoreManager")
def test_upload_markdown_directory_mocked(mock_v_mgr):
    mock_instance = MagicMock()
    mock_instance.index_articles.return_value = {"files": 2, "chunks": 5}
    mock_v_mgr.return_value = mock_instance

    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = os.path.join(temp_dir, "1001-article-one.md")
        file2 = os.path.join(temp_dir, "1002-article-two.md")

        with open(file1, "w", encoding="utf-8") as f:
            f.write("# Article 1\n\nSource: https://example.com/1\n\nContent 1")
        with open(file2, "w", encoding="utf-8") as f:
            f.write("# Article 2\n\nSource: https://example.com/2\n\nContent 2")

        stats = upload_markdown_directory(
            docs_dir=temp_dir,
            persist_dir="temp_chroma",
            api_key="dummy_key",
        )
        assert stats["files"] == 2
        assert stats["chunks"] == 5
        mock_instance.index_articles.assert_called_once()
