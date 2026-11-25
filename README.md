# AI-Powered News Aggregator with Advanced Credibility and Content Analysis

M.Sc. Computer Science mini project (MIT-WPU, Group 17). A full-stack web application that collects
news from public RSS feeds, analyses every article (credibility-risk indicator, sentiment,
eight-dimension content analysis, extractive summary), groups reports of the same event across
publishers and presents everything on a newspaper-style dashboard with analytics and PDF reports.

> The system produces **indicators for critical reading, not verdicts**. Risk scores are heuristic
> and model scores are raw (uncalibrated) outputs. Nothing here proves that a report is true or false.

## Features

| Feature | Where |
|---|---|
| Scheduled RSS collection (every 30 min), cleaning, duplicate removal | `backend/services/rss_fetcher.py`, `scheduler.py`, `db_service.py` |
| Fake-news classifier (BERT-tiny) + sentiment (DistilBERT SST-2), lazy-loaded | `backend/services/ai_service.py` |
| Eight dimensions: sentiment, bias, objectivity, readability, propaganda, headline accuracy, source credibility, content quality | `backend/services/dimension_service.py` (mirror of `frontend/src/lib/scoring.ts`) |
| Risk score → Low / Moderate / High, or "not assessed"; Needs-Verification flag | `backend/services/analysis_pipeline.py` |
| Extractive summary (only when the excerpt has ≥ 3 sentences) | `analysis_pipeline.py` |
| Cross-source event grouping (TF-IDF + cosine, time window, ≥ 2 publishers) | `backend/services/clustering_service.py`, `frontend/src/lib/clustering.ts` |
| REST API (FastAPI) incl. PDF report | `backend/api/router.py`, `services/report_service.py` |
| Dashboard, article page, search & filters, external search, analytics, compare view, browser PDF | `frontend/src` |

## Architecture

```
RSS feeds ─► rss_fetcher (httpx + feedparser) ─► dedupe ─► analysis_pipeline
                                                         ├─ dimension_service (rules, 8 dimensions)
                                                         ├─ ai_service (BERT-tiny, DistilBERT SST-2)
                                                         └─ risk + verification + summary
          ─► Supabase/PostgreSQL `articles` ─► clustering_service (group_id)
          ─► FastAPI (/api/...)  and  Next.js server (reads Supabase with the public key)
          ─► Next.js pages: front page, article, search, compare, analytics, PDF
```

## Setup

### 1. Database (Supabase)

1. Create a Supabase project.
2. **New database:** run `backend/db/supabase_complete_setup.sql` in the SQL editor.
   **Existing (v1) database:** run `backend/db/01_upgrade_to_msc_synopsis.sql`, then
   `backend/db/02_integrity_and_security.sql`. Both are idempotent and do not delete data;
   migration 02 clears the fake "Low Risk" default from old rows and marks them `legacy`.
3. Project Settings → API: copy the URL, the **anon/publishable** key (frontend) and the
   **service-role/secret** key (backend only).

Security model: `articles` is publicly **readable** only; the backend writes with the service-role key
(bypasses RLS). `named_visitors` allows public read + insert for the name-only reader registration.

### 2. Backend (Python 3.10+)

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
python -m services.scheduler      # one ingestion run now, then every 30 minutes (Ctrl+C to stop)
uvicorn main:app --reload         # API on http://localhost:8000, docs at /docs
```

The API also starts the scheduler itself (`ENABLE_SCHEDULER=1`, `INGEST_ON_STARTUP=1` for an immediate run).
Re-score old rows with `python -m scripts.reanalyze`; check the models with `python -m scripts.validate_models`.

| Variable | Meaning |
|---|---|
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | Database (service key: server only) |
| `ALLOWED_ORIGINS` | CORS origins, comma-separated (default localhost:3000) |
| `RATE_LIMIT_PER_MINUTE` | Per-IP limit for `/analyze` and `/report` (default 30) |
| `ENABLE_SCHEDULER`, `INGEST_INTERVAL_MINUTES`, `INGEST_ON_STARTUP` | Scheduler |
| `ENABLE_MODELS`, `FAKE_NEWS_MODEL`, `SENTIMENT_MODEL` | Models |
| `FAKE_NEWS_FAKE_LABEL` / `FAKE_NEWS_REAL_LABEL` | Classifier label mapping (default LABEL_1 = fake) |
| `INGEST_TOKEN` | Enables `POST /api/ingest` (header `X-Ingest-Token`) |

### 3. Frontend (Node 20+)

```bash
cd frontend
cp .env.example .env.local        # NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_URL
npm install
npm run dev                       # http://localhost:3000
```

## API

| Method | Path (also under `/api/v1`) | Description |
|---|---|---|
| GET | `/api/health` | Status, DB configured, model load state, last ingestion run |
| POST | `/api/analyze` | `{text, title?, publisher?}` → full analysis (nothing stored) |
| GET | `/api/articles` | `limit, offset, category, risk (Low Risk/Moderate Risk/High Risk/Unavailable), q, needs_verification` |
| GET | `/api/article/{uuid}` | One article |
| GET | `/api/groups` | Cross-source groups with publisher-wise coverage |
| GET | `/api/analytics` | Counts by category, sentiment, risk, status; dimension averages |
| GET | `/api/report/{uuid}` | A4 PDF report |
| POST | `/api/ingest` | Manual ingestion (only when `INGEST_TOKEN` is set) |

## Tests

```bash
cd backend && python -m pytest          # unit/API tests (models and DB are faked)
RUN_MODEL_TESTS=1 python -m pytest      # + real model download & inference
RUN_LIVE_TESTS=1 python -m pytest       # + real RSS feeds and Supabase
cd frontend && npm run test && npm run lint && npm run build
```

`shared/scoring_vectors.json` is checked by both suites, so the Python and TypeScript scoring
engines cannot drift apart.

## Documentation

`docs/Project_Report.pdf` — final project report (source: `docs/report/`).

## Limitations (short)

RSS excerpts are short, so many articles carry the Needs-Verification flag; the BERT-tiny classifier
was trained on long political articles and its label mapping is not documented in the model config;
lexicon-based dimensions are approximations; cross-source similarity is not claim verification; the
system is English-only. See the report for details.
