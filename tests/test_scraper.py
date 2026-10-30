from src.scraper import clean_html_to_markdown, generate_slug


def test_generate_slug():
    title = "How to Use YouTube with OptiSigns!"
    slug = generate_slug(title, article_id=360051014713)
    assert slug == "360051014713-how-to-use-youtube-with-optisigns"


def test_clean_html_to_markdown():
    raw_html = """
    <h2>Install OptiSigns</h2>
    <p>Go to <a href="https://app.optisigns.com">OptiSigns Portal</a>.</p>
    <script>alert('bad');</script>
    <ul>
      <li>Step 1</li>
      <li>Step 2</li>
    </ul>
    """
    md = clean_html_to_markdown(raw_html)
    assert "## Install OptiSigns" in md
    assert "[OptiSigns Portal](https://app.optisigns.com)" in md
    assert "alert" not in md
    assert "Step 1" in md
    assert "Step 2" in md
