# Knowledge Base Ingestion & AI Support Assistant (OptiBot Mini-Clone)

An automated pipeline that scrapes technical documentation from Zendesk Help Center, detects content deltas using SQLite, embeds text into a ChromaDB Vector Store via Google Gemini API, and provides an AI Support Assistant with exact citations.

> **Part 2 Assessment Delivery (Planning - Brief B)**:  
> Detailed engineering plan, 4-question defense, PostgreSQL DDL, and live system audit:  
> 👉 [**SCIO_SLICE_PLAN.md**](SCIO_SLICE_PLAN.md)

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

# Interactive chat mode:
python test_bot.py -i

# Verbose inspection mode (inspect chunks & citations):
python test_bot.py --verbose
```

### Code Quality & PEP 8 Check:
```bash
ruff check .
ruff format --check .
```

### Run with Docker:
```bash
docker build -t optibot-sync .
docker run --rm -e API_KEY=your_key optibot-sync
```

## 3. Chunking & Embedding Strategy
- **Chunking**: Markdown-aware sliding window with chunk size = 1000 characters and overlap = 150 characters to preserve context across section boundaries.
- **Embeddings**: Google Gemini `text-embedding-004` (768 dimensions), stored in local persistent ChromaDB with Cosine distance indexing.
- **Citations**: Source URLs are bound to chunk metadata and rendered verbatim in assistant responses.

## 4. Daily Job, Ingestion Mechanism & Reports
- **Automation Engine**: Automated via GitHub Actions scheduled workflow ([`.github/workflows/daily-sync.yml`](.github/workflows/daily-sync.yml)).
- **Execution Schedule**: Runs daily at **00:00 UTC** (`0 0 * * *`) with manual trigger support (`workflow_dispatch`).
- **4-Step Pipeline**:
  1. **Re-scrape**: Polls Zendesk Help Center API (`support.optisigns.com`) for latest articles.
  2. **Delta Detection**: Computes SHA-256 content hashes, comparing against local SQLite database (`sync_state.db`).
  3. **Delta-Only Embedding**: Only `added` and `updated` articles are embedded into ChromaDB via Gemini API; unchanged articles are skipped.
  4. **Reporting & Artifacts**: Generates machine-readable `reports/daily_sync_report.json` and human-readable `reports/daily_sync_report.md`, rendered into GitHub Actions `$GITHUB_STEP_SUMMARY` and uploaded as workflow artifacts.
- **Live Workflow Runs & Logs**:
  - 👉 [**All Workflow Runs History**](https://github.com/Personal-Source-SP/atlas-support-agent/actions)
  - 👉 [**Direct Link to Latest Verified Run**](https://github.com/Personal-Source-SP/atlas-support-agent/actions/runs/41268930151)
- **Sample Execution Report Output**:
  ```text
  === Step 1: Ingesting Zendesk Articles (support.optisigns.com) ===
  Total articles fetched: 31
  === Step 2: Checking Delta via SQLite ===
  Delta Result: [Added: 0] | [Updated: 0] | [Skipped: 31]
  === Step 3: Knowledge Base is up-to-date. Zero delta to embed. ===

  [SUCCESS] Daily Sync Completed.
  Summary: added=0, updated=0, skipped=31
  Reports generated: reports/daily_sync_report.json, reports/daily_sync_report.md
  ```


## 5. Sanity Check Screenshot

![OptiBot Sanity Check Screenshot](docs/sanity-check.png)

