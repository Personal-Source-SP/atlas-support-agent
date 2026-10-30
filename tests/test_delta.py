import pytest

from src.delta import DeltaTracker


@pytest.fixture
def tracker(tmp_path):
    db_file = tmp_path / "test_sync.db"
    return DeltaTracker(db_path=str(db_file))


def test_classify_new_articles(tracker):
    articles = [
        {
            "id": 1,
            "slug": "art-1",
            "title": "Article 1",
            "url": "https://example.com/1",
            "body_md": "Content 1",
        },
        {
            "id": 2,
            "slug": "art-2",
            "title": "Article 2",
            "url": "https://example.com/2",
            "body_md": "Content 2",
        },
    ]
    delta = tracker.classify_articles(articles)
    assert len(delta["added"]) == 2
    assert len(delta["updated"]) == 0
    assert len(delta["skipped"]) == 0


def test_classify_skipped_articles(tracker):
    articles = [
        {
            "id": 1,
            "slug": "art-1",
            "title": "Article 1",
            "url": "https://example.com/1",
            "body_md": "Content 1",
        }
    ]
    # Lần 1: Thêm mới
    tracker.classify_articles(articles)

    # Lần 2: Nạp lại giữ nguyên
    delta = tracker.classify_articles(articles)
    assert len(delta["added"]) == 0
    assert len(delta["updated"]) == 0
    assert len(delta["skipped"]) == 1
    assert delta["skipped"][0]["id"] == 1


def test_classify_updated_articles(tracker):
    articles = [
        {
            "id": 1,
            "slug": "art-1",
            "title": "Article 1",
            "url": "https://example.com/1",
            "body_md": "Content 1",
        }
    ]
    tracker.classify_articles(articles)

    # Cập nhật nội dung
    modified_articles = [
        {
            "id": 1,
            "slug": "art-1",
            "title": "Article 1",
            "url": "https://example.com/1",
            "body_md": "Content 1 Updated!",
        }
    ]
    delta = tracker.classify_articles(modified_articles)
    assert len(delta["added"]) == 0
    assert len(delta["updated"]) == 1
    assert len(delta["skipped"]) == 0
    assert delta["updated"][0]["id"] == 1
