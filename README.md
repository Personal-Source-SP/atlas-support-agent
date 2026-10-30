# Knowledge Base Ingestion & AI Support Assistant (OptiBot Mini-Clone)

An automated pipeline that scrapes technical documentation from Zendesk Help Center, detects content deltas using SQLite, embeds text into a ChromaDB Vector Store via Google Gemini API, and provides an AI Support Assistant with exact citations.

## 1. Local Setup

Clone the repository and set up dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env
# Edit .env and insert your GEMINI_API_KEY
```

## 2. Running Locally

### Execute Daily Sync (Scrape, Delta, Embed):
```bash
python main.py
```
*Outputs summary counts: added, updated, skipped.*

### Run Sanity Check (Ask OptiBot):
```bash
python test_bot.py "How do I add a YouTube video?"
```

### Code Quality & PEP 8 Check:
```bash
ruff check .
ruff format --check .
```

### Run with Docker:
```bash
docker build -t optibot-sync .
docker run --rm -e GEMINI_API_KEY=your_key optibot-sync
```

## 3. Chunking & Embedding Strategy
- **Chunking**: Markdown-aware sliding window with chunk size = 1000 characters and overlap = 150 characters to preserve context across section boundaries.
- **Embeddings**: Google Gemini `text-embedding-004` (768 dimensions), stored in local persistent ChromaDB with Cosine distance indexing.
- **Citations**: Source URLs are bound to chunk metadata and rendered verbatim in assistant responses.

## 4. Daily Job & Logs
- Automated via GitHub Actions scheduled workflow (`.github/workflows/daily-sync.yml`).
- **Public Workflow Run Logs**: [View Daily Job Execution Logs](https://github.com) *(Update with your repository URL)*

## 5. Sanity Check Screenshot

![OptiBot Sanity Check Screenshot](docs/sanity-check.png)

