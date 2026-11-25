# Synopsis vs. implementation: discrepancy audit (Group 17, "AI-Powered News Aggregator with Advanced Credibility and Content Analysis")

Notes on method and links:
- Synopsis = `/root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/7fa5cf3c-synopsiswithdiagram_1.pdf` (29 PDF pages; printed page labels 1–21; UML diagrams are PDF pages 15–19). I extracted the text with `pdftotext -layout` and looked at the use case and class diagram pages as images to read their associations. Cited as [Syn §…](file:///root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/7fa5cf3c-synopsiswithdiagram_1.pdf).
- Code links are `file:///home/user/Ai_fake_news/<path>#L<line>`. Line numbers were checked against the working tree at commit `cf943f4`.
- Classification keys: **M** = Matches; **D** = Implemented differently; **P** = Partially implemented; **N** = Not implemented; **X** = Code has an extra feature that is not in the synopsis.
- Rule followed: where the code and the documentation disagree, the code wins. Each recommended wording describes what the code does and also names the gap.

---

## Q1. Section-by-section: every synopsis claim checked against the code

### Takeaway
The synopsis is mostly implemented. The collection pipeline, deduplication, the 30-minute APScheduler job, BERT-tiny plus sentiment, the eight dimensions, Needs Verification, cross-source grouping, Supabase, the FastAPI endpoints, the Recharts analytics and the PDF reports all exist. Four headline promises are **not** met:
1. Summaries are **extractive**, not "AI-generated".
2. **No calibration** is done.
3. **No accuracy/precision/recall/F1 evaluation** was carried out on any labelled dataset.
4. The **frontend does not read data through FastAPI**: the Next.js server queries Supabase directly.

Several synopsis details are also implemented differently:
- Sentiment comes from a binary SST-2 model plus a neutral band.
- Source credibility comes from a hand-curated reputation table, not from "source history".
- Near-duplicates are only handled through exact normalised title/URL matching.
- The data model is a single `articles` table, not separate Source, Summary and Report entities.

### Cited Findings

**Introduction / Overview / Background / Need (Syn printed pp.1–3)**
- Synopsis: "short AI-generated summaries", "transformer-based NLP", "Python, FastAPI, Supabase, Next.js, React, Tailwind, Recharts", "scheduled at regular 30-minute intervals … near-real-time" — [Syn Intro p.1](file:///root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/7fa5cf3c-synopsiswithdiagram_1.pdf)
  - 30-minute near-real-time → **M**. `INTERVAL_MINUTES = int(os.getenv("INGEST_INTERVAL_MINUTES","30"))` and an `IntervalTrigger` with `max_instances=1, coalesce=True` — [scheduler.py:25](file:///home/user/Ai_fake_news/backend/services/scheduler.py#L25), [scheduler.py:53-63](file:///home/user/Ai_fake_news/backend/services/scheduler.py#L53). The interval can be changed through an env var. Ingestion only runs when the scheduler is enabled in the FastAPI lifespan (`ENABLE_SCHEDULER`) — [main.py:27-38](file:///home/user/Ai_fake_news/backend/main.py#L27).
  - "AI-generated summaries" → **D/N**. `extractive_summary()` is described as a "Frequency-based extractive summary … Nothing is generated or paraphrased". It returns None unless there are at least 3 sentences longer than 30 characters — [analysis_pipeline.py:52-74](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L52). Stored with `summary_method: "extractive"` — [analysis_pipeline.py:153,167](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L153). The frontend live-feed summary is simply the first two sentences — [scoring.ts:99-103](file:///home/user/Ai_fake_news/frontend/src/lib/scoring.ts#L99).
  - "Overview: BERT model used for credibility-risk classification … Sentiment classifies Positive, Negative or Neutral" → BERT **M** (`mrm8488/bert-tiny-finetuned-fake-news-detection`, [ai_service.py:34](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L34)). Sentiment is **D**: `distilbert-base-uncased-finetuned-sst-2-english` is a binary POSITIVE/NEGATIVE model ([ai_service.py:6,35](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L35)). "Neutral" is derived from a score band: ≥60 positive, ≤40 negative, otherwise neutral ([dimension_service.py:140-141](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L140), [analysis_pipeline.py:77-87](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L77)).
  - "Overview: the frontend … FastAPI provides the backend APIs and connects the frontend with … database layers" → **D**. See Q2 (sequence diagram) and the technology flow below.
  - "Background: Summarization models can reduce lengthy content" → **N** (no summarization model anywhere; requirements.txt has no summarization model, and grep finds no `pipeline("summarization")`) — [requirements.txt](file:///home/user/Ai_fake_news/backend/requirements.txt).
  - Need bullets (save time, fewer duplicates, quick credibility-risk indication, short summary, cross-source comparison, eight dimensions, original links) → all **M**, except "short summary", which is **D** (extractive, and only when the excerpt has ≥3 sentences). Original links: "Original report" link on the article page — [article/[id]/page.tsx:68-70,105-106](file:///home/user/Ai_fake_news/frontend/src/app/article/[id]/page.tsx#L68).
  - "PDF report can contain … AI summary" → **P**. The ReportLab PDF includes `ai_summary` when it exists and also prints the RSS excerpt — [report_service.py:93-96](file:///home/user/Ai_fake_news/backend/services/report_service.py#L93).

**Technology table (Syn §1.4, printed p.4)**
| Synopsis technology | Code evidence | Class |
|---|---|---|
| Python | backend/*.py | M |
| FastAPI | `fastapi>=0.110.0`, [main.py](file:///home/user/Ai_fake_news/backend/main.py) | M (but the frontend does not use it for reads, see below) |
| BERT / Transformer | `transformers>=4.38.0`, `torch>=2.2.0`, bert-tiny ([requirements.txt](file:///home/user/Ai_fake_news/backend/requirements.txt), [ai_service.py:34](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L34)) | M. Loaded lazily and optional (`ENABLE_MODELS`); if it fails, status = "unavailable" ([ai_service.py:38,47-69](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L47)) |
| Sentiment model (Pos/Neg/Neu) | DistilBERT SST-2 (binary) plus neutral band; word-list fallback | D |
| AI Summarization | none; frequency-based extractive | N (replaced by extractive) |
| Supabase/PostgreSQL | `supabase>=2.3.4`; [supabase_complete_setup.sql](file:///home/user/Ai_fake_news/backend/db/supabase_complete_setup.sql) | M |
| APScheduler | `apscheduler>=3.11.3`; [scheduler.py](file:///home/user/Ai_fake_news/backend/services/scheduler.py) | M |
| Next.js/React | `next 16.1.6`, `react 19.2.3` ([package.json](file:///home/user/Ai_fake_news/frontend/package.json)) | M |
| Tailwind CSS | `tailwindcss ^4`, `@tailwindcss/postcss`; `@import "tailwindcss"` in [globals.css:1](file:///home/user/Ai_fake_news/frontend/src/app/globals.css#L1). Much of the styling is a custom "editorial design system" written in plain CSS classes in the same file | M |
| Recharts | `recharts ^3.7.0`; BarChart, AreaChart in [DashboardAnalytics.tsx](file:///home/user/Ai_fake_news/frontend/src/components/dashboard/DashboardAnalytics.tsx); RadarChart in [DimensionRadarChart.tsx](file:///home/user/Ai_fake_news/frontend/src/components/ui/DimensionRadarChart.tsx) | M |
| (not in synopsis) feedparser + httpx + BeautifulSoup | [rss_fetcher.py:18-20](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L18) | X (feedparser is named only in the architecture table) |
| (not in synopsis) ReportLab (server PDF), jsPDF (browser PDF) | `reportlab>=4.1.0`, `jspdf ^4.2.1` | X |
| (not in synopsis) Vitest, Testing Library, pypdf | package.json devDeps; requirements.txt | X |
| axios in package.json | not imported anywhere in `frontend/src` (grep) | unused dependency (housekeeping) |

**Overall technology flow (Syn printed p.4)**: "RSS → Python → Cleaning/Dedup → AI/NLP → DB → FastAPI → Next.js"
- **D**. Three things differ:
  - The Next.js server reads Supabase directly with the public anon key: `loadDatabaseArticles()` runs `supabase.from('articles').select('*')…limit(500)` and caches the result for 60 s ([repository.ts:135-151](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L135)). FastAPI is only called for the optional server PDF, and only when `NEXT_PUBLIC_API_URL` is set ([ReportDownload.tsx:14-16](file:///home/user/Ai_fake_news/frontend/src/components/analysis/ReportDownload.tsx#L14); [.env.example](file:///home/user/Ai_fake_news/frontend/.env.example): "FastAPI backend URL, used for the server-side PDF report link (optional)").
  - When the DB is empty or not configured, a second path runs: Next.js reads publisher RSS feeds itself and scores them with rules in TypeScript ([repository.ts:169-184](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L169), [liveNewsService.ts:1-12](file:///home/user/Ai_fake_news/frontend/src/lib/liveNewsService.ts#L1)).
  - Cross-source grouping runs after storage as a batch step (`update_groups()` after `store_articles_in_db`), not per article inside the AI layer ([scheduler.py:37-40](file:///home/user/Ai_fake_news/backend/services/scheduler.py#L37)).

**Problem statement / Proposed solution (Syn printed p.5)**
- "needs a better way to interpret credibility-related model outputs rather than raw confidence" → **P**. Better interpretation is done: raw scores are labelled uncalibrated, an uncertainty band is applied, the Needs Verification flag is set, and rule and model scores are combined. Calibration is not done (see Q3).
- "searchable dashboard" → **M** (search page, `/api/articles?q=`; [router.py:78-105](file:///home/user/Ai_fake_news/backend/api/router.py#L78); [repository.ts](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts) `queryArticles`).

**Objectives (Syn §2.3, printed p.6)**
| # | Objective | Class | Evidence |
|---|---|---|---|
| 1 | Collect recent news from multiple RSS sources | M | 11 feeds in 5 categories, 8 entries per feed — [rss_fetcher.py:25-49](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L25) |
| 2 | Clean/normalise/preprocess | M | `clean_html`, `normalise_url`, `normalise_title`, ISO-UTC dates; untitled or URL-less items dropped — [rss_fetcher.py:54-106](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L54) |
| 3 | Identify/reduce duplicate **or highly similar** entries | P | Only exact matches after normalisation: title and URL within the batch ([rss_fetcher.py:115-125](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L115)), against the DB ([db_service.py:67-80,119-123](file:///home/user/Ai_fake_news/backend/services/db_service.py#L67)), plus a UNIQUE(title) upsert ([db_service.py:94-105](file:///home/user/Ai_fake_news/backend/services/db_service.py#L94)). "Highly similar" stories are grouped (TF-IDF), not removed |
| 4 | Transformer credibility-risk + confidence indicator | M (conditional) | `classify_fake_news` → `fake_probability`, `confidence = max(p,1-p)` — [ai_service.py:106-139](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L106). Final risk = mean(rule_risk, p_fake) — [analysis_pipeline.py:113-121](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L113) |
| 5 | Improve interpretation **and calibration** of confidence | P (interpretation) / N (calibration) | "Softmax scores are reported as raw, uncalibrated model outputs" — [ai_service.py:22](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L22); "These are heuristic indicators, not calibrated probabilities" — [analysis_pipeline.py:20](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L20) |
| 6 | Sentiment Pos/Neg/Neu | D | binary SST-2 plus neutral band (above) |
| 7 | Concise AI-based summaries | D/N | extractive only (above) |
| 8 | Compare articles from different sources, show differences in coverage/framing | M/P | Grouping in [clustering_service.py](file:///home/user/Ai_fake_news/backend/services/clustering_service.py), `/api/groups` with publisher-wise coverage ([db_service.py:39-64](file:///home/user/Ai_fake_news/backend/services/db_service.py#L39)), `/compare` page ([CrossSourceView.tsx](file:///home/user/Ai_fake_news/frontend/src/components/dashboard/CrossSourceView.tsx)). The page shows headlines, risk and sentiment side by side. There is no automatic "difference/framing" analysis |
| 9 | 8-dimension analysis | M (D in method) | All eight keys — [dimension_service.py:29-32](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L29). Seven dimensions are lexical/rule-based; only sentiment uses a model |
| 10 | Needs Verification when evidence/confidence is insufficient | M (D in conditions) | Five conditions — [analysis_pipeline.py:124-135](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L124) |
| 11 | Store in Supabase; search and filtering | M | [db_service.py](file:///home/user/Ai_fake_news/backend/services/db_service.py); filters for category, risk, needs_verification and q — [router.py:78-105](file:///home/user/Ai_fake_news/backend/api/router.py#L78). The frontend adds publisher and date filters |
| 12 | Visual analytics + downloadable PDF | M | analytics page and Recharts; ReportLab + jsPDF |
| 13 | Evaluate with classification, calibration and output-quality measures | N (classification, calibration) / P (software tests) | [validate_models.py:9-10](file:///home/user/Ai_fake_news/backend/scripts/validate_models.py#L9): "The examples are illustrative, not a benchmark: no accuracy figure from this script should be reported" |

**Scope (Syn printed p.6–7)**
- "Selected public RSS feeds, primarily English" → **M**. Backend feeds: BBC (several), BBC Sport, CNN (3), Yahoo Sports/Finance, Al Jazeera ([rss_fetcher.py:25-47](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L25)). The live fallback adds Google News topic feeds, The Guardian, The Hindu, NDTV, Indian Express, Mint and TechCrunch ([sections.ts:25-74](file:///home/user/Ai_fake_news/frontend/src/lib/sections.ts#L25)).
- "Calibrated model-confidence presentation" → **N**.
- "Short AI-generated summaries" → **D**.
- All other scope bullets → **M**.

**16 implementation phases (Syn §3.1, printed pp.8–10)**
| Phase | Class | Evidence / difference |
|---|---|---|
| 1 Requirements & design | M | separate modules: collection / analysis / storage / API / frontend |
| 2 RSS collection (title, source, URL, date, category, description) | M | [rss_fetcher.py:86-106](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L86). Category comes from the feed's configured group, not from the feed item |
| 3 Preprocessing & dedup (incl. "highly similar") | P | exact title/URL only (above). A missing date → DB default `now()` ([db_service.py:89-90](file:///home/user/Ai_fake_news/backend/services/db_service.py#L89)) |
| 4 BERT credibility + sentiment | M/D | bert-tiny; sentiment binary SST-2 (above). Models are optional and may be "unavailable" |
| 5 AI short summarization | D/N | extractive, ≥3 sentences; RSS excerpts are usually 1–2 sentences, so most articles get no summary (the README says it appears "only when the excerpt has ≥ 3 sentences") |
| 6 Better-calibrated credibility; "Calibration will be evaluated" | P/N | interpretation layer: risk labels (Low ≤0.35, Moderate ≤0.65, High), 0.40–0.60 band, "uncalibrated" wording ([dimension_service.py:132-137](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L132)). No calibration method (temperature scaling, Platt, isotonic) and no ECE/Brier/reliability evaluation anywhere in the repo |
| 7 Cross-source comparison "using titles, descriptions **and generated summaries**" | D | Headline counted twice + lead sentence of the excerpt, TF-IDF cosine ≥0.32, 48 h window, ≤36 h from the seed, ≥2 publishers, one article per publisher — [clustering_service.py:28-31,97,85-129](file:///home/user/Ai_fake_news/backend/services/clustering_service.py#L28). Summaries are not used |
| 8 Eight dimensions (table of assessment methods) | M/D | See Q1 dimension table below |
| 9 DB integration (articles, **source information**, categories, sentiment, credibility, summaries, groups, dimensions) | M/D | One `articles` table holding everything: dimensions in JSONB, `group_id`/`event_title`, `ai_summary`, `summary_method`, risk fields ([supabase_complete_setup.sql:14-…](file:///home/user/Ai_fake_news/backend/db/supabase_complete_setup.sql#L14)). There is no `sources` table: the source is a text column `source_domain`. The only other tables are `named_visitors` and `user_profiles` (unused) |
| 10 FastAPI endpoints: listing, details, search, filters, **categories, sources**, groups, analytics, AI outputs | P | Exists: `/health`, `/analyze`, `/articles` (search and filters through query params), `/article/{id}`, `/groups`, `/analytics`, `/report/{id}`, `/ingest` — [router.py:53-187](file:///home/user/Ai_fake_news/backend/api/router.py#L53). There are no `/categories` or `/sources` endpoints (`/analytics` returns category and publisher counts) |
| 11 APScheduler every 30 min, logging, one failing source doesn't stop the run | M | [scheduler.py:30-50](file:///home/user/Ai_fake_news/backend/services/scheduler.py#L30); a failing feed is recorded in `failed_sources` ([rss_fetcher.py:138-147](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L138)) |
| 12 Frontend: Next.js, React, Tailwind; cards, indicators, sentiment, summaries, groups, 8-dim | M | "The Daily Signal" newspaper UI; the summary is labelled "Extractive summary — sentences selected from the excerpt" ([article/[id]/page.tsx:111-116](file:///home/user/Ai_fake_news/frontend/src/app/article/[id]/page.tsx#L111)) |
| 13 PDF report (title, source, publication, AI summary, credibility, 8-dim) | M (+X) | Server: ReportLab `GET /api/report/{id}` ([router.py:161-175](file:///home/user/Ai_fake_news/backend/api/router.py#L161), [report_service.py](file:///home/user/Ai_fake_news/backend/services/report_service.py)). Browser: jsPDF for any article ([pdfReportGenerator.ts](file:///home/user/Ai_fake_news/frontend/src/lib/pdfReportGenerator.ts)) |
| 14 Recharts: category, sentiment, source-wise counts, credibility-risk distribution | M (+X) | `getAnalytics()` returns sections, risk (+Needs Verification), sentiment, dimension averages, publishers, hourly timeline and coverage width — [repository.ts:364-431](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L364) |
| 15 Testing & evaluation (module tests + accuracy/P/R/F1 + calibration + summary/grouping/8-dim checks) | P | Backend: 56 `def test_` functions in 9 files (62 passed, 3 opt-in skipped, per [PROJECT_STATUS.md](file:///home/user/Ai_fake_news/docs/PROJECT_STATUS.md)). Frontend: 32 tests in 5 files. No model metrics and no calibration metrics. Live model, feed and Supabase tests are opt-in and were not executed ([test_live_optional.py](file:///home/user/Ai_fake_news/backend/tests/test_live_optional.py)) |
| 16 Final integration & docs ("evaluation results") | P | Docs exist (README, PROJECT_STATUS, 30-page report). There are no model evaluation results |

**System architecture table (Syn printed p.11)**
- Data Source / Processing (Python, feedparser, cleaning) / Storage / API → **M**.
- AI Layer "Transformer models, sentiment, summarization, 8-dimension" → **P**: no summarization model, and the eight dimensions are rule-based.
- Presentation (Next.js, React, Tailwind, Recharts) → **M**. The table implies the API layer sits between storage and presentation; in the code, presentation reads storage directly (**D**).

**8-dimension table (Syn Phase 8 p.9 and §3.4 p.12) vs `dimension_service.py`**
| Dimension | Synopsis method | Code method | Class |
|---|---|---|---|
| Sentiment | sentiment-analysis output | DistilBERT positive score ×100 (clamped 5–95) when the model runs; otherwise ±9 per positive/negative cue word ([dimension_service.py:172-176](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L172), [analysis_pipeline.py:77-87](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L77)) | M/D |
| Bias | loaded / one-sided wording | `LOADED` word list (12 terms), −6 if there is no attribution | M (lexical) |
| Objectivity | balanced/neutral/factual-looking | `SUBJECTIVE` adjective list (17 terms) | M (lexical) |
| Readability | sentence/word complexity | Flesch Reading Ease; None when only a headline is available | M |
| Propaganda | loaded/exaggerated/manipulative patterns | 11 clickbait regexes + shouting capitals | M (lexical) |
| Headline accuracy | headline vs main content | share of headline key terms present in the **RSS excerpt** (not the article body); None with no excerpt | D (excerpt, not article) |
| Source credibility | "recognised publisher information **and source history** where available" | 14-entry hand-curated `PUBLISHER_REPUTATION` table (e.g. bbc 93, cnn 86, yahoo 78); None if the publisher is absent — [dimension_service.py:36-40,119-124](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L36) | P (no source history) |
| Content quality | structure, completeness, clarity, consistency | length (capped at 600 chars) + sentence count of the **excerpt** | D (excerpt length only) |
- Dimensions are 0–100 integers with an explanation each. A dimension that cannot be measured is `None`, never a placeholder ([dimension_service.py:20-21 docstring](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L20)).
- Interpretation section ("scores are indicators … Objectivity is presentation style … Source Credibility not a permanent rating … Needs Verification state") → **M**. Both PDFs carry the disclaimer and method note ([report_service.py:24-37](file:///home/user/Ai_fake_news/backend/services/report_service.py#L24); [dimensions.ts:29-34](file:///home/user/Ai_fake_news/frontend/src/lib/dimensions.ts#L29)).

**Functional requirements (Syn printed p.13)**
- Input: RSS feeds, fields, English → **M**.
- Processing: validate/clean **M**; normalise/detect duplicates **M** (exact only); credibility + sentiment **M**; "concise AI summary" **D**; group related **M**; eight dimensions **M**; uncertainty/Needs Verification **M**.
- Output: cards **M**; credibility/confidence **M** (confidence is "Not reported" when the classifier did not run — [article/[id]/page.tsx:128](file:///home/user/Ai_fake_news/frontend/src/app/article/[id]/page.tsx#L128)); sentiment **M/D**; "AI-generated short summary" **D**; cross-source **M**; eight dimensions with descriptions **M**; search/filter **M**; analytics **M**; PDF **M**; original link **M**.

**Non-functional requirements (Syn printed p.14)**
- Usability **M**.
- Performance **M** (feed timeout 15 s, max 8 entries per feed — [rss_fetcher.py:49-50](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L49); lazy model load).
- Reliability **M** (per-feed try/except, scheduler lock).
- Maintainability **M**.
- Scalability **M** (source dict; modular services).
- Transparency **M**: "uncalibrated" wording, explanations, disclaimers.

**Proposed user workflow (Syn printed p.14), steps 1–11**
- Steps 1–4, 6–8, 10 → **M**.
- Step 5 "short AI summary" → **D**.
- Step 7 "for supported content" → **M** (dimensions are None when not measurable).
- Step 9 "frontend retrieves the processed information through FastAPI" → **D** (Next.js reads Supabase directly; [repository.ts:21-27](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L21)).
- Step 11 PDF → **M**.

**Example analysis display (Syn printed p.14)**: "80/100 Sentiment, 85/100 Bias, 90/100 Objectivity … accompanied by short explanations" → **M** in form (0–100 plus explanation, `DimensionTable.tsx`, radar chart). The numbers are illustrative only. In the code, Sentiment 50 = neutral, so "80/100 Sentiment" would mean a clearly positive tone, not a "good" score.

**Cross-source view (Syn printed p.15)**: "compare headlines, summaries and analysis results; agreement is not proof" → **M/P**. Headlines and analysis are compared, and the code explicitly says agreement ≠ truth ([clustering_service.py:10-11](file:///home/user/Ai_fake_news/backend/services/clustering_service.py#L10)). Summaries are usually missing because excerpts are short.

**Testing and evaluation plan (Syn printed pp.15–16)**
| Plan item | Class | Evidence |
|---|---|---|
| 1 Functional testing (fetch errors, malformed records, repeated/similar articles) | M | [test_rss_fetcher.py](file:///home/user/Ai_fake_news/backend/tests/test_rss_fetcher.py), [test_db_service.py](file:///home/user/Ai_fake_news/backend/tests/test_db_service.py) (same batch twice; URL with tracking params) |
| 2 AI model evaluation: accuracy/precision/recall/F1 on a labelled dataset; sentiment on test examples | N (metrics) / P (sanity check) | [validate_models.py:16-30](file:///home/user/Ai_fake_news/backend/scripts/validate_models.py#L16): 4 fake-news and 2 sentiment hand-picked examples, printed by eye, "not a benchmark". Unit tests use a **fake** pipeline ([test_ai_service.py](file:///home/user/Ai_fake_news/backend/tests/test_ai_service.py)). The real-model test is opt-in and was never run (`RUN_MODEL_TESTS=1`, [test_live_optional.py:12](file:///home/user/Ai_fake_news/backend/tests/test_live_optional.py#L12)) |
| 3 Calibration evaluation | N | no reliability diagram, ECE or Brier score anywhere (grep "calibrat" only finds "uncalibrated" disclaimers) |
| 4 Summarization evaluation (relevance, coverage, readability, consistency) | N | only a unit test that a summary needs 3 sentences ([test_analysis_pipeline.py:63](file:///home/user/Ai_fake_news/backend/tests/test_analysis_pipeline.py#L63)) |
| 5 Cross-source evaluation (same event vs similar wording/different event) | P | tests cover same event across publishers, same publisher only, a time gap, the window and accents ([test_clustering_service.py:13-55](file:///home/user/Ai_fake_news/backend/tests/test_clustering_service.py#L13)). There is **no** "similar wording, different event" negative test. content.html admits two separate Gaza strike reports were wrongly grouped in the test run |
| 6 8-dimension evaluation (consistency, explanation matches indicator) | P | Python/TS parity on 10 reference vectors ([shared/scoring_vectors.json](file:///home/user/Ai_fake_news/shared/scoring_vectors.json), [test_dimension_service.py](file:///home/user/Ai_fake_news/backend/tests/test_dimension_service.py), [scoringParity.test.ts](file:///home/user/Ai_fake_news/frontend/src/lib/scoringParity.test.ts)). No human usefulness study |
| 7 System testing (end-to-end, PDF, search, charts, links) | P | PDF tests ([test_report_service.py](file:///home/user/Ai_fake_news/backend/tests/test_report_service.py), [pdfReportGenerator.test.ts](file:///home/user/Ai_fake_news/frontend/src/lib/pdfReportGenerator.test.ts)); API tests ([test_api.py](file:///home/user/Ai_fake_news/backend/tests/test_api.py)). The E2E run (41 stored, 5 groups) is reported only in docs; the live tests were not executed ([PROJECT_STATUS.md](file:///home/user/Ai_fake_news/docs/PROJECT_STATUS.md) "Remaining" item 5) |

**Expected outcome (Syn printed p.17)**
- 30-min collection **M**; duplicates reduced **M**; groups **M**; eight dimensions **M**; Needs Verification **M**; search, filter and analytics **M**; PDF **M**; original links **M**.
- "Each supported article will receive sentiment and credibility-risk/confidence" → **P**. Articles with too little evidence get `risk_score=None`, label "Unavailable"/"not assessed" ([analysis_pipeline.py:110-112,123](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L110)). Confidence is None whenever the classifier did not run.
- "Concise AI-generated summary" → **D**.
- "Demonstrate the importance of evaluating model confidence" → **P**: the importance is argued and the output labelled, but nothing was evaluated.

**Limitations (Syn printed p.17)**: all six still hold. The one about "AI-generated summaries may omit details" should be reworded for extractive summaries, which select sentences and so cannot invent content, but can omit context. The code adds further real limitations: short RSS excerpts (<150 chars → flagged), a lexicon-based approach, the small reputation table, and grouping false positives.

**Timeline / Deliverables (Syn printed p.18)**
- Deliverables: pipeline **M**; deduplicated dataset **M**; credibility and sentiment **M**; "AI short summarization" **D**; "Calibrated credibility interpretation" **P/N**; cross-source **M**; eight dimensions **M**; dashboard and analytics **M**; PDF **M**; "testing results and documentation" **M** for software tests, **N** for model evaluation results.
- Weeks 4, 6, 7 and 12 promise "initial evaluation", "summarization … evaluation", "calibration … evaluation" and "model evaluation". None of these were produced. Week 6 (summarization) and Week 7 (calibration) were delivered as the extractive summary and the uncertainty-band interpretation.

**Bibliography (Syn printed p.20)**: the references used match the code (HF Transformers, mrm8488 bert-tiny, FastAPI, Supabase, Next.js, React, Tailwind, Recharts, PyTorch, APScheduler, Pytest).
- Missing from the synopsis bibliography but used in the code: the DistilBERT SST-2 model card, feedparser, ReportLab, jsPDF, Vitest, the GDELT/GNews/Google News RSS APIs and the Flesch reading-ease formula. content.html adds the DistilBERT and Devlin/Sanh papers.

### Inferences
- The gaps cluster in one place: anything that needs a **labelled dataset or a generative model** (abstractive summaries, calibration, P/R/F1) was not done. Everything that is deterministic software was done and tested.
- Short RSS excerpts limit the system more than any model does. They cause most articles to be flagged Needs Verification, most summaries to be absent, and Headline Accuracy and Content Quality to describe the excerpt, not the article.
- Recommended framing for the final report: "Planned → Delivered → Gap/Reason" per item, rather than rewriting synopsis promises as achieved.

### Gaps
- I could not run the models, the live feeds or Supabase. Whether bert-tiny's LABEL_1 = fake mapping is correct on this machine remains unverified in code (configurable via `FAKE_NEWS_FAKE_LABEL`).
- No stored DB snapshot is in the repo. The real share of articles with summaries, scores or Needs Verification can only be estimated from docs and screenshots (`docs/report/demo_feed_items.json` exists but was not analysed in depth).

---

## Q2. UML diagrams: synopsis diagrams vs code, and the current `gen_diagrams.py` diagrams vs code

### Takeaway
All five synopsis UML diagrams are conceptual and differ from the code:
- The sequence diagram routes reads through FastAPI; the code does not.
- The class diagram shows Source, Summary and Report entities and attributes that do not exist (`credibilityIndicator`, `confidenceLevel` as a separate class attribute, `generatedAt`, `filePath`, `reportId`).
- The activity diagram puts summary and cross-source comparison in the per-article chain; grouping actually runs once per batch.
- The object diagram uses invented values.

The regenerated diagrams in `docs/report/gen_diagrams.py` track the code closely. They have a few remaining inaccuracies:
- Methods drawn on classes are really module-level functions.
- The browser jsPDF path and the live-RSS/external-search paths are missing.
- The architecture arrow passes from the API layer to presentation.
- The sequence diagram shows a single-row select, whereas the code first loads a cached 500-row edition.

### Cited Findings

**Use case diagram (synopsis Fig 3.3(a), PDF p.15)**
- Synopsis elements:
  - Actors: User, Scheduler (APScheduler).
  - Scheduler use cases: Collect RSS Feeds; Preprocess & Deduplicate; Run AI Analysis Pipeline (Credibility, Sentiment, Summary, 8-Dimension, Cross-Source).
  - User use cases: View News Dashboard; Search & Filter; View Article Details & AI Summary; View Credibility & Sentiment Indicators; View 8-Dimension Analysis; Compare Cross-Source Coverage; View Analytics Dashboard; Generate PDF Report — [Syn Fig 3.3(a)](file:///root/.claude/uploads/1906c76c-bbe3-5864-8def-44e8386987c9/7fa5cf3c-synopsiswithdiagram_1.pdf).
- Vs code:
  - All use cases exist.
  - "AI Summary" is extractive and often absent (**D**).
  - Missing use cases that exist in code (**X**):
    - Register display name: the name-only modal posts to `/api/auth/profile`, which inserts into `named_visitors` and stores the name in localStorage — [profile/route.ts:1-60](file:///home/user/Ai_fake_news/frontend/src/app/api/auth/profile/route.ts#L1), [NameAuthModal.tsx:27-42](file:///home/user/Ai_fake_news/frontend/src/components/ui/NameAuthModal.tsx#L27).
    - Search external news (Google News/GNews/GDELT): [api/search/external/route.ts](file:///home/user/Ai_fake_news/frontend/src/app/api/search/external/route.ts).
    - Analyse custom text: `POST /api/analyze` — [router.py:64-75](file:///home/user/Ai_fake_news/backend/api/router.py#L64).
    - Trigger ingestion with a token: `POST /api/ingest` — [router.py:178-187](file:///home/user/Ai_fake_news/backend/api/router.py#L178).
  - Cross-source grouping is a separate batch step, not part of the per-article AI pipeline.
- Current gen_diagrams `use_case()` ([gen_diagrams.py:214-232](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L214)):
  - Scheduler: Collect RSS feeds; Remove duplicates; Analyse articles; Group cross-source events.
  - Reader: Register display name; View news dashboard; Search & filter; View article analysis; Compare coverage; View analytics; Download PDF report; Analyse custom text (API).
  - This **matches the code**. It still omits external news search and token-triggered ingestion (minor).

**Class diagram (synopsis Fig 3.3(b), PDF p.16)**
- Synopsis classes:
  - Source{name, feedUrl, **credibilityIndicator: String**; fetchArticles()}
  - Article{id:int, title, url, publishedDate, category, content; getSummary(), getAnalysis()}
  - CredibilityResult{riskScore, **confidenceLevel**, label}
  - SentimentResult{label, score: float}
  - Summary{text, **generatedAt: Date**}
  - ArticleGroup{groupId:int, articles; addArticle()}
  - Report{**reportId:int, articleId:int, generatedDate, filePath**; generatePDF(): File}
  - DimensionAnalysis{8 float scores}
  - Associations: Source 1–many Article; Article 1–1 each result class; Article many–1 ArticleGroup; Report many–1 Article.
- Vs code:
  - **No Source entity or table.** The publisher is a text column `source_domain`. Feeds are a Python dict `RSS_SOURCES` ([rss_fetcher.py:25](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L25)).
  - `credibilityIndicator: String` → **D**: an integer 0–100 from `PUBLISHER_REPUTATION`, or None ([dimension_service.py:36-40](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L36)). It is stored per article as `dimensions.source_credibility`, not per source.
  - `Article.id: int` → **D**: a UUID (`gen_random_uuid()`, [schema.sql:13](file:///home/user/Ai_fake_news/backend/db/schema.sql#L13)). `title` is UNIQUE. `content` → `content_summary` (the RSS excerpt only).
  - `getSummary()/getAnalysis()` → no OO methods; `analyze_article()` is a module function ([analysis_pipeline.py:90](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L90)).
  - `CredibilityResult.confidenceLevel` → column `confidence_level` = the classifier's top-class softmax (uncalibrated). It is None if the model did not run. Code also has `model_fake_probability`, `needs_verification`, `analysis_status`, `analysis_method`, `model_version` and `ai_reasoning`, which are not in the synopsis ([analysis_pipeline.py:154-172](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L154); [02_integrity_and_security.sql:13-19](file:///home/user/Ai_fake_news/backend/db/02_integrity_and_security.sql#L13)).
  - `SentimentResult.score: float` → the sentiment dimension is an int 0–100; the label is lowercase positive/negative/neutral.
  - `Summary.generatedAt` → **N**: there is no summary timestamp. Code has `ai_summary` + `summary_method`; the closest field is the article-level `analyzed_at`.
  - `ArticleGroup` → no table. `group_id` is a string `"ev-<uuid>"` plus `event_title` on each article; groups are assembled at read time ([clustering_service.py:122-128](file:///home/user/Ai_fake_news/backend/services/clustering_service.py#L122); [db_service.py:39-64](file:///home/user/Ai_fake_news/backend/services/db_service.py#L39)). There is no `addArticle()`.
  - `Report` → **D**: not persisted, so there is no reportId, generatedDate or filePath. The PDF is streamed as bytes (`build_article_report() -> bytes`, [report_service.py:58](file:///home/user/Ai_fake_news/backend/services/report_service.py#L58); [router.py:171-175](file:///home/user/Ai_fake_news/backend/api/router.py#L171)) or generated in the browser.
  - `DimensionAnalysis` floats → nullable ints plus an `explanations` map, stored in one JSONB column.
- Current gen_diagrams `class_diagram()` ([gen_diagrams.py:172-211](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L172)):
  - Source{name, feedUrl, category; fetch_articles()}
  - Article{id: UUID, title {unique}, sourceUrl, excerpt, category, publishedAt; analyze_article()}
  - ArticleGroup{groupId: String, eventTitle, publishers; cluster_articles()}
  - CredibilityResult{riskScore, label, classifierFakeScore, classifierConfidence, needsVerification, status}
  - DimensionAnalysis{8 int [0..1], explanations; rule_risk()}
  - SentimentResult{label, score:int}
  - Summary{text, method}
  - Report{articleId, format A4 PDF; build_article_report()}
  - Composition from Article; Report «uses» Article.
  - Close to the code. Remaining caveats:
    - `fetch_articles`, `analyze_article`, `cluster_articles`, `rule_risk` and `build_article_report` are module-level functions, not methods of those classes ([rss_fetcher.py:128](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L128), [clustering_service.py:85](file:///home/user/Ai_fake_news/backend/services/clustering_service.py#L85), [dimension_service.py:144](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L144)).
    - Source is conceptual (no table), which content.html §3.2 states.
    - `Source.category` is the config group.
    - Missing `reasoning`, `modelVersion`, `analysisMethod` and `publisher` on Article.
    - `Source.fetch_articles()` actually fetches all sources at once.

**Sequence diagram (synopsis Fig 3.3(c), PDF p.17)**
- Synopsis messages:
  1. User→Frontend Open Article
  2. Frontend→FastAPI `GET /api/article/{id}`
  3. FastAPI→DB Query Article + AI Results
  4. Return Record
  5. JSON Response
  6. Render
  7. Click "Generate Report"
  8. Frontend→FastAPI `GET /api/report/{id}`
  9. Generate PDF
  10. Return PDF File
  11. Download
- Vs code:
  - Steps 2–5 → **D**. The article page is a server component calling `getArticle(id)`. That calls `getEdition()` → `loadDatabaseArticles()`: `supabase.from('articles').select('*').order(...).limit(500)`, cached 60 s. If the id is not in the edition, it runs `select('*').eq('id', id)` against Supabase ([repository.ts:135-151,330-349](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L330)).
  - FastAPI `/api/article/{id}` exists ([router.py:108-117](file:///home/user/Ai_fake_news/backend/api/router.py#L108)) but the frontend does not call it. Next.js also has its own `/api/article/[id]` route handler that reads through the same repository, not through FastAPI ([frontend api/article/[id]/route.ts](file:///home/user/Ai_fake_news/frontend/src/app/api/article/[id]/route.ts)).
  - Steps 8–10 → **P/D**:
    - The server PDF link is `${NEXT_PUBLIC_API_URL}/api/v1/report/{id}`. It is only rendered if the backend URL is configured **and** the article came from the DB.
    - It is a plain `<a href download>`, so the browser calls FastAPI directly; the frontend does not proxy it.
    - Otherwise, or as "Export in browser", jsPDF generates the PDF client-side with no server round trip ([ReportDownload.tsx:11-40](file:///home/user/Ai_fake_news/frontend/src/components/analysis/ReportDownload.tsx#L11)).
    - Both `/api/report/{id}` and `/api/v1/report/{id}` are mounted ([main.py:73-75](file:///home/user/Ai_fake_news/backend/main.py#L73)).
- Current gen_diagrams `sequence()` ([gen_diagrams.py:235-270](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L235)):
  - Lifelines: Reader, Next.js server, FastAPI backend, Supabase.
  - Messages: 1 GET /article/{id} → 2 "select * from articles where id = {id}" → 3 row → 4 rendered page → 5 Reader→FastAPI GET /api/report/{id} → 6 get_article_by_id → 7 row → 8 build_article_report() → 9 application/pdf.
  - Mostly correct (direct Supabase read; browser→FastAPI for the PDF). Caveats:
    - Message 2 is simplified: normally the cached 500-row edition query is used and the by-id select is only a fallback.
    - The frontend actually uses `/api/v1/report/{id}`.
    - The alternative jsPDF path and its precondition (`NEXT_PUBLIC_API_URL` set, database origin) are not shown.
    - The live-feed fallback is not shown.

**Activity diagram (synopsis Fig 3.3(d), PDF p.18)**
- Synopsis flow: Start (every 30 min) → Fetch RSS → Validate & Clean → [Duplicate? yes→Discard] → Credibility Classification → Sentiment → **Generate AI Summary → Cross-Source Comparison** → 8-Dimension Analysis → [Confidence sufficient? no→Mark "Needs Verification"] → Store Results.
- Vs code (`fetch_and_store_job`, `store_articles_in_db`, `analyze_article`):
  - The per-feed loop includes a failure branch, not shown in the synopsis ([rss_fetcher.py:138-147](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L138)).
  - Two-stage dedup: within the batch, then against the DB **before** analysis ([db_service.py:119-123](file:///home/user/Ai_fake_news/backend/services/db_service.py#L119)).
  - Per-article order is **different**. The eight rule dimensions come **first**, then the classifier and sentiment models, then the sentiment dimension is replaced by the model score, then rule risk, combined risk, label and flags, and the extractive summary comes **last** ([analysis_pipeline.py:92-153](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L92)).
  - A risk-score decision ("≥65% of risk weight scoreable?") is missing from the synopsis ([dimension_service.py:144-160](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L144)).
  - Needs Verification is not a single "confidence sufficient?" test. It is any of five conditions (next section).
  - **Cross-source comparison is not per-article.** `update_groups()` re-clusters the last 48 h once, after all inserts ([scheduler.py:37-40](file:///home/user/Ai_fake_news/backend/services/scheduler.py#L37); [db_service.py:142-160](file:///home/user/Ai_fake_news/backend/services/db_service.py#L142)).
  - Flagged articles are still stored, with the flag.
- Current gen_diagrams `activity()` ([gen_diagrams.py:273-325](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L273)):
  - Feed loop with a 15 s timeout and failure branch; in-batch dedup; "Already in database?"; "Score 8 dimensions (rules); run models if available"; "≥65% of risk weight?"; Low/Moderate/High vs "not assessed"; Needs Verification (footnote lists the five rules); insert; loop; "Re-group recent articles (TF-IDF)".
  - **Matches the code.** The only omission is the extractive summary step (part of `analyze_article`), which is not drawn.

**Object diagram (synopsis Fig 3.3(e), PDF p.19)**
- Synopsis values:
  - source1{name "TechNews Daily", credibilityIndicator "High"}
  - article1{id 101, "New AI Regulation Proposed", Technology, 2026-09-10}
  - credibility1{riskScore 0.15, confidenceLevel 0.82, label "Low Risk"}
  - sentiment1{Neutral, 0.58}
  - summary1{"Govt proposes new AI oversight rules...", generatedAt 2026-09-10 14:32}
  - dimension1{72/80/85/76/88/79/83/81}
- Vs code:
  - **Illustrative and inconsistent with the code's scales.** "TechNews Daily" is not in the feed list or the reputation table, so in the code its source_credibility would be **None**.
  - Ids are UUIDs.
  - Sentiment score is 0–100 with 50 = neutral; 0.58 on a 0–1 scale would not exist as such.
  - Synopsis sentiment=72 would be labelled "positive" by `sentiment_from_score` (≥60), contradicting label "Neutral" in the same diagram ([dimension_service.py:140-141](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L140)).
  - The summary text is paraphrased ("Govt proposes…"), which the extractive method cannot produce.
  - `generatedAt` does not exist.
- Current gen_diagrams `object_diagram()` ([gen_diagrams.py:144-169](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L144)):
  - bbc:Source{name BBC, category general, reputation 93}
  - a1:Article{Huawei … , 2026-11-25 02:59 UTC, excerptLength 52, groupId ev-d73d8a5a…}
  - a2:Article{AlJazeera}
  - g1:ArticleGroup{[BBC, AlJazeera]}
  - c1:CredibilityResult{riskScore 0.15, Low Risk, classifierFakeScore null, needsVerification true, status partial}
  - d1{sentiment 50, bias 84, objectivity 92, readability 66, propaganda 95, headline 45, sourceCredibility 93, contentQuality 44}
  - s1{neutral, 50 (rules)}
  - I recomputed the values with the code's formulas and they are **internally consistent**:
    - rule risk = 1 − (93·.35 + 95·.20 + 92·.15 + 84·.15 + 45·.15)/100 = 1 − 0.847 ≈ 0.15.
    - bias 84 = 90 − 6 (no attribution).
    - content quality 44 = 35 + 52/12 + 1·5.
    - Needs Verification is true because the excerpt is 52 < 150 chars.
    - status "partial" because the models were unavailable.
    - Coincidence to note: riskScore 0.15 equals the synopsis' illustrative value.
  - The caption states it is from a real run with models not installed ([content.html §3.1](file:///home/user/Ai_fake_news/docs/report/content.html)).

**Current architecture / modules diagrams**
- `architecture()` ([gen_diagrams.py:123-141](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L123)) draws six stacked layers with arrows Data source → Collection → Analysis → Storage → API → Presentation. The data source lists only the backend feeds (BBC, CNN, Al Jazeera, Yahoo).
  - The single arrow API → Presentation suggests the frontend reads through FastAPI. The Presentation label says "read-only Supabase key", which half-corrects this.
  - Missing: the live publisher-RSS fallback and external search (Google News/GNews/GDELT) feeding the Next.js server directly.
- `modules()` ([gen_diagrams.py:328-351](file:///home/user/Ai_fake_news/docs/report/gen_diagrams.py#L328)) matches the file layout. It omits `liveNewsService.ts`, `externalSearch.ts`, `clustering.ts` (listed under Grouping), `search.ts` and the Next.js API route handlers.

### Inferences
- In the final report, keep the synopsis diagrams out of the "as built" chapter, or label them "planned (synopsis)" next to the as-built `gen_diagrams.py` versions, with a short delta list under each.
- The sequence diagram is the most important correction: a viva examiner comparing it to the code will see that FastAPI is not on the read path.

### Gaps
- I did not re-render the SVGs. The statements about the current diagrams come from the generator source, not from the PNG/SVG images embedded in `docs/Project_Report.pdf`.

---

## Q3. Specific known gaps: confirmed or refuted

### Takeaway
Every suspected gap is **confirmed**:
- Extractive-only summaries.
- No calibration.
- No P/R/F1 evaluation (validate_models.py is a 6-example eyeball check).
- No Source.credibilityIndicator.
- Needs Verification uses five heuristic conditions rather than a confidence threshold alone.
- Scheduled every 30 min, not real-time.

The technology list is honoured apart from "AI summarization" and the three-class sentiment model. The documented runs were also rules-only (models not installed). So the live system has never been shown working with BERT in the evidence the repo holds.

### Cited Findings
- **AI-generated summaries** → CONFIRMED as a gap.
  - `extractive_summary` "Nothing is generated or paraphrased" — [analysis_pipeline.py:52-74](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L52).
  - The frontend maps `summary_method === 'abstractive'` → "ai", which never happens, so the "AI executive summary" label can never show for DB rows — [repository.ts:107-109](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L107); [article/[id]/page.tsx:45,114](file:///home/user/Ai_fake_news/frontend/src/app/article/[id]/page.tsx#L114).
  - PROJECT_STATUS: "Abstractive 'AI-generated' summaries: replaced by extractive summaries (honestly labelled)" — [PROJECT_STATUS.md](file:///home/user/Ai_fake_news/docs/PROJECT_STATUS.md).
  - Recommended wording: "Summaries are extractive: the two most representative sentences of the publisher's excerpt are selected by word frequency. They are produced only when the excerpt has at least three sentences. Abstractive (generative) AI summarisation, planned in Phase 5 of the synopsis, was not implemented."
- **Better-calibrated credibility / calibration evaluation** → CONFIRMED not implemented.
  - "Softmax scores are reported as raw, uncalibrated model outputs" — [ai_service.py:22](file:///home/user/Ai_fake_news/backend/services/ai_service.py#L22).
  - "These are heuristic indicators, not calibrated probabilities" — [analysis_pipeline.py:20](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L20).
  - Reasoning text: "(raw softmax output, not a calibrated probability)" — [analysis_pipeline.py:116-118](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L116).
  - Recommended wording: "Calibration was not performed because no labelled evaluation set was assembled. Instead, the interpretation was made more careful: classifier scores are shown as uncalibrated, combined with a transparent rule-based risk, and an uncertainty band of 0.40–0.60 plus a low-confidence threshold (<0.60) raise Needs Verification. Temperature scaling with an ECE/reliability evaluation is future work."
- **Accuracy/precision/recall/F1 on a labelled dataset** → CONFIRMED not done.
  - `validate_models.py` has 4 fake-news and 2 sentiment examples and says "illustrative, not a benchmark: no accuracy figure … should be reported" — [validate_models.py:9-30](file:///home/user/Ai_fake_news/backend/scripts/validate_models.py#L9).
  - content.html §5: "No accuracy, precision or recall figures are reported".
  - Recommended wording: "Model-level evaluation (accuracy, precision, recall, F1 and calibration) on a labelled dataset was planned but not carried out. The models could not be downloaded in the test environment, and no labelled news dataset was prepared. `scripts/validate_models.py` only prints raw outputs on six hand-picked examples to confirm the label mapping."
- **Source.credibilityIndicator** → CONFIRMED absent.
  - There is no sources table or per-source attribute. Each article gets `dimensions.source_credibility` = an integer from a 14-entry table, or None — [dimension_service.py:36-40,235](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L36).
  - Recommended wording: "Source credibility is a per-article dimension (0–100) looked up from a hand-curated table of 14 established newsrooms. Unknown publishers are left unscored. No per-source history is kept."
- **"Needs Verification when confidence insufficient"** → CONFIRMED as different (broader).
  - Backend conditions: no risk score; risk score in 0.40–0.60; excerpt < 150 chars; classifier confidence < 0.60; |p_fake − rule_risk| ≥ 0.50 — [analysis_pipeline.py:124-135](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L124).
  - The frontend live-feed/external path uses only three conditions (score null, ambiguous band, thin excerpt) because there is no classifier there — [scoring.ts:262](file:///home/user/Ai_fake_news/frontend/src/lib/scoring.ts#L262); [dimension_service.py:276](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L276).
  - The frontend also forces Needs Verification when the label is "Unavailable" — [repository.ts:93-95](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L93).
  - Consequence (from content.html §7): most RSS items are < 150 chars, so most are flagged.
- **"Real-time" vs 30-minute schedule** → the synopsis itself says near-real-time every 30 min → **M** ([scheduler.py:25](file:///home/user/Ai_fake_news/backend/services/scheduler.py#L25)).
  - The live-feed fallback refreshes on a 2-minute cache ([liveNewsService.ts:15](file:///home/user/Ai_fake_news/frontend/src/lib/liveNewsService.ts#L15)). The DB edition is cached for 60 s ([repository.ts:31](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L31)).
  - A code comment calls Google News RSS "real-time" ([externalSearch.ts:10](file:///home/user/Ai_fake_news/frontend/src/lib/externalSearch.ts#L10)). Avoid repeating that word in the report.
- **Technologies vs requirements.txt / package.json**
  - BERT ✓ (bert-tiny, about 4.4M params per content.html); sentiment model ✓ (binary SST-2); AI summarization ✗; APScheduler ✓; Recharts ✓; Tailwind ✓ (v4); FastAPI ✓; Supabase ✓; PyTorch ✓ — [requirements.txt](file:///home/user/Ai_fake_news/backend/requirements.txt), [package.json](file:///home/user/Ai_fake_news/frontend/package.json).
- **Models actually executed?** Not in any documented run.
  - content.html §5 Table 5.2: "Real model inference RUN_MODEL_TESTS=1 — Not executed: model download blocked".
  - The /api/analyze example and the object diagram are "rules only, models not installed".
  - PROJECT_STATUS Remaining items 3–5 ask the team to install the models and run validation.

### Inferences
- The final report should say plainly that the BERT/DistilBERT integration is implemented and unit-tested with fake pipelines, and that the documented screenshots and runs were produced in rules-only mode. If the team runs the models before submission, those screenshots should be refreshed.

### Gaps
- Whether the team's own machine has since run the models (and whether the Supabase data contains `analysis_method = 'model+rules'` rows) cannot be determined from the repo.

---

## Q4. Features in the code that the synopsis does not mention

### Takeaway
The code goes beyond the synopsis in eight areas:
1. A live-RSS fallback edition with rule-based scoring in TypeScript.
2. External news search (Google News RSS / GNews / GDELT).
3. Name-only reader registration.
4. A browser PDF generated with jsPDF, alongside the server ReportLab PDF.
5. `POST /api/analyze`.
6. `POST /api/ingest` with a token.
7. Rate limiting, a CORS allow-list and RLS hardening.
8. Python/TypeScript scoring parity tests, analysis provenance columns, and the "Daily Signal" newspaper UI with sections.

These should appear in the report as additions beyond the synopsis.

### Cited Findings
- **Live-RSS fallback with rule-based scoring.** When Supabase is unconfigured or empty, `getEdition()` uses `getLiveEdition()`. Publisher feeds (Google News topic feeds, BBC, Guardian, Hindu, NDTV, Indian Express, Mint, Al Jazeera, TechCrunch) are scored by `analyseText` in TS with no models (`analysisMethod: 'heuristic'`) — [repository.ts:169-184](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L169); [liveNewsService.ts:1-16,142-163](file:///home/user/Ai_fake_news/frontend/src/lib/liveNewsService.ts#L1); [sections.ts:17-74](file:///home/user/Ai_fake_news/frontend/src/lib/sections.ts#L17). Grouping is recomputed client-side with `clusterArticles` ([clustering.ts](file:///home/user/Ai_fake_news/frontend/src/lib/clustering.ts)). Note: the Google News feeds are aggregators, not single publishers.
- **External news search** — `GET /api/search/external?q=` (Next.js route). Providers are Google News RSS search (keyless), GNews (when `GNEWS_API_KEY` is set) and the GDELT DOC 2.0 fallback, with a GDELT request queue / minimum gap. Results with enough text are analysed with the eight-dimension rules — [externalSearch.ts:1-40,126-186,257](file:///home/user/Ai_fake_news/frontend/src/lib/externalSearch.ts#L1); [search/external/route.ts](file:///home/user/Ai_fake_news/frontend/src/app/api/search/external/route.ts).
- **Name-only reader registration** — `named_visitors` table (name UNIQUE, 1–40 chars), public read+insert RLS, modal plus localStorage — [schema.sql:30-34](file:///home/user/Ai_fake_news/backend/db/schema.sql#L30); [02_integrity_and_security.sql:49-52,68-70](file:///home/user/Ai_fake_news/backend/db/02_integrity_and_security.sql#L49); [profile/route.ts](file:///home/user/Ai_fake_news/frontend/src/app/api/auth/profile/route.ts). There is no password authentication; `user_profiles` (linked to auth.users) exists in SQL but nothing in the frontend or backend uses it.
- **Browser PDF via jsPDF** — [pdfReportGenerator.ts:1-30](file:///home/user/Ai_fake_news/frontend/src/lib/pdfReportGenerator.ts#L1); [ReportDownload.tsx:18-40](file:///home/user/Ai_fake_news/frontend/src/components/analysis/ReportDownload.tsx#L18).
- **`POST /api/analyze`** — analyses arbitrary text and stores nothing; 1–20,000 chars; validation via pydantic — [router.py:29-75](file:///home/user/Ai_fake_news/backend/api/router.py#L29).
- **`POST /api/ingest`** — disabled unless `INGEST_TOKEN` is set; uses `hmac.compare_digest` — [router.py:178-187](file:///home/user/Ai_fake_news/backend/api/router.py#L178).
- **`GET /api/health`** — model state and last ingestion summary — [router.py:53-61](file:///home/user/Ai_fake_news/backend/api/router.py#L53).
- **Rate limiting** — in-memory, 30 requests/min per IP on `/analyze` and `/report/` — [main.py:21-24,52-64](file:///home/user/Ai_fake_news/backend/main.py#L21).
- **CORS allow-list** — [main.py:18-19,43-49](file:///home/user/Ai_fake_news/backend/main.py#L43). The generic 500 handler hides internal errors — [main.py:67-70](file:///home/user/Ai_fake_news/backend/main.py#L67).
- **RLS hardening / integrity migration** — public key may only SELECT articles; public insert/update policies are dropped; the "Low Risk" default is dropped; CHECK constraints are added; legacy rows are marked — [02_integrity_and_security.sql:8-66](file:///home/user/Ai_fake_news/backend/db/02_integrity_and_security.sql#L8).
- **Analysis provenance** — `analysis_status` (complete/partial/unavailable/legacy), `analysis_method`, `model_version`, `analyzed_at`, `model_fake_probability` — [02_integrity_and_security.sql:13-19](file:///home/user/Ai_fake_news/backend/db/02_integrity_and_security.sql#L13); `scripts/reanalyze.py` re-scores legacy rows ([reanalyze.py](file:///home/user/Ai_fake_news/backend/scripts/reanalyze.py)).
- **Python/TypeScript scoring parity** — `dimension_service.py` is a "line-by-line port of scoring.ts", checked against `shared/scoring_vectors.json` in both suites — [dimension_service.py:1-9](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L1).
- **Risk combination formula** (rule-risk weights 0.35/0.20/0.15/0.15/0.15, 65% minimum weight, mean with p_fake) — [dimension_service.py:59-68,144-160](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L59). The synopsis never specifies how risk is computed.
- **Newspaper UI** ("The Daily Signal") with sections World, India, Politics, Business, Technology, Science, Culture, Sports, plus Coverage and Analysis pages; infinite feed; radar chart with the edition average — [sections.ts](file:///home/user/Ai_fake_news/frontend/src/lib/sections.ts), [SectionNav.tsx](file:///home/user/Ai_fake_news/frontend/src/components/layout/SectionNav.tsx), [globals.css:1-5](file:///home/user/Ai_fake_news/frontend/src/app/globals.css#L1). Science and Culture only have stories in live-feed mode, since the backend categories are sports/politics/business/technology/general ([rss_fetcher.py:25-47](file:///home/user/Ai_fake_news/backend/services/rss_fetcher.py#L25); [sections.ts:125-132](file:///home/user/Ai_fake_news/frontend/src/lib/sections.ts#L125)).
- **Extra analytics** beyond the synopsis: dimension averages, hourly timeline, coverage width (publishers per group) and the Needs Verification count — [repository.ts:364-431](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L364).

### Inferences
- The live-RSS and external-search paths mean the frontend can show articles that never passed through the FastAPI/BERT pipeline. The report should state which origin each screenshot comes from. The analytics page already prints "Source: ingestion database …" vs "live publisher feeds" ([analytics/page.tsx:49-51](file:///home/user/Ai_fake_news/frontend/src/app/analytics/page.tsx#L49)).

### Gaps
- None material.

---

## Q5. Earlier report (`docs/report/content.html`) vs code: overstatements

### Takeaway
The earlier 30-page report is largely accurate and already concedes the main gaps: extractive summaries, uncalibrated scores, no P/R/F1, models not run. A few statements still overstate or misdescribe the code:
- "every article receives a credibility-risk indicator".
- The scope names only the four backend publishers.
- The conclusion says results are available "through a REST API, a responsive dashboard" without noting that the dashboard does not use the API.
- The feasibility section implies the system was fully built and tested on a laptop, although the models were never run.
- Separately, a UI bug labels all DB rows "model" in analytics.

### Cited Findings
- Conclusion: "every article receives a credibility-risk indicator, a sentiment label and eight explained content scores" — [content.html §9](file:///home/user/Ai_fake_news/docs/report/content.html).
  - **Overstated.** `risk_score` is None and the label "Unavailable" when <65% of the risk weight is scoreable ([analysis_pipeline.py:110-112,123](file:///home/user/Ai_fake_news/backend/services/analysis_pipeline.py#L110); [dimension_service.py:157-158](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L157)).
  - Several of the eight dimensions are None for headline-only items (readability, headline accuracy, content quality, and source credibility for unknown publishers).
  - Suggested fix: "every article receives the analysis that its available text supports; a risk score is given only when enough dimensions can be measured, otherwise the article is marked 'not assessed' and Needs Verification."
- Conclusion: "results are available through a REST API, a responsive dashboard …" — accurate as a list. Elsewhere, though, the report should not imply the dashboard uses the REST API. §3.4 itself correctly says "The Next.js server reads the article directly from Supabase" — [content.html §3.4](file:///home/user/Ai_fake_news/docs/report/content.html).
- §1.2 Scope: "selected public RSS feeds (BBC, CNN, Al Jazeera and Yahoo)" — **incomplete**. It omits the live-feed fallback publishers and the Google News/GNews/GDELT external search ([sections.ts:25-74](file:///home/user/Ai_fake_news/frontend/src/lib/sections.ts#L25); [externalSearch.ts:1-16](file:///home/user/Ai_fake_news/frontend/src/lib/externalSearch.ts#L1)). Also "Out of scope: … training new ML models" and "user accounts with passwords" are correct.
- §2.1 Technical feasibility: "The project was built and tested on a standard laptop-class environment" vs Table 5.2 "Real model inference … Not executed: model download blocked in the test environment" — **internally inconsistent / mild overstatement**. Say that the software was tested and the models were tested with stand-in pipelines.
- §2.1 Schedule feasibility lists "summary, risk interpretation" stages as if done. They were delivered as the extractive summary and the uncertainty-band interpretation, not as the synopsis' AI summarization and calibration. Acceptable if worded that way.
- Table 1.2 says Supabase "Stores articles, analysis results … reader names" (**M**), and Tailwind gives a "Responsive newspaper-style layout" (**M**; mostly custom CSS on Tailwind v4).
- Table 3.2: "Sentiment … 50 = neutral; never unscored" → **M** ([dimension_service.py:172-176](file:///home/user/Ai_fake_news/backend/services/dimension_service.py#L172)). "Bias/Objectivity/Propaganda never unscored" → **M**.
- Table 5.2 test counts: "62 passed, 3 skipped", "32 passed (5 files)". The frontend count matches the test files (2+9+1+16+4 = 32 `it/test` calls). The backend has 56 `def test_` functions; 62 is plausible with parametrisation. I did not re-run the suites.
- Code-level overstatement in the UI: `normaliseRow` sets `analysisMethod: 'model'` for **every** database row, even rows stored with `analysis_method = 'rules'` while the models were unavailable ([repository.ts:129](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L129)). The analytics page therefore prints the "model" method note, which says "when the models are available, Sentiment comes from DistilBERT…" ([dimensions.ts:32-33](file:///home/user/Ai_fake_news/frontend/src/lib/dimensions.ts#L32)). The hedge "when available" limits the damage, but the per-row `analysis_method` column is ignored.
- Frontend label logic: `summaryKind === 'ai'` is reachable only if `summary_method === 'abstractive'`, which the backend never writes ([repository.ts:109](file:///home/user/Ai_fake_news/frontend/src/lib/repository.ts#L109)). This is dead code, not an overstatement.
- Things content.html gets right and the final report should keep:
  - Extractive summaries.
  - "raw, uncalibrated indicator".
  - The five Needs-Verification rules.
  - Risk weights and thresholds.
  - Grouping thresholds (0.32 / 48 h / 36 h).
  - "No accuracy, precision or recall figures are reported".
  - Limitations: short text, label mapping, word-list errors such as "won't" → "won", grouping false positives, in-memory rate limit.
  - Future scope: calibration with temperature scaling, P/R/F1, abstractive summaries.

### Inferences
- content.html is a sound base for the final report. The main changes needed are the "every article" wording, the scope sentence on sources, and an explicit "planned in synopsis vs delivered" table.

### Gaps
- I compared tag-stripped text of content.html. Placeholder blocks (`{{ANALYZE_EXAMPLE}}`, `{{CODE:…}}`) are filled in by `docs/report/build.py`, which I did not check.

---

## Appendix A: Recommended wording for the final report (resolved in favour of the code, gap kept visible)

| Synopsis item | Final-report wording |
|---|---|
| AI-generated summaries | "Extractive summaries (sentence selection by word frequency, shown only when the excerpt has ≥3 sentences). Abstractive AI summarisation was planned but not implemented." |
| BERT credibility-risk classification | "BERT-tiny (`mrm8488/bert-tiny-finetuned-fake-news-detection`) fake-class score, loaded lazily and optional. It is averaged with a transparent rule-based risk; if the model is unavailable, the rule-based risk is used alone and the article is marked 'partial'." |
| Calibrated confidence / calibration evaluation | "Scores are raw softmax outputs and are labelled uncalibrated. Uncertainty is handled by a 0.40–0.60 band, a <0.60 confidence threshold and a model–rule disagreement check. Calibration (e.g. temperature scaling with ECE) is future work." |
| Accuracy / precision / recall / F1 | "Not measured: no labelled dataset was evaluated and the models could not be run in the test environment. A sanity script prints raw outputs on six examples." |
| Sentiment Positive/Negative/Neutral | "DistilBERT SST-2 (binary) positive score mapped to 0–100. Scores 41–59 are read as Neutral. A word-list fallback is used when the model is unavailable." |
| Needs Verification when confidence insufficient | "Raised when there is no risk score, the score is 0.40–0.60, the excerpt has <150 characters, classifier confidence is <0.60, or classifier and rules differ by ≥0.50." |
| Duplicate or highly similar entries | "Exact duplicates are removed by normalised title and URL, within the batch and against the database. Highly similar reports from different publishers are grouped, not removed." |
| Cross-source comparison using summaries | "Grouping uses TF-IDF cosine similarity of headline and lead sentence (≥0.32, within 36 h of the seed, ≥2 publishers). Summaries are not used, and agreement is not treated as verification." |
| Source credibility "and source history" | "Per-article score from a hand-curated table of 14 newsrooms. Unknown publishers are left unscored, and no source history is kept." |
| Frontend retrieves data through FastAPI | "The Next.js server reads Supabase directly with the read-only public key. FastAPI provides the REST API, the scheduler and the server-side PDF; the browser can also generate the PDF itself." |
| Report entity (reportId, filePath) | "PDF reports are generated on demand and streamed; they are not stored." |
| Summary.generatedAt, Source.credibilityIndicator, CredibilityResult.confidenceLevel | "Stored as columns of one `articles` table: `ai_summary` + `summary_method`, `dimensions.source_credibility`, and `confidence_level` (uncalibrated; null without the model)." |
| Evaluation results deliverable | "Software test results: backend 62 passed / 3 opt-in skipped; frontend 32 passed. Model evaluation results are not available." |
| Real-time | "Near-real-time: scheduled every 30 minutes (configurable)." |
