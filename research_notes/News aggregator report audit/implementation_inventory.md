# Implementation Inventory: AI-Powered News Aggregator with Advanced Credibility and Content Analysis

Audit date: 25 Nov 2026. Repository: `/home/user/Ai_fake_news`, branch `claude/elegant-maxwell-qvf1gr` (HEAD `f96fa47`, working tree clean apart from the untracked `research_notes/` folder). Every finding below was checked in the source code. "Sources" are repository-relative `file:line` references, not web URLs. Nothing in the repository was modified.

Status key: **FULL** = fully implemented (and unit-tested where stated), **PARTIAL** = implemented but limited or not verifiable here, **PLANNED** = named in the synopsis or schema but not implemented.

---

## 1. Architecture and data flow (article path end to end)

### Takeaway
There are **two separate data paths**, and the report has to describe both correctly. (a) The **backend ingestion path**: APScheduler → `rss_fetcher.py` → `analysis_pipeline.py` (`dimension_service` + `ai_service` + extractive summary) → `db_service.py` → Supabase `articles` → `clustering_service.py` (group_id written back). (b) The **frontend read path**: Next.js server components and Next.js API routes read Supabase **directly** with the anon key, through `frontend/src/lib/repository.ts`. They do **not** go through the FastAPI REST API. The only call from the frontend to FastAPI is the optional server PDF link (`/api/v1/report/{id}`), and only when `NEXT_PUBLIC_API_URL` is set. When Supabase is not configured or the table is empty, the frontend falls back to fetching publisher RSS feeds itself and scoring them in TypeScript with the same rules.

### Cited Findings
- Scheduler job `fetch_and_store_job`: `fetch_articles()` → `store_articles_in_db(articles)` → `update_groups()`; the summary is kept in `last_run` for `/api/health` — [backend/services/scheduler.py:30-50](backend/services/scheduler.py)
- The scheduler starts in the FastAPI lifespan unless `ENABLE_SCHEDULER` is 0/false; it runs once at startup only if `INGEST_ON_STARTUP=1` — [backend/main.py:27-38](backend/main.py)
- `rss_fetcher.fetch_articles()` downloads every feed with httpx (timeout 15 s, follow_redirects, User-Agent "AI-News-Aggregator/2.0 (academic project; RSS reader)"), parses it with feedparser, records failed feeds in `failed_sources` and de-duplicates the batch — [backend/services/rss_fetcher.py:49-51,128-151](backend/services/rss_fetcher.py)
- Backend feed list (11 feeds in 5 categories): sports (BBC Sport, Yahoo Sports), politics (CNN Politics, BBC Politics), business (Yahoo Finance, BBC Business), technology (CNN Tech, BBC Technology), general (BBC, CNN, AlJazeera). CNN feeds use http:// — [backend/services/rss_fetcher.py:25-47](backend/services/rss_fetcher.py)
- At most 8 entries per feed (`ENTRIES_PER_SOURCE = 8`). An entry without a title or link is skipped. HTML is removed with BeautifulSoup and whitespace collapsed. `content_summary` is set to "" when the excerpt equals the title (there is no title fallback). `published_at` is ISO-8601 UTC from `published_parsed`/`updated_parsed`, or None — [backend/services/rss_fetcher.py:54-106](backend/services/rss_fetcher.py)
- In-batch de-duplication by normalised URL (lower-case host; query string, fragment and trailing slash dropped) and normalised title (`[^a-z0-9]+` → space) — [backend/services/rss_fetcher.py:62-72,115-125](backend/services/rss_fetcher.py)
- `db_service.store_articles_in_db`: loads stored titles/URLs in chunks of 50 (raw and normalised URL), skips duplicates **before** analysis, calls `analyze_article(title, content_summary, source_domain)`, upserts with `on_conflict="title", ignore_duplicates=True`, and falls back to pre-v2 columns if migration 02 has not been applied. Returns counts received/duplicates/inserted/failed/needs_verification/unavailable — [backend/services/db_service.py:67-139](backend/services/db_service.py)
- An empty `published_at` is removed from the record so that the column default `now()` applies — [backend/services/db_service.py:83-91](backend/services/db_service.py)
- `update_groups`: selects up to 1000 rows with `published_at >= now-48h`, computes `assignments()` and updates only rows whose group_id/event_title changed — [backend/services/db_service.py:142-160](backend/services/db_service.py)
- Frontend data entry point: `getEdition()` uses Supabase (`select * order published_at desc limit 500`, 60 s in-process cache) when it is configured and non-empty, otherwise `getLiveEdition()` — [frontend/src/lib/repository.ts:22-31,133-151,169-211](frontend/src/lib/repository.ts)
- The frontend Supabase client uses `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`, with a placeholder client when they are missing — [frontend/src/lib/supabase.ts:1-18](frontend/src/lib/supabase.ts)
- DB groups are taken from the stored `group_id`, keeping only groups with ≥2 publishers. If none exist, the TypeScript `clusterArticles` is run in the frontend — [frontend/src/lib/repository.ts:157-196](frontend/src/lib/repository.ts)
- Row normalisation: label = stored label if valid, else `riskLabelFor(risk_score)` if a score exists, else 'Unavailable'. needsVerification = stored flag OR label Unavailable. Legacy rows get status 'legacy'. **Every DB row is tagged `analysisMethod: 'model'` even when it was analysed by rules only** (cosmetic inconsistency: the "model" method note is shown even for status `partial`/method `rules`) — [frontend/src/lib/repository.ts:84-131](frontend/src/lib/repository.ts)
- Full-table DB search: `ilike *word*` OR over title/content_summary/ai_summary/source_domain, limit 400, then in-memory ranking. It retries without ai_summary if that column is missing — [frontend/src/lib/repository.ts:262-286](frontend/src/lib/repository.ts)
- When a query has fewer local matches than the page size, `searchExternal` results are appended to the local results — [frontend/src/lib/repository.ts:288-328](frontend/src/lib/repository.ts)
- Live-RSS fallback (`liveNewsService.ts`): 8 sections, 33 feed URLs (Google News topic feeds, BBC, Guardian, Al Jazeera, The Hindu, NDTV, Indian Express, Mint, TechCrunch, BBC Sport); 20 items per feed, 8 s fetch timeout, 2 min cache, Next `revalidate: 120`; regex XML parsing; ids `lv-<hash of canonical link>`; dedup by id and publisher+title; each item scored with `analyseText` + `extractiveSummary`; `analysisMethod: 'heuristic'` — [frontend/src/lib/liveNewsService.ts:14-16,111-220](frontend/src/lib/liveNewsService.ts); [frontend/src/lib/sections.ts:20-108](frontend/src/lib/sections.ts)
- External search (`externalSearch.ts`, server-side only): if `GNEWS_API_KEY` is set → GNews (`/api/v4/search`, lang en, max 10, 15 s timeout, 429/403 → "rate-limited"); otherwise Google News RSS search (`news.google.com/rss/search`, `when:1d/7d/30d` for the since filter, 10 s timeout, first 30 items). An empty answer or an error falls back to GDELT DOC 2.0 (`mode=artlist`, maxrecords 250, `timespan=3months`, `sourcelang:english`, 30 s timeout, serialised with a 5.5 s minimum gap). GDELT results are kept only if the headline matches every term. Results are de-duplicated against local URLs/titles, max 12 results, 30 min cache. Results with ≥150 chars of description are analysed with `toArticle` (ids `ex-…`, kept 24 h in `globalThis.__analysedArticles`) — [frontend/src/lib/externalSearch.ts:1-352](frontend/src/lib/externalSearch.ts)
- Name-only reader registration: `ClientLayout` shows `NameAuthModal` when localStorage `ai_news_user` is empty. The modal POSTs `{name}` to `/api/auth/profile` (input `maxLength=60`). The route selects `named_visitors` by name and inserts the name if it is new. If Supabase is not configured or on DB error, it returns success with id "local-demo-user"/"fallback-visitor-id" — [frontend/src/components/ClientLayout.tsx:10-43](frontend/src/components/ClientLayout.tsx); [frontend/src/components/ui/NameAuthModal.tsx:15-50,76](frontend/src/components/ui/NameAuthModal.tsx); [frontend/src/app/api/auth/profile/route.ts:11-83](frontend/src/app/api/auth/profile/route.ts)
- The server PDF link is shown only if `backendUrl && article.origin === 'database'`; otherwise only the in-browser jsPDF export is offered — [frontend/src/components/analysis/ReportDownload.tsx:11-43](frontend/src/components/analysis/ReportDownload.tsx); [frontend/src/app/article/[id]/page.tsx:137](frontend/src/app/article/[id]/page.tsx)

### Inferences
- An architecture diagram in the report should draw Next.js → Supabase (read-only anon key) directly and Next.js → FastAPI only for the PDF. A "FastAPI router → Next.js" arrow for article data would be inaccurate. The FastAPI GET endpoints exist and are tested, but the frontend does not use them. Note: `docs/report/diagrams/architecture.svg` already labels the presentation layer "(read-only Supabase key)".
- There are two feed lists: backend 11 feeds, frontend 33. They overlap only partly; for example, Guardian/Hindu/NDTV/Mint/TechCrunch appear only in the frontend fallback.

### Gaps
- It could not be verified in this environment that live feeds, Supabase or Google News/GDELT respond (no network or credentials; the live tests are opt-in and skipped).

---

## 2. Exact models, label mapping, thresholds and formulas

### Takeaway
All numeric rules are deterministic and exist in identical copies in Python (`dimension_service.py`) and TypeScript (`scoring.ts`, `clustering.ts`); parity is checked against `shared/scoring_vectors.json`. Two transformer models are wired in but are lazily loaded and **were not run here** (transformers/torch are not installed). The one real algorithmic difference between the two sides is the summary: the backend uses frequency-based extractive selection, the frontend takes the first two sentences.

### Cited Findings
**Models (ai_service.py)**
- Fake-news model `mrm8488/bert-tiny-finetuned-fake-news-detection` (env `FAKE_NEWS_MODEL`); sentiment model `distilbert-base-uncased-finetuned-sst-2-english` (env `SENTIMENT_MODEL`) — [backend/services/ai_service.py:34-35](backend/services/ai_service.py)
- Label mapping: `FAKE_NEWS_FAKE_LABEL` default `LABEL_1`, `FAKE_NEWS_REAL_LABEL` default `LABEL_0`. The docstring states that the model config has no id2label and that LABEL_1=fake is an assumption carried over from the original code and third-party usage — [backend/services/ai_service.py:8-14,36-37](backend/services/ai_service.py)
- `ENABLE_MODELS` (default 1). `MAX_TOKENS = 512` (pipeline is called with `truncation=True, max_length=512`). `MAX_INPUT_CHARS = 20_000` — [backend/services/ai_service.py:38-40,97-98](backend/services/ai_service.py)
- Lazy, thread-locked loading of `pipeline("text-classification", model=…, top_k=None)`. On failure the error is cached and the outputs are `None` with status "unavailable" (no placeholder 0.5) — [backend/services/ai_service.py:47-69,106-139](backend/services/ai_service.py)
- Fake score = softmax of the fake label (or 1 − real); clamped to 0–1; `confidence = max(p, 1−p)`; `predicted_label = fake if p ≥ 0.5`. Unexpected labels produce an error — [backend/services/ai_service.py:124-139](backend/services/ai_service.py)
- Sentiment = POSITIVE softmax (or 1 − NEGATIVE) — [backend/services/ai_service.py:142-165](backend/services/ai_service.py)
- Model input text = title + ". " + body, whitespace collapsed, truncated to 20,000 characters — [backend/services/ai_service.py:101-103](backend/services/ai_service.py)
- `scripts/validate_models.py` contains 4 fake/real and 2 sentiment examples for checking the label mapping by eye; its docstring says explicitly that this is not a benchmark — [backend/scripts/validate_models.py:1-58](backend/scripts/validate_models.py)

**Eight dimensions (dimension_service.py = scoring.ts)**
- Keys: sentiment, bias, objectivity, readability, propaganda, headline_accuracy, source_credibility, content_quality — [backend/services/dimension_service.py:29-32](backend/services/dimension_service.py)
- `body = excerpt if excerpt != title else ""`; `combined = title + ". " + body`; `evidence_chars = len(body)` — [backend/services/dimension_service.py:167-169](backend/services/dimension_service.py)
- Sentiment = `clamp(50 + (pos−neg)*9, 5, 95)` from word lists (23 positive, 36 negative terms). Label: ≥60 positive, ≤40 negative, otherwise neutral (**neutral band 41–59**) — [backend/services/dimension_service.py:42-43,140-141,172-175](backend/services/dimension_service.py)
- Objectivity = `clamp(92 − 14·subjective_hits, 20)` (17 subjective terms) — [backend/services/dimension_service.py:44,183-184](backend/services/dimension_service.py)
- Bias = `clamp(90 − 15·loaded_hits − (6 if body and no attribution else 0), 20)` (12 loaded terms, 10 attribution terms) — [backend/services/dimension_service.py:45-46,191-193](backend/services/dimension_service.py)
- Readability = Flesch Reading Ease `206.835 − 1.015·(words/sentences) − 84.6·(syllables/words)` with a heuristic syllable counter, clamped 0–100. **None if there is no body** — [backend/services/dimension_service.py:100-116,202-203](backend/services/dimension_service.py)
- Propaganda = `clamp(95 − 22·manipulation_patterns − 10·shouting_words, 5)`. 11 regex patterns (shocking, you won't believe, secret, urgent, exposed, outrage, `!{2,}`, must see, goes viral, destroys, slams); shouting = `\b[A-Z]{5,}\b` in the title — [backend/services/dimension_service.py:47-52,212-214](backend/services/dimension_service.py)
- Headline accuracy = `clamp(45 + 50·matched/head_terms)`; head terms are words longer than 3 characters that are not stopwords, matched in the body (also with a trailing "s" removed). None if there is no body or no head terms — [backend/services/dimension_service.py:222-226](backend/services/dimension_service.py)
- Source credibility = publisher reputation table (substring match, first hit): reuters 95, associated press 95, bbc 93, guardian 90, the hindu 90, financial times 93, bloomberg 92, indian express 88, al jazeera 86, ndtv 84, mint 86, techcrunch 84, cnn 86, yahoo 78. **None for unknown publishers** — [backend/services/dimension_service.py:36-40,119-124](backend/services/dimension_service.py)
  - Caution (inference from the code): "AlJazeera" (the backend `source_domain` without a space, rss_fetcher.py:45) does **not** contain "al jazeera", so backend-ingested Al Jazeera rows get source_credibility = None. The current screenshots are consistent with this: dimension average Source Credibility 93 = BBC only.
- Content quality = `clamp(35 + min(chars,600)/12 + min(sentences,4)·5)`; None if there is no body — [backend/services/dimension_service.py:242-243](backend/services/dimension_service.py)
- Every dimension carries a text explanation — [backend/services/dimension_service.py:251-270](backend/services/dimension_service.py)

**Rule risk, labels, verification**
- RISK_WEIGHTS: source_credibility 0.35, propaganda 0.20, objectivity 0.15, bias 0.15, headline_accuracy 0.15. `MIN_RISK_WEIGHT = 0.65`. rule_risk = `round2(1 − Σ(v·w)/Σw/100)` over the scoreable dimensions; None if Σw < 0.65 — [backend/services/dimension_service.py:59-67,144-160](backend/services/dimension_service.py)
- Labels: ≤0.35 Low Risk; ≤0.65 Moderate Risk; otherwise High Risk — [backend/services/dimension_service.py:132-137](backend/services/dimension_service.py)
- `MIN_EVIDENCE_CHARS = 150`; `UNCERTAINTY_BAND = (0.4, 0.6)` — [backend/services/dimension_service.py:59,68](backend/services/dimension_service.py)
- Pipeline combination: risk_score = mean(rule_risk, p_fake) if the model ran; rule_risk alone if it did not; None if rule_risk is None. `PIPELINE_VERSION = "2.0"` — [backend/services/analysis_pipeline.py:43,105-123](backend/services/analysis_pipeline.py)
- needs_verification if ANY of: no score; score within 0.40–0.60; evidence <150 chars; classifier confidence <0.60 (`LOW_MODEL_CONFIDENCE`); |p_fake − rule_risk| ≥ 0.50 (`DISAGREEMENT`) — [backend/services/analysis_pipeline.py:44-45,124-137](backend/services/analysis_pipeline.py). (The browser `analyseText` uses only the first three conditions — [frontend/src/lib/scoring.ts:258-262](frontend/src/lib/scoring.ts).)
- When the sentiment model ran, the sentiment dimension = `clamp(pos·100, 5, 95)` (replaces the lexical score) — [backend/services/analysis_pipeline.py:77-87](backend/services/analysis_pipeline.py)
- analysis_status: "unavailable" (no score) / "complete" (both models ok) / "partial"; analysis_method "model+rules" or "rules"; model_version `"pipeline 2.0; <models or 'rules only'>"`; is_fake = p_fake ≥ 0.5; legacy `credibility_score = 1 − p_fake` — [backend/services/analysis_pipeline.py:139-173](backend/services/analysis_pipeline.py)
- `confidence` in the browser analysis is always `null` — [frontend/src/lib/scoring.ts:279](frontend/src/lib/scoring.ts)

**Summary**
- Backend extractive summary: sentences longer than 30 characters; None if fewer than 3; each sentence scored by the mean normalised document frequency of its content words (+0.15 bonus for the first sentence); the top 2 are returned in original order — [backend/services/analysis_pipeline.py:52-74](backend/services/analysis_pipeline.py)
- Frontend extractive summary: same ≥3 sentences of more than 30 characters, but simply **the first two sentences** — [frontend/src/lib/scoring.ts:98-103](frontend/src/lib/scoring.ts)
- No abstractive or LLM summary exists anywhere; the frontend would label `summary_method='abstractive'` as 'ai', but nothing writes that value — [frontend/src/lib/repository.ts:109](frontend/src/lib/repository.ts)

**Clustering (clustering_service.py = clustering.ts)**
- Text = title ×2 + lead sentence (≤240 chars up to the first . ! ?) — [backend/services/clustering_service.py:47-49,97](backend/services/clustering_service.py)
- Tokens: NFKD accent folding, possessive 's removed, `[^a-z0-9\s-]` → space, length >2, stopwords and pure numbers dropped — [backend/services/clustering_service.py:34-44](backend/services/clustering_service.py)
- TF-IDF `w = tf · ln((1+n)/(1+df) + 1)`, L2-normalised, cosine similarity — [backend/services/clustering_service.py:52-72](backend/services/clustering_service.py)
- `SIMILARITY_THRESHOLD = 0.32`, `WINDOW_HOURS = 48`, `MAX_GAP_HOURS = 36`, `MIN_PUBLISHERS = 2`. Seed-based grouping (a candidate is compared with the seed only); one article per publisher; group id `ev-<smallest id>` — [backend/services/clustering_service.py:28-31,85-129](backend/services/clustering_service.py); TS: [frontend/src/lib/clustering.ts:24-38](frontend/src/lib/clustering.ts)

**Scheduler, rate limit, CORS, validation**
- Interval `INGEST_INTERVAL_MINUTES` default 30. A non-blocking `threading.Lock` skips overlapping runs. APScheduler `max_instances=1, coalesce=True, replace_existing=True` — [backend/services/scheduler.py:25-68](backend/services/scheduler.py)
- Rate limit: in-memory sliding 60 s window per (client IP, "analyze"/"report"); `RATE_LIMIT_PER_MINUTE` default 30; applies to paths containing `/analyze` or `/report/`; returns 429 with `Retry-After: 60` — [backend/main.py:21-24,52-64](backend/main.py)
- CORS: `ALLOWED_ORIGINS` default `http://localhost:3000,http://127.0.0.1:3000`; credentials false; methods GET, POST; header Content-Type — [backend/main.py:18-19,43-49](backend/main.py)
- Generic 500 handler ("Internal server error.") and DB errors mapped to 503 "The database is temporarily unavailable." (details are not leaked) — [backend/main.py:67-70](backend/main.py); [backend/api/router.py:24-26](backend/api/router.py)

**PDF reports**
- Backend ReportLab A4 report ("The Daily Signal", "Article Intelligence Report"). Fields: generated timestamp (UTC) plus "MIT-WPU M.Sc Computer Science, Group 17"; category · publisher; title; published; source link; publisher excerpt box; extractive summary box; credibility table (Risk label, Risk score 0–1, Classifier fake score, Classifier confidence %, Verification); ai_reasoning; 8-dimension table (score + scale + explanation, "n/a" when missing); method note; status/method/model version/analysed time; disclaimer; footer with page number. Missing values print "Not recorded"/"Not computed"/"Not available"/"Not reported" — [backend/services/report_service.py:26-186](backend/services/report_service.py)
- Frontend jsPDF A4 report: same sections, plus a score bar per dimension, "Page p of n", a method note for heuristic vs model, and Windows-1252 sanitising (₹ → "Rs"). File name `daily-signal-report-<slug>.pdf` — [frontend/src/lib/pdfReportGenerator.ts:25-220](frontend/src/lib/pdfReportGenerator.ts)

### Inferences
- The analyze_example.json case (sensational headline from an unknown blog) receives only **Moderate Risk 0.57**: source_credibility is None, so propaganda = 5 is diluted by the other dimensions. This is a known limitation of the rule weights and should be discussed honestly.
- Short BBC/Al Jazeera excerpts systematically produce Low Risk with needs_verification (all 41 in the 25 Nov screenshots). That follows from the rule design, not a bug, but the report should state it.

### Gaps
- Whether LABEL_1 really means "fake" for the BERT-tiny model has not been confirmed (validate_models.py was not run here).

---

## 3. Database (tables, columns, constraints, indexes, RLS, readers and writers)

### Takeaway
Three tables: `articles` (main), `named_visitors` (name-only reader register) and `user_profiles` (FK to Supabase `auth.users`). **`user_profiles` is defined but never used by any code (PLANNED).** There is no FK between `articles` and the other tables. Grouping uses the non-FK text column `articles.group_id`.

### Cited Findings
- `articles` columns (supabase_complete_setup.sql): id uuid PK default gen_random_uuid(); title text NOT NULL UNIQUE; source_domain text; source_url text; content_summary text; category text default 'general'; sentiment text; is_fake boolean; credibility_score real; ai_reasoning text; published_at timestamptz default now(); created_at timestamptz default now(); risk_score real; confidence_level real; credibility_label text (no default); needs_verification boolean default false; ai_summary text; dimensions jsonb default '{}'; group_id text default NULL; event_title text default NULL; analysis_status text; analysis_method text; model_version text; analyzed_at timestamptz; summary_method text; model_fake_probability real — [backend/db/supabase_complete_setup.sql:14-63](backend/db/supabase_complete_setup.sql)
- `named_visitors`: id uuid PK; name text UNIQUE NOT NULL; created_at timestamptz default now() — [backend/db/supabase_complete_setup.sql:68-72](backend/db/supabase_complete_setup.sql)
- `user_profiles`: id uuid PK REFERENCES auth.users(id) ON DELETE CASCADE; name text; saved_topics text[]; created_at — [backend/db/supabase_complete_setup.sql:77-82](backend/db/supabase_complete_setup.sql)
- RLS enabled on all three tables. articles: SELECT for public only (insert/update policies dropped). named_visitors: public SELECT + INSERT (no update or delete). user_profiles: insert/select/update where `auth.uid() = id` — [backend/db/supabase_complete_setup.sql:87-113](backend/db/supabase_complete_setup.sql)
- Indexes: published_at DESC, category, credibility_score DESC, group_id, credibility_label, needs_verification, source_url, analysis_status — [backend/db/supabase_complete_setup.sql:118-125](backend/db/supabase_complete_setup.sql)
- CHECK constraints (NOT VALID): credibility_label IN (Low/Moderate/High Risk) or NULL; 0 ≤ risk_score ≤ 1; analysis_status IN (complete, partial, unavailable, pending, legacy); named_visitors `char_length(btrim(name)) BETWEEN 1 AND 40` — [backend/db/supabase_complete_setup.sql:130-148](backend/db/supabase_complete_setup.sql)
- Migration 01 adds risk_score, confidence_level, credibility_label (no default), needs_verification, ai_summary, dimensions, group_id, event_title and 3 indexes — [backend/db/01_upgrade_to_msc_synopsis.sql:5-48](backend/db/01_upgrade_to_msc_synopsis.sql)
- Migration 02 drops the 'Low Risk' default, adds the 6 provenance columns, sets the label to NULL on rows without risk_score, marks rows with NULL status as 'legacy', adds constraints and 2 indexes, and makes articles public read-only — [backend/db/02_integrity_and_security.sql:8-70](backend/db/02_integrity_and_security.sql)
- schema.sql = original v1 (12 article columns, same 3 tables, 3 indexes) — [backend/db/schema.sql:12-86](backend/db/schema.sql)
- Backend writes articles with the service-role key (`SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_SECRET_KEY` or `SUPABASE_KEY`) — [backend/db/supabase.py:19-44](backend/db/supabase.py)
- Readers and writers: backend db_service inserts/updates `articles` (store_articles_in_db, update_groups, reanalyze) and reads it (get_article_by_id, get_grouped_articles); router reads `articles` (/articles, /analytics); frontend repository.ts reads `articles` (anon key); /api/auth/profile reads and inserts `named_visitors`; `user_profiles` has no reader or writer (grep found no reference in the code) — [backend/services/db_service.py:32-176](backend/services/db_service.py); [backend/api/router.py:89,134](backend/api/router.py); [frontend/src/lib/repository.ts:139,273,342](frontend/src/lib/repository.ts); [frontend/src/app/api/auth/profile/route.ts:36,60](frontend/src/app/api/auth/profile/route.ts)
- `dimensions` jsonb structure = 8 numeric-or-null keys + an `explanations` object — [backend/services/dimension_service.py:251-270](backend/services/dimension_service.py)

### Inferences
- ER diagram: articles (standalone, PK id, UK title); named_visitors (standalone, UK name); user_profiles 1:1 → auth.users. The "event group" is a logical grouping through `group_id`, not a table.
- The name-length rule is not enforced consistently: the modal allows 60 characters and the route checks only for non-empty names. A 41–60 character name violates the DB CHECK on insert, and the route then silently returns success with "fallback-visitor-id" (route.ts:63-74). The earlier report says "1–40 characters", which is true only of the DB constraint.

### Gaps
- Whether migration 02 was actually applied on the live Supabase project cannot be checked here (no credentials). The 23 Nov Supabase screenshots show the **pre-migration** state (see section 8).

---

## 4. REST endpoints (FastAPI and Next.js)

### Takeaway
FastAPI exposes 8 routes, each mounted twice (`/api/v1/...` and `/api/...`), plus `/`. Next.js has 6 API routes of its own, some with the same paths (`/api/articles`, `/api/article/{id}`, `/api/groups`, `/api/analytics`), but they are different servers with different response shapes.

### Cited Findings
- Routers mounted at `/api/v1` and `/api`; FastAPI title "AI News Aggregator API", version "2.0.0"; `GET /` returns status/message/docs — [backend/main.py:41,73-80](backend/main.py)
- `GET /health` → {status "healthy", database_configured, models (model_status), last_ingestion} — [backend/api/router.py:53-61](backend/api/router.py)
- `POST /analyze` body: text (1–20000 chars, required), title (≤500), publisher (≤120). Without a title, the first sentence (or first 120 chars) is used as the title. Nothing is stored. The response model has 16 fields (sentiment, is_fake, credibility_score, risk_score, credibility_label, needs_verification, confidence_level, model_fake_probability, dimensions, ai_reasoning, ai_summary, analysis_status, analysis_method, model_version, model_errors). Validation error → 422; rate-limited — [backend/api/router.py:29-75](backend/api/router.py)
- `GET /articles?limit (1–200, default 50)&offset (0–10000)&category (≤40)&risk (Low Risk|Moderate Risk|High Risk|Unavailable)&q (≤120; only alphanumerics, space, `-` and `'` kept, then ilike on title/content_summary)&needs_verification` ordered by published_at desc; 503 on DB error — [backend/api/router.py:78-105](backend/api/router.py)
- `GET /article/{article_id: UUID}` → row; 404 "Article not found"; 422 for a non-UUID; 503 on DB error — [backend/api/router.py:108-117](backend/api/router.py)
- `GET /groups` → groups with publisher_count ≥ 2 (+ coverage per publisher) from the 300 most recent grouped rows — [backend/api/router.py:120-127](backend/api/router.py); [backend/services/db_service.py:39-64](backend/services/db_service.py)
- `GET /analytics?limit (1–2000, default 500)` → total, categories, sentiment, risk (incl. Unavailable), needs_verification, analysis_status, dimension_averages (mean of numeric values only, 1 decimal), dimension_counts, publishers, groups — [backend/api/router.py:130-158](backend/api/router.py)
- `GET /report/{article_id: UUID}` → application/pdf attachment `article-report-<id>.pdf`; 404; rate-limited — [backend/api/router.py:161-175](backend/api/router.py)
- `POST /ingest`: returns 404 unless `INGEST_TOKEN` is set; header `X-Ingest-Token` compared with `hmac.compare_digest`, 403 if wrong; runs `fetch_and_store_job()` — [backend/api/router.py:178-187](backend/api/router.py)
- Next.js `GET /api/articles` (q, section|category, publisher, risk, verify=1, sort newest|oldest|relevance, since 24h|7d|30d, page, limit clamped 1–100; q truncated to 120) → ArticlePage + info; 503 on error — [frontend/src/app/api/articles/route.ts:1-18](frontend/src/app/api/articles/route.ts); [frontend/src/lib/query.ts:15-33](frontend/src/lib/query.ts); [frontend/src/lib/repository.ts:290](frontend/src/lib/repository.ts)
- Next.js `GET /api/article/[id]` → {article}; 404 "Article not found in the current edition." — [frontend/src/app/api/article/[id]/route.ts:1-15](frontend/src/app/api/article/[id]/route.ts)
- Next.js `GET /api/groups`, `GET /api/analytics` (503 on error) — [frontend/src/app/api/groups/route.ts](frontend/src/app/api/groups/route.ts); [frontend/src/app/api/analytics/route.ts](frontend/src/app/api/analytics/route.ts)
- Next.js `GET /api/search/external?q=&since=` (400 if q is empty; q ≤120; 502 if unavailable) — [frontend/src/app/api/search/external/route.ts:1-24](frontend/src/app/api/search/external/route.ts)
- Next.js `POST /api/auth/profile` {name} (400 if empty; 500 on exception) — [frontend/src/app/api/auth/profile/route.ts](frontend/src/app/api/auth/profile/route.ts)

### Inferences
- `/ingest` was added after 23 Nov: it is absent from the old Swagger screenshot (25_api_docs.png), which also shows version 1.0.0 and an analyze body of only `{text}`.

### Gaps
- None for the code. Live responses with real models were not observed.

---

## 5. Frontend pages and main components

### Takeaway
Next.js 16 App Router newspaper-style UI ("The Daily Signal"), with 7 page routes plus not-found, error and loading pages. All pages are server-rendered from `repository.ts` (`dynamic = 'force-dynamic'`).

### Cited Findings
- `/` front page: Latest Articles rail, Breaking News lead + "Also reporting this story" (group), Daily Feed, "edition at a glance" risk counts (Low/Moderate/High/Needs verification), Featured Stories, Most-Covered Events, section blocks; old query links are redirected (`?view=comparison` → /compare, `?q`/`?risk` → /search) — [frontend/src/app/page.tsx:16-169](frontend/src/app/page.tsx)
- `/article/[id]`: breadcrumb, headline, publisher/date, RiskMark, stored or RSS excerpt with a provenance note ("does not reproduce full articles"), Continue-reading link, extractive summary, Credibility panel (risk label, risk score, classifier fake score, classifier confidence, verification, reasoning, disclaimer), PDF download, "Also reported by" (group), Analysis supplement with an 8-dimension radar chart (vs. the edition average when more than 5 articles are scored the same way) and a dimension table, related stories — [frontend/src/app/article/[id]/page.tsx:26-193](frontend/src/app/article/[id]/page.tsx)
- `/search`: query + filters (section, publisher, risk, order, published since, needs-verification), 20 results per page, InfiniteFeed (`/api/articles`), ExternalResults (`/api/search/external`) started automatically when fewer than 5 full matches — [frontend/src/app/search/page.tsx:12-112](frontend/src/app/search/page.tsx)
- `/section/[slug]` for the 8 sections (world, india, politics, business, technology, science, culture, sports) — [frontend/src/app/section/[slug]/page.tsx](frontend/src/app/section/[slug]/page.tsx); [frontend/src/lib/sections.ts:20-108](frontend/src/lib/sections.ts)
- `/compare` "One story, many newsrooms": CrossSourceView of groups, with a method text that names threshold 0.32 and the 48 h window — [frontend/src/app/compare/page.tsx:10-58](frontend/src/app/compare/page.tsx)
- `/analytics` "The News Intelligence Report": 7 figures (sections, risk labels, tone, average dimension scores, publication timeline over the last 36 h, publishers, publishers per group) + note on method — [frontend/src/app/analytics/page.tsx:83-187](frontend/src/app/analytics/page.tsx); [frontend/src/lib/repository.ts:364-431](frontend/src/lib/repository.ts)
- Layout: Masthead, SectionNav, SiteFooter, ClientLayout (register modal); fonts Playfair Display / Source Serif 4 / Inter — [frontend/src/app/layout.tsx](frontend/src/app/layout.tsx)
- Search features: accent and case normalisation, word-prefix matching, aliases (facebook↔meta, google↔alphabet, un↔united nations, uk↔britain/british, us↔usa/america/american), a year treated as a date hint, ranking headline > publisher > summary/excerpt — [frontend/src/lib/search.ts:1-40](frontend/src/lib/search.ts)
- Components: DimensionRadarChart (Recharts), DimensionTable, ReportDownload, CrossSourceView, DashboardAnalytics (HorizontalBars, Timeline), NewsCard, InfiniteFeed, ExternalResults, SearchAndFilter, ViewSwitcher, NameAuthModal — [frontend/src/components/](frontend/src/components/)

### Inferences
- The "Coverage" and "Analysis" nav items correspond to /compare and /analytics.

### Gaps
- `npm run build` was not re-run in this audit (PROJECT_STATUS.md says it passed; not verified here).

---

## 6. Hardware/software stack (declared versions)

### Takeaway
Python FastAPI backend (Docker base python:3.10-slim, port 7860, layout suited to Hugging Face Spaces). Next.js 16.1.6 / React 19.2.3 frontend. Supabase (PostgreSQL) for the database. No hardware requirement is stated anywhere in the repository.

### Cited Findings
- requirements.txt minimums: fastapi>=0.110.0, uvicorn>=0.28.0, pydantic>=2.6.4, python-dotenv>=1.0.1, httpx>=0.27.0, supabase>=2.3.4, feedparser>=6.0.11, beautifulsoup4>=4.12.3, apscheduler>=3.11.3, transformers>=4.38.0, torch>=2.2.0, reportlab>=4.1.0, pytest>=8.2.2, pypdf>=4.0 — [backend/requirements.txt:1-25](backend/requirements.txt)
- Dockerfile: python:3.10-slim, non-root user uid 1000, `uvicorn main:app --host 0.0.0.0 --port 7860` — [backend/Dockerfile:1-27](backend/Dockerfile)
- package.json: next 16.1.6, react/react-dom 19.2.3, @supabase/supabase-js ^2.97.0, @supabase/ssr ^0.8.0, jspdf ^4.2.1, recharts ^3.7.0, lucide-react ^0.575.0, axios ^1.13.5 (**declared but unused**: grep finds no import); dev: typescript ^5, eslint ^9, eslint-config-next 16.1.6, tailwindcss ^4, vitest ^4.0.18, @testing-library/react ^16.3.2, jsdom ^28.1.0, babel-plugin-react-compiler 1.0.0 — [frontend/package.json](frontend/package.json)
- `reactCompiler: true` — [frontend/next.config.ts](frontend/next.config.ts)
- Versions in the audit environment: Python 3.13.18, Node v22.23.5, Next.js v16.1.6, fastapi 0.165.0, pydantic 2.13.5, supabase 2.34.1, feedparser 6.0.14, httpx 0.28.1, reportlab 5.0.1, APScheduler 3.11.3, pytest 9.1.1, pypdf 6.17.0; **transformers and torch are NOT installed** (ModuleNotFoundError) — observed via `pip list` and `python3 -c "import transformers"` in this session

### Inferences
- The Python version differs between environments: Docker uses 3.10, tests ran on 3.13.

### Gaps
- No documented hardware (CPU/RAM/GPU). The models are small (BERT-tiny, DistilBERT) and CPU inference is plausible, but there is no measured evidence.

---

## 7. Tests (real results, 25 Nov 2026 run)

### Takeaway
Backend: **62 passed, 3 skipped** (pytest, 2.30 s). Frontend: **5 files, 32 tests passed** (Vitest 4.0.18). `npm run lint` exit 0 (no warnings printed). `npx tsc --noEmit -p .` exit 0. All model and network calls in the unit tests are faked.

### Cited Findings
- Command output: `62 passed, 3 skipped in 2.30s`. Skipped: test_real_models_load_and_return_scores (needs RUN_MODEL_TESTS=1; downloads transformer weights), test_real_rss_feeds (RUN_LIVE_TESTS=1), test_supabase_connectivity (RUN_LIVE_TESTS=1, needs credentials) — [backend/tests/test_live_optional.py:6-33](backend/tests/test_live_optional.py); markers in [backend/pytest.ini](backend/pytest.ini)
- Test infrastructure: `FakePipeline` (fixed label scores), `fake_models` fixture (LABEL_0 0.8 / LABEL_1 0.2; NEGATIVE 0.9), `no_models` fixture, `ENABLE_SCHEDULER=0`; `fake_supabase.py` in-memory client — [backend/tests/conftest.py](backend/tests/conftest.py); [backend/tests/fake_supabase.py](backend/tests/fake_supabase.py)
- Backend per-file counts (from `pytest -v`): test_ai_service 9 (LABEL_1 read as fake, LABEL_0 read as real, truncation requested, empty input → unavailable, load failure, inference error, unexpected labels, sentiment separate, prepare_text); test_analysis_pipeline 7 (complete with models, rules-only, headline-only never Low Risk, low confidence flags, disagreement flags, risk = mean, summary needs 3 sentences); test_api 12 (health, analyze with/without models, validation, article by id, filters & validation, analytics with unavailable/missing scores, DB errors not leaked, report PDF, CORS, ingest disabled, rate limit); test_clustering_service 6 (cross-publisher grouping, same publisher not a group, time gap, window/clearing, insufficient articles, accent folding); test_db_service 6 (store & skip duplicates, missing published_at, idempotent re-run, analysis failure counted, update_groups, publisher coverage); test_dimension_service 16 (10 parity vectors + 6 rule tests); test_live_optional 3 (skipped); test_report_service 2 (required fields, no invented values); test_rss_fetcher 4 (parse, clean/normalise, dedupe, failed feed continues)
- Frontend: search.test.ts 16, pdfReportGenerator.test.ts 2, NewsCard.test.tsx 4, scoring.test.ts 9 (7 analyseText + 2 clusterArticles), scoringParity.test.ts 1 (matches shared/scoring_vectors.json) — Vitest output in this session; test names in [frontend/src/lib/search.test.ts](frontend/src/lib/search.test.ts), [frontend/src/lib/scoring.test.ts](frontend/src/lib/scoring.test.ts), [frontend/src/lib/scoringParity.test.ts](frontend/src/lib/scoringParity.test.ts), [frontend/src/lib/pdfReportGenerator.test.ts](frontend/src/lib/pdfReportGenerator.test.ts), [frontend/src/components/ui/NewsCard.test.tsx](frontend/src/components/ui/NewsCard.test.tsx)
- `shared/scoring_vectors.json` = shared reference inputs and TS outputs used by both parity tests — [backend/services/dimension_service.py:4-8](backend/services/dimension_service.py)

### Inferences
- These counts match PROJECT_STATUS.md ("Backend 62 passed (3 opt-in skipped); frontend 32 passed").

### Gaps
- The tests cover logic only; there is no end-to-end test against real Supabase, real feeds or real models.

---

## 8. What is NOT done or cannot be verified; history; available evidence

### Takeaway
Not done: real model inference in this environment, any labelled-dataset evaluation (no accuracy, precision, recall or F1), confidence calibration, abstractive summaries, use of `user_profiles`, and Supabase Auth. All 25 Nov screenshots come from a rules-only run (status "partial"). The 23 Nov screenshots predate commit `f13a5ad` and show the old bugs. Use them only as "before" evidence, never as current output.

### Cited Findings
- Models are not installed (ModuleNotFoundError for transformers and torch, this session). analyze_example.json shows `model_errors: ModuleNotFoundError: could not load model.`, `analysis_status "partial"`, `model_version "pipeline 2.0; rules only"` — [docs/report/analyze_example.json](docs/report/analyze_example.json)
- PROJECT_STATUS lists calibration and accuracy/precision/recall/F1 as not done, and abstractive summaries replaced by extractive ones — [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
- Pending owner steps: run migration 02, set the service-role key, install models and run validate_models, run reanalyze, run the opt-in tests — [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
- Re-analysis CLI for legacy rows (`--all`, `--regroup`, `--limit 500`) — [backend/scripts/reanalyze.py](backend/scripts/reanalyze.py)
- The analysis_pipeline docstring refers to `docs/PROJECT_REPORT.md`, which does not exist (the report is `docs/Project_Report.pdf`) — [backend/services/analysis_pipeline.py:11](backend/services/analysis_pipeline.py)
- Git history (8 commits): 236fbe4 2026-03-10 first commit; bd2e1d9 2026-10-28 Supabase, live feeds, global search; 4c4802e/e129b8a 2026-11-23 synopsis screenshots; **f13a5ad 2026-11-25 "Integrate 8-dimension analysis into backend pipeline, fix risk defaults, harden API and DB"**; 7394d1f/0618faa/f96fa47 2026-11-25 report, PDF and UML diagrams — `git log` in this session
- `docs/Project_Report.pdf` is 30 pages (pypdf). It states the 25 Nov screens use real BBC World/Al Jazeera items processed by the backend pipeline with models not installed. Its source data is `docs/report/demo_feed_items.json` (41 items: [publisher, category, title, excerpt, url, published_at]) — [docs/report/content.html:305-308](docs/report/content.html); [docs/report/demo_feed_items.json](docs/report/demo_feed_items.json)

**docs/report/img (25 Nov, current code; all rules-only/partial)**
- ui_home.jpg (1200×755): front page, "Ingestion database", 41 reports · 2 publishers, Latest/Breaking/Daily feed, "NEEDS VERIFICATION" tags. **Valid.**
- out_article_top.jpg: BBC "Huawei found guilty…" article, Low Risk 0.15, classifier "Not available", confidence "Not reported", needs verification (52 chars < 150), status partial (pipeline 2.0; rules only), two PDF buttons, "Also reported by" Al Jazeera. **Valid.**
- out_article_analysis.jpg: radar chart + dimension table (Sentiment 50, Bias 84, Objectivity 92, Readability 66, Propaganda 95, Headline 45, Source 93, Content quality 44). **Valid.**
- out_analytics.jpg: 41 reports, 5 multi-source events (10 reports grouped), 41 flagged for verification (100%), risk labels Low 41 / Moderate 0 / High 0 / Not assessed 0, tone Negative 1 / Neutral 40 / Positive 0, dimension averages Sentiment 48, Bias 84, Objectivity 92, Readability 53, Propaganda 95, Headline 56, Source 93, Content 49. **Valid.** Note that every label is Low Risk; explain this as short excerpts from reputable outlets, with the verification flag carrying the uncertainty.
- out_compare.jpg: "One story, many newsrooms", 5 events with 2 publishers each (e.g. Ábrego García BBC vs AlJazeera, showing the accent folding), per-article tone/dimension bars. **Valid.**
- out_report.jpg (662×936): backend ReportLab PDF page for the Huawei article, Generated 25 Nov 2026 05:09 UTC, Status partial · Method rules. **Valid.**
- io_search.jpg: search "russia", 6 reports match every term, database search note. **Valid.**
- io_verify.jpg: Sports + needs-verification filter, 3 reports. **Valid.**
- ui_register.jpg: reader register modal over the blurred front page. **Valid.**
- ui_mobile.jpg (739×1600): mobile article view. **Valid.**
- mitwpu_logo.jpg: institution logo (not app output).

**synopsis_screenshots/ (23 Nov, BEFORE fixes)**
- 13_article_detail_top.png: Al Jazeera Iran article "LOW RISK", **risk score 1.00**, "Not flagged", reasoning "…with 0% confidence". **UNSAFE** (shows the old bug).
- 20_analytics_dashboard.png: 70 reports / 9 publishers, Low Risk 70, 0 flagged, **all dimension averages 0**. **UNSAFE.**
- 30_api_analytics.png: JSON with `risk: Low Risk 70`, all dimension_averages null, needs_verification 0. **UNSAFE.**
- 25_api_docs.png / 31_api_docs_analyze_schema.png: Swagger "AI News Aggregator API 1.0.0", no /ingest, analyze request `{text}` only, response `{sentiment,is_fake,credibility_score}`. **OUTDATED** (current version 2.0.0, 8 routes; the analyze schema has changed).
- 26_api_health.png: `{"status":"healthy"}` only (the current health response has more fields). **OUTDATED.**
- 27/28/29 api JSON: same pre-fix period; treat as outdated (not inspected in detail; they date from before commit f13a5ad).
- 01–12, 14–24 UI screenshots: old UI from the same run. Anything showing risk labels or scores (14, 16–19, 21, 23, 24, 04) should be treated as **UNSAFE**. Neutral views such as 01/02 (register modal), 22 (404 page) and section layouts are visually usable but superseded by docs/report/img.
- article_credibility_report.pdf / article_report_server.pdf: pre-fix PDFs. **UNSAFE.**
- supabase/03_table_definition_articles.png: articles DDL with `credibility_label … default 'Low Risk'` and no v2 columns. **Pre-migration; UNSAFE as the current schema** (usable only as "before migration 02").
- supabase/08_schema_visualizer.png: 3 tables, user_profiles → auth.users link, no v2 columns. Usable for the table relationships, but the column list is outdated.
- supabase/12_rls_policies.png: articles show "public insert" and "public update" policies (later removed by migration 02). **UNSAFE as current.**
- supabase/10_database_indexes.png: indexes without idx_articles_source_url and analysis_status. Outdated.
- supabase/01 project overview, 04–07 named_visitors/user_profiles editors and definitions, 09 tables list, 11 functions, 15 auth users, 16 PostgREST docs, 17–19 reports and logs: environment evidence. Generally still valid for describing the Supabase project; not individually inspected beyond the index file.

**docs/report/diagrams/*.svg (current)**: activity (ingestion flow, 15 s timeout, 30 min), architecture (layers; presentation "read-only Supabase key"), class, modules, object (bbc Source reputation 93, Huawei article, 52 chars, groupId ev-…), sequence (Reader → Next.js → Supabase; PDF via FastAPI /api/report/{id}), usecase (Scheduler, Reader actors) — [docs/report/diagrams/](docs/report/diagrams/)

### Inferences
- For the final report: present the system as "implemented and unit-tested; demonstrated in rules-only mode". Model-based scoring is wired in and tested with fake pipelines, but it has not been executed on real weights. State this explicitly and claim no accuracy figures.
- The before/after pair 13_article_detail_top.png (Low Risk, 1.00) vs. out_article_top.jpg (Low Risk 0.15, needs verification, reasoning) can be shown honestly in a "bugs fixed" section.

### Gaps
- Real model outputs, label-mapping confirmation, live Supabase state and live feed availability could not be verified. Screenshots 27–29 and most Supabase screenshots were not opened individually; they are classified by date and the index text only.
