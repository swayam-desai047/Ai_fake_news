# Project status vs. synopsis (25 Nov 2026)

## Done (implemented and tested)
| Synopsis item | Status |
|---|---|
| RSS collection every 30 min (APScheduler) | Done — timeouts, ISO dates, failed feeds logged, no overlapping runs |
| Cleaning + duplicate removal | Done — in-batch and against the DB (title + URL, incl. tracking params) |
| BERT-tiny credibility classifier | Done — lazy loading, explicit label mapping (LABEL_1 = fake, configurable), "unavailable" status instead of fake values |
| Sentiment (Positive/Neutral/Negative) | Done — DistilBERT SST-2 with a neutral band; word-list fallback |
| 8-dimension analysis with explanations | Done — backend now stores all eight (was frontend-only); unmeasurable dimensions are `null` |
| Needs Verification state | Done — no score, 0.40–0.60 band, < 150 chars, low classifier confidence, or disagreement |
| Risk labels Low/Moderate/High | Done — no more "Low Risk" default; "not assessed" when evidence is insufficient |
| AI summary | Done as **extractive** summary (only when the excerpt has ≥ 3 sentences) |
| Cross-source comparison | Done — backend + frontend grouping, time-gap rule, accent folding, ≥ 2 publishers |
| Supabase storage, FastAPI APIs, Next.js dashboard, analytics, PDF report | Done |
| Security | Done — read-only public RLS on articles, service key server-only, CORS allow-list, validation, rate limit |
| Testing | Backend 62 passed (3 opt-in skipped); frontend 32 passed; lint, type check, build OK |
| Documentation | `docs/Project_Report.pdf` (30 pages, college index format), README, env examples |

## Remaining (needs your machine / credentials)
1. Run `backend/db/02_integrity_and_security.sql` in Supabase (existing DB) — or `supabase_complete_setup.sql` for a new one.
2. Put `SUPABASE_SERVICE_ROLE_KEY` in `backend/.env` (the public key can no longer write articles).
3. Install models (`pip install -r requirements.txt`) and run `python -m scripts.validate_models` to confirm the label mapping on your machine.
4. Run `python -m scripts.reanalyze` once to re-score old (legacy) rows.
5. Optional: `RUN_MODEL_TESTS=1` / `RUN_LIVE_TESTS=1 python -m pytest` (could not run in the build environment: no model download / feed access).

## Synopsis items not achievable as written
- **Calibration evaluation and accuracy/precision/recall/F1**: needs a labelled dataset and running models — not done; no numbers are claimed.
- **Abstractive "AI-generated" summaries**: replaced by extractive summaries (honestly labelled).
