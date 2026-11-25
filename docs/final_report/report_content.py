"""Chapter text of the final report (concise edition, 40-45 pages in total).

Every number below comes from the code (file named next to it) or from the test runs of 25 Nov 2026.
Figures, tables and listings are numbered per chapter; {fig:key}, {tab:key} and {lst:key} in the text
are replaced by "Figure 3.1", "Table 1.2", ... The eight design diagrams (DIAG) are each printed alone on
their own page, at full text width, with the caption below.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNG = Path(__file__).resolve().parent / "png"
IMG = ROOT / "docs" / "report" / "img"
SCREENS = Path(__file__).resolve().parent / "screens"


def register_crop():
    """The registration modal cut out of the full-page screenshot (docs/report/img/ui_register.jpg)."""
    from PIL import Image
    SCREENS.mkdir(exist_ok=True)
    out = SCREENS / "ui_register_modal.jpg"
    Image.open(IMG / "ui_register.jpg").crop((372, 222, 828, 532)).save(out, quality=92)
    return out


REGISTER_CROP = register_crop()


def src_excerpt(rel, start, end, dedent=True):
    """Lines from the first line containing `start` up to and including the first later line containing `end`."""
    lines = (ROOT / rel).read_text(encoding="utf-8").split("\n")
    i = next(k for k, l in enumerate(lines) if start in l)
    j = i + end - 1 if isinstance(end, int) else next(k for k in range(i, len(lines)) if end in lines[k])
    chunk = lines[i:j + 1]
    if dedent:
        pad = min(len(l) - len(l.lstrip()) for l in chunk if l.strip())
        chunk = [l[pad:] for l in chunk]
    return "\n".join(chunk), i + 1, j + 1


def C(rel, start, end):
    text, a, b = src_excerpt(rel, start, end)
    return text, f"{rel}, lines {a}–{b}"


# ─── content blocks ─────────────────────────────────────────────────────────────────────────

def H1(num, title): return ("h1", num, title)
def H2(num, title): return ("h2", num, title)
def H3(title): return ("h3", None, title)
def P(text): return ("p", text)
def BL(*items): return ("bullets", list(items))
def TAB(key, caption, header, rows, widths, size=10.5, first_bold=False): return ("table", key, caption, header, rows, widths, size, first_bold)
def FIG(key, path, caption, width=None, max_h=19.5): return ("fig", key, path, caption, width, max_h, False)
def DIAG(key, name, caption): return ("fig", key, PNG / f"{name}.png", caption, None, 22.75, True)
def CODE(key, caption, text, size=8.5): return ("code", key, caption, text, size)


def analyze_example():
    ex = json.loads((ROOT / "docs" / "report" / "analyze_example.json").read_text())
    return ex["request"], ex["response"]


def blocks():
    rr1, a1 = C("backend/services/dimension_service.py", "MIN_EVIDENCE_CHARS = 150", "UNCERTAINTY_BAND = (0.4, 0.6)")
    rr2, a2 = C("backend/services/dimension_service.py", "def rule_risk(dims", "return round2(1 - composite), weight")
    rule_risk = rr1 + "\n...\n" + rr2
    rule_src = a1 + " and " + a2.split(", ")[1]
    pipe, pipe_src = C("backend/services/analysis_pipeline.py", "rule_score, _ = rule_risk(dims)", "needs_verification = bool(flags)")
    clf, clf_src = C("backend/services/ai_service.py", 'fake = scores.get(FAKE_LABEL, scores.get("FAKE"))', 16)
    repo, repo_src = C("frontend/src/lib/repository.ts", "async function loadDatabaseArticles()", 17)
    repo2, repo2_src = C("frontend/src/components/analysis/ReportDownload.tsx", "const serverReport = backendUrl", ": null;")
    req, resp = analyze_example()
    d = resp["dimensions"]

    B = []
    # ════════════════════════════════ Chapter 1 ════════════════════════════════
    B += [
        H1("1", "Introduction"),
        P("Online news is published continuously by many newsrooms, and the same event appears under different "
          "headlines, wording and levels of detail. A reader who wants a balanced picture must visit several sites and "
          "cannot easily tell which reports use one-sided or sensational language, or which headlines are not supported "
          "by the text."),
        P("The **AI-Powered News Aggregator with Advanced Credibility and Content Analysis** is a web application that "
          "collects news from selected RSS feeds, removes exact duplicates, analyses each article with transparent rules "
          "and, when installed, two transformer models, groups reports of the same event from different publishers, and "
          "presents the results in a newspaper-style dashboard named *The Daily Signal*. For every article it shows a "
          "credibility-risk indicator, a sentiment label, eight explained content-analysis scores, a Needs Verification "
          "flag, an extractive summary when the excerpt is long enough, related coverage and a downloadable PDF report. "
          "The outputs are reading aids, not verdicts of truth; the link to the original report is always kept. This "
          "report describes the system as implemented in the repository and states every difference from the synopsis "
          "(Chapter 7)."),

        H2("1.1", "Existing System"),
        BL("**Publisher websites and apps** present one newsroom; comparing coverage requires visiting several sites.",
           "**General news aggregators** collect headlines from many sources but explain nothing about tone, balance, "
           "sensational framing or headline support.",
           "**Fact-checking websites** verify claims manually; they are reliable but cover only a small number of stories.",
           "**Automatic fake-news classifiers** in research output a single label [3] that does not say why an article "
           "looks risky or how much text the decision used."),

        H2("1.2", "Need for System"),
        BL("Reduce the effort of following one event across sources by collecting articles automatically and showing "
           "related reports together.",
           "Replace a single unexplained number with several explained indicators and a separate verification flag.",
           "State clearly when the available text is too short for a judgement, instead of showing a default score.",
           "Keep the original link so that every indicator can be checked against the full article."),

        H2("1.3", "Scope of System"),
        P("**In scope.** English-language news from public RSS feeds: 11 backend feeds in five categories (BBC, CNN, "
          "Yahoo, Al Jazeera; `backend/services/rss_fetcher.py`), collected every 30 minutes; a frontend fallback of 31 "
          "feed URLs in eight sections when the database is empty (`frontend/src/lib/sections.ts`); and external search "
          "through Google News RSS, GNews or GDELT DOC 2.0 when few stored reports match (`externalSearch.ts`). The "
          "system analyses the headline and feed excerpt, scores risk, sentiment and eight dimensions, writes extractive "
          "summaries, groups related reports, and provides search, filters, analytics, PDF reports and a REST API."),
        P("**Out of scope.** Verifying factual claims; downloading full article bodies; languages other than English; "
          "password-based accounts (only a display name is stored); training or fine-tuning models; and measuring model "
          "accuracy, since no labelled dataset was used."),

        H2("1.4", "Operating Environment - Hardware and Software"),
        P("{tab:env} lists the operating environment. Software versions are the minimum versions declared in "
          "`backend/requirements.txt`, `backend/Dockerfile` and `frontend/package.json`. The hardware figures are a "
          "recommendation, not a measurement, because the transformer models were not executed during development. "
          "The tests in Chapter 5 were run with Python 3.13.18 and Node.js 22.23.5."),
        TAB("env", "Operating environment (hardware recommended, not measured)",
            ["Item", "Requirement"],
            [["Processor / RAM", "64-bit dual-core CPU and 4 GB RAM (rules-only mode); quad-core and 8 GB RAM recommended with both models"],
             ["Storage / network", "2–5 GB free disk (packages and model files); internet access to the RSS feeds, Supabase and, on first use, the Hugging Face Hub"],
             ["Operating system", "Windows 10/11, Linux or macOS"],
             ["Backend runtime", "Python 3.10 or later (Dockerfile: python:3.10-slim, port 7860); Uvicorn"],
             ["Frontend runtime", "Node.js 20 or later (required by Next.js 16)"],
             ["Database", "Supabase project (hosted PostgreSQL with Row Level Security)"],
             ["Client", "Current Chrome, Edge or Firefox on desktop or mobile"]],
            [3.6, 12.3], first_bold=True),

        H2("1.5", "Brief Description of Technology Used"),
        P("{tab:tech} summarises the technologies and their roles. The backend is written in Python and the frontend in "
          "TypeScript; both implement one scoring method, checked by shared test vectors (`shared/scoring_vectors.json`)."),
        TAB("tech", "Technology stack and role of each technology",
            ["Technology (version)", "Role in this project"],
            [["FastAPI >=0.110, Uvicorn, Pydantic >=2.6", "REST API (`backend/main.py`, `api/router.py`): eight routes under /api and /api/v1, validation, CORS allow-list, rate limit."],
             ["feedparser, httpx, BeautifulSoup4", "Download feeds (15 s timeout), parse entries, strip HTML (`rss_fetcher.py`)."],
             ["APScheduler >=3.11", "Collect-analyse-store-group job every 30 minutes without overlapping runs (`scheduler.py`)."],
             ["Transformers >=4.38, PyTorch >=2.2", "Optional models loaded on first use (`ai_service.py`): `mrm8488/bert-tiny-finetuned-fake-news-detection` and `distilbert-base-uncased-finetuned-sst-2-english`."],
             ["Supabase (PostgreSQL), supabase-py, supabase-js", "Storage with Row Level Security; backend writes with the service-role key, frontend reads with the anon key."],
             ["ReportLab >=4.1, jsPDF ^4.2", "Server-side PDF (GET /api/report/{id}) and browser-side PDF report."],
             ["Next.js 16.1.6, React 19.2.3, TypeScript, Tailwind CSS ^4", "Server-rendered pages and six Next.js API routes; responsive newspaper layout."],
             ["Recharts ^3.7", "Eight-dimension radar chart and analytics charts."],
             ["pytest, Vitest, Testing Library", "Backend (66 tests, 3 opt-in) and frontend (32 tests) suites."]],
            [5.2, 10.7]),
        P("BERT-tiny, a very small BERT model [1] fine-tuned for fake-news detection, supplies a fake-class softmax "
          "score. DistilBERT [2] fine-tuned on the binary SST-2 dataset [4] supplies a positive-class score that is "
          "mapped to a 0–100 sentiment scale. Readability uses the Flesch Reading Ease formula [5], and event grouping "
          "uses TF-IDF weighting with cosine similarity [6]. None of these scores is calibrated."),
    ]

    # ════════════════════════════════ Chapter 2 ════════════════════════════════
    B += [
        H1("2", "Proposed System"),
        P("The proposed system turns RSS entries into analysed, grouped and searchable articles, giving several "
          "explained indicators instead of one verdict. It consists of a FastAPI backend pipeline, a Supabase PostgreSQL "
          "database and a Next.js web application. {tab:feas} summarises its feasibility."),
        H2("2.1", "Feasibility Study"),
        TAB("feas", "Feasibility study",
            ["Aspect", "Assessment"],
            [["Technical", "Mature open-source libraries; all components except the models were built and tested. The small models are expected to run on a CPU (not measured: not installed). Supabase needs no server maintenance."],
             ["Economic", "Libraries, models and RSS feeds are free; the Supabase free tier suffices. The only cost is development time."],
             ["Operational", "No training needed; every score is explained. Collection is automatic and failures are logged without stopping the run."],
             ["Schedule", "Staged work (requirements, collection, analysis, storage and API, interface, reports, testing) fitted the semester."]],
            [2.8, 13.1], size=10, first_bold=True),
        H2("2.2", "Objectives of Proposed System"),
        P("The synopsis defines thirteen objectives: collect, clean and de-duplicate articles from multiple RSS sources; "
          "estimate credibility risk with a transformer classifier and its confidence; classify sentiment; produce short "
          "summaries; compare coverage of one event across publishers; score eight content dimensions; raise a Needs "
          "Verification flag; store articles with search and filters; provide analytics and PDF reports; and evaluate "
          "the models. Their implementation status is given in {tab:synvs} (Chapter 7)."),
        H2("2.3", "Users of System"),
        P("{tab:users} lists the users. The Scheduler is a system actor because it starts ingestion by itself."),
        TAB("users", "Users of the system",
            ["User", "Description", "Main functions"],
            [["Reader", "Visitor (display name only)", "Register, browse, search and filter, read analyses, compare coverage, view analytics, download PDFs"],
             ["Operator / API client", "Developer using the REST API", "Analyse text (POST /api/analyze); read articles, groups, analytics; trigger ingestion with a token"],
             ["Scheduler", "APScheduler job in FastAPI", "Collect, de-duplicate, analyse, store and group articles every 30 minutes"]],
            [3.4, 4.6, 7.9], size=10, first_bold=True),
    ]

    # ════════════════════════════════ Chapter 3 ════════════════════════════════
    B += [
        H1("3", "Analysis and Design"),
        P("This chapter states the requirements, presents the eight design diagrams of the college format, each drawn "
          "from the implemented code and printed on its own page, and shows sample input and output screens."),
        H2("3.1", "System Requirements (Functional and Non-Functional requirements)"),
        TAB("fr", "Functional requirements",
            ["No.", "Requirement", "Implemented in"],
            [["FR1", "Collect title, publisher, URL, category, excerpt and time from the RSS feeds every 30 minutes.", "rss_fetcher.py, scheduler.py"],
             ["FR2", "Strip HTML and skip duplicates by normalised title and URL, within a batch and against the database.", "rss_fetcher.py, db_service.py"],
             ["FR3", "Score eight dimensions with explanations; leave a dimension unscored when it cannot be measured.", "dimension_service.py, scoring.ts"],
             ["FR4", "Run the classifier and the sentiment model when available; otherwise report them as unavailable.", "ai_service.py"],
             ["FR5", "Compute a risk score, a label (Low / Moderate / High or not assessed) and a Needs Verification flag.", "analysis_pipeline.py"],
             ["FR6", "Group reports of the same event from at least two publishers.", "clustering_service.py, clustering.ts"],
             ["FR7", "Search by keywords; filter by section, publisher, risk, verification flag and date.", "search/page.tsx, repository.ts, search.ts"],
             ["FR8", "Show the article page with credibility panel, radar chart and dimension table.", "article/[id]/page.tsx"],
             ["FR9", "Show analytics of the current edition.", "analytics/page.tsx"],
             ["FR10", "Generate a PDF report of an article.", "report_service.py, pdfReportGenerator.ts"],
             ["FR11", "Register a reader display name (1–40 characters).", "NameAuthModal.tsx, api/auth/profile"],
             ["FR12", "Analyse custom text through the API without storing it.", "router.py (POST /analyze)"]],
            [1.3, 10.2, 4.4], size=10),
        TAB("nfr", "Non-functional requirements",
            ["Requirement", "How it is met"],
            [["Usability", "Newspaper layout, plain-language explanations, responsive design for mobile screens."],
             ["Reliability", "Feed timeouts (15 s backend, 8 s frontend); failures are logged and the run continues; a lock prevents overlapping runs."],
             ["Transparency", "Every score is explained; model scores are labelled raw and uncalibrated; missing values are shown as \"n/a\" or \"Not available\", never as defaults."],
             ["Security", "Public key read-only on articles (RLS); service-role key only on the server; CORS allow-list; input validation; 30 requests per minute per client on /analyze and /report."],
             ["Maintainability", "Separate modules; one scoring method mirrored in Python and TypeScript and checked by shared vectors; idempotent SQL migrations."],
             ["Performance", "Models load once on first use; the 500-row edition is cached for 60 s and live feeds for 2 min. No load test was performed."]],
            [3.0, 12.9], size=10, first_bold=True),
        P("The rule-based risk is the inverse of a weighted average of five dimensions ({tab:risk}); only scored "
          "dimensions count, and no risk is given when they carry less than 65 % of the weight. When the classifier runs, "
          "the final risk is the mean of the rule-based risk and the classifier's fake-class score. {tab:dims} defines the "
          "eight dimensions, computed identically in `dimension_service.py` and `scoring.ts`."),
        TAB("risk", "Risk computation, labels and Needs Verification conditions",
            ["Item", "Value (dimension_service.py, analysis_pipeline.py)"],
            [["Weights", "Source Credibility 0.35; Propaganda 0.20; Objectivity 0.15; Bias 0.15; Headline Accuracy 0.15"],
             ["Rule-based risk", "1 − Σ(score × weight) / Σ(weight) / 100 over scored dimensions; none if Σ(weight) < 0.65"],
             ["Final risk / labels", "mean(rule risk, classifier fake score) if the classifier ran; Low ≤ 0.35 < Moderate ≤ 0.65 < High"],
             ["Needs Verification", "No risk score; score in 0.40–0.60; < 150 characters of text; classifier confidence < 0.60; |classifier − rules| ≥ 0.50"],
             ["Analysis status", "complete (both models ran), partial (rules only or one model), unavailable (no score)"]],
            [3.3, 12.6], size=10, first_bold=True),
        TAB("dims", "The eight content dimensions (0–100)",
            ["Dimension", "Measurement", "Unscored when"],
            [["Sentiment", "50 + 9 × (positive − negative cue words), 5–95; DistilBERT positive score × 100 when available; 41–59 = neutral", "never"],
             ["Bias", "90 − 15 per loaded term, − 6 without attribution (\"said\", \"according to\"); min. 20", "never"],
             ["Objectivity", "92 − 14 per evaluative adjective; min. 20", "never"],
             ["Readability", "Flesch Reading Ease of headline and excerpt", "headline only"],
             ["Propaganda", "95 − 22 per clickbait pattern − 10 per shouted headline word; min. 5", "never"],
             ["Headline Accuracy", "45 + 50 × share of headline key terms found in the excerpt", "no excerpt"],
             ["Source Credibility", "Curated table of 14 newsrooms (e.g. Reuters 95, BBC 93, Al Jazeera 86)", "unknown publisher"],
             ["Content Quality", "35 + min(characters, 600)/12 + 5 × min(sentences, 4)", "no excerpt"]],
            [3.1, 10.2, 2.6], size=10, first_bold=True),

        H2("3.2", "Module Hierarchy Diagram"),
        P("{fig:modules} decomposes the source tree. The backend has six module groups: collection, analysis, "
          "grouping, storage, API and reports, and maintenance scripts. The frontend has seven: data access, live and "
          "external news, scoring, reports, pages, API routes and components. `repository.ts` is the single "
          "data-access module of the frontend, and the shared parity vectors connect the Python and TypeScript scoring "
          "tests."),
        DIAG("modules", "modules", "Module hierarchy diagram (backend/, frontend/src/, shared/)"),

        H2("3.3", "Architecture Diagram"),
        P("{fig:arch} shows two independent paths. In the **ingestion path**, inside the FastAPI process, the scheduler "
          "fetches the feeds, the analysis pipeline scores each new article and `db_service.py` writes it to Supabase "
          "with the service-role key. In the **read path** the Next.js server reads Supabase directly with the read-only "
          "anon key (500 newest rows, 60-second cache) and renders the pages; it falls back to live feeds scored in "
          "TypeScript when the database is empty. The browser contacts FastAPI only for the optional server-side PDF, "
          "and only when `NEXT_PUBLIC_API_URL` is set. {tab:api} lists the REST interfaces of both servers; each FastAPI "
          "route is mounted under `/api` and `/api/v1`."),
        TAB("api", "REST interfaces (backend/api/router.py; frontend/src/app/api/)",
            ["Server", "Method and path", "Input → output"],
            [["FastAPI", "GET /health", "– → status, database configured, model state, last ingestion run"],
             ["FastAPI", "POST /analyze", "text (1–20,000 chars), title, publisher → full analysis, not stored; 422 on invalid input"],
             ["FastAPI", "GET /articles", "limit 1–200, offset, category, risk, q, needs_verification → list; 503 on database error"],
             ["FastAPI", "GET /article/{id}", "UUID → one article; 404 if absent; 422 for a malformed id"],
             ["FastAPI", "GET /groups, GET /analytics", "– / limit → multi-publisher groups; counts and dimension averages"],
             ["FastAPI", "GET /report/{id}", "UUID → application/pdf attachment; rate-limited"],
             ["FastAPI", "POST /ingest", "X-Ingest-Token → run summary; 404 unless INGEST_TOKEN is set, 403 for a wrong token"],
             ["Next.js", "GET /api/articles, /api/article/[id]", "query, filters, page → articles of the current edition"],
             ["Next.js", "GET /api/groups, /api/analytics", "– → groups and analytics of the edition"],
             ["Next.js", "GET /api/search/external", "q, since → external results; 400 if q is empty, 502 if unavailable"],
             ["Next.js", "POST /api/auth/profile", "{name} → row in named_visitors; 400 if the name is empty"]],
            [1.9, 5.0, 9.0], size=9.5),
        DIAG("arch", "architecture", "Architecture diagram: ingestion through FastAPI, reading directly from Supabase"),

        H2("3.4", "Class Diagram"),
        P("{fig:class} models the core data. An Article belongs to one source and is composed of exactly one "
          "CredibilityResult, one DimensionAnalysis and one SentimentResult, and of at most one Summary; it may belong "
          "to one ArticleGroup, which has at least two articles. The backend is written in a functional style, so the "
          "operations are module-level functions. Multiplicity [0..1] on an attribute means that the value may be "
          "missing; it is never replaced by zero or a default."),
        P("Physically, all article data is stored in one `articles` table, with the eight scores and explanations in a "
          "JSONB column; related reports share a `group_id` value without a foreign key ({tab:schema}). Row Level "
          "Security makes articles read-only for the public key. The `user_profiles` table is defined in the SQL but no "
          "code reads or writes it."),
        TAB("schema", "Database schema (backend/db/supabase_complete_setup.sql)",
            ["Table.column(s)", "Type", "Constraint / meaning"],
            [["articles.id", "uuid", "Primary key, gen_random_uuid()"],
             ["articles.title", "text", "NOT NULL, UNIQUE (database-level duplicate check)"],
             ["articles.source_domain, source_url", "text", "Publisher name and original link (source_url indexed)"],
             ["articles.content_summary, category", "text", "Feed excerpt; category (default 'general')"],
             ["articles.published_at, created_at", "timestamptz", "Publication time; ingestion time"],
             ["articles.sentiment", "text", "positive / neutral / negative"],
             ["articles.risk_score", "real", "CHECK 0–1 or NULL"],
             ["articles.credibility_label", "text", "Low / Moderate / High Risk or NULL (= not assessed); no default"],
             ["articles.needs_verification", "boolean", "Verification flag (default false)"],
             ["articles.confidence_level, model_fake_probability", "real", "Classifier scores (uncalibrated; NULL without model)"],
             ["articles.dimensions", "jsonb", "Eight scores (or null) and explanations"],
             ["articles.ai_reasoning, ai_summary, summary_method", "text", "Explanation; extractive summary and its method"],
             ["articles.group_id, event_title", "text", "Cross-source group (group_id indexed)"],
             ["articles.analysis_status, analysis_method, model_version, analyzed_at", "text, timestamptz", "Provenance; status CHECK complete / partial / unavailable / pending / legacy"],
             ["named_visitors.id, name, created_at", "uuid, text, timestamptz", "Primary key; name UNIQUE, 1–40 characters"],
             ["user_profiles.id, name, saved_topics, created_at", "uuid, text, text[], timestamptz", "id references auth.users(id); defined but unused"]],
            [6.3, 2.9, 6.7], size=9.5),
        DIAG("class", "class", "Class diagram of the core data (operations are module-level functions)"),

        H2("3.5", "Use-case Diagram"),
        P("In {fig:usecase} the Scheduler starts the ingestion cycle every 30 minutes; the cycle includes collection, "
          "duplicate removal, analysis and grouping. The Operator can start the cycle with POST /api/ingest (ingest "
          "token) and analyse custom text. Of the Reader's eight use cases, searching is extended by external search."),
        H2("3.6", "Sequence Diagram"),
        P("In {fig:sequence} a reader opens an article and downloads its report. `getEdition()` queries Supabase only "
          "when the cached edition is older than 60 seconds. The PDF is produced either by FastAPI with ReportLab (database "
          "articles, backend URL configured) or in the browser with jsPDF."),
        H2("3.7", "Activity Diagram"),
        P("{fig:activity} shows one ingestion run (`fetch_and_store_job`). The first loop downloads every feed and logs "
          "failures without stopping. After in-batch de-duplication, the second loop skips stored articles, scores and "
          "classifies the rest, computes the risk or marks it not assessed, sets the flag and inserts the article. "
          "Articles of the last 48 hours are then re-grouped."),
        H2("3.8", "Component Diagram"),
        P("In {fig:component} (UML 2) the Next.js subsystem provides the pages and `/api/*` routes; `repository.ts` "
          "depends on the live-feed, external-search and scoring components. The FastAPI subsystem provides the REST API; "
          "the router uses the report service, pipeline and storage service, and the scheduler drives the RSS fetcher and "
          "storage. Supabase provides one interface (PostgREST) required by both subsystems."),
        H2("3.9", "Deployment Diagram"),
        P("{fig:deployment} shows the deployment supported by the code: the browser uses the Next.js server (Node.js 20+) "
          "and, for the optional server PDF, the backend (Python 3.10+, Uvicorn; Dockerfile image python:3.10-slim, port "
          "7860). Both servers reach Supabase over HTTPS with different keys. The system was run locally; no production "
          "deployment is claimed."),
        DIAG("usecase", "usecase", "Use-case diagram"),
        DIAG("sequence", "sequence", "Sequence diagram: viewing an article and downloading its PDF report"),
        DIAG("activity", "activity", "Activity diagram of one ingestion run"),
        DIAG("component", "component", "Component diagram (UML 2)"),
        DIAG("deployment", "deployment", "Deployment diagram (UML 2)"),

        H2("3.10", "Sample Input and Output Screens"),
        P("The screens were captured on 25 November 2026 from the running application, using 41 real BBC World and "
          "Al Jazeera RSS items processed by the backend pipeline. The models were **not installed**, so all analysis is "
          "rules-only: status \"partial\", classifier fields \"Not available\", and every item flagged Needs "
          "Verification because RSS excerpts are short."),
        P("**Input: registration and search.** A first-time reader enters a display name of 1–40 characters "
          "({fig:register}), stored in `named_visitors` through POST /api/auth/profile. The search page ({fig:search}) "
          "filters by section, publisher, risk (including \"Not assessed\"), order, date and \"Needs verification only\"."),
        FIG("register", REGISTER_CROP, "Input: reader registration modal (first visit)", width=7.2),
        FIG("search", IMG / "io_search.jpg", "Input and output: search for \"russia\" with filters, newest first", width=9.6),
        P("**Output: article analysis.** The article page ({fig:article}) shows the excerpt, the original link and the "
          "credibility panel. For this BBC article the rule-based risk is 0.15 (Low Risk); it needs verification "
          "because the feed supplied only 52 characters, and \"Also reported by\" lists the grouped Al Jazeera report. "
          "The analysis supplement ({fig:analysis}) shows the radar chart and the eight scores with explanations."),
        FIG("article", IMG / "out_article_top.jpg", "Output: article page with credibility panel (rules-only analysis)", width=10),
        FIG("analysis", IMG / "out_article_analysis.jpg", "Output: eight-dimension radar chart and score table", width=13.5),
        P("**Output: cross-source comparison.** The compare page ({fig:compare}) lists the five events covered by both "
          "publishers; accent folding matches \"Ábrego García\" (BBC) with \"Abrego Garcia\" (Al Jazeera)."),
        FIG("compare", IMG / "out_compare.jpg", "Output: events covered by more than one publisher", width=9.5),
        P("**Input/output: analyse-text API.** {tab:analyze} shows a real call of POST /api/analyze in rules-only mode "
          "(`docs/report/analyze_example.json`). The sensational text receives Propaganda 5 but only Moderate Risk 0.57, "
          "because the unknown blog has no Source Credibility score and the other dimensions dilute the penalty "
          "(Chapter 8)."),
        TAB("analyze", "Sample input and output of POST /api/analyze (rules-only mode)",
            ["Field", "Value"],
            [["Input: title", req["title"]],
             ["Input: text", req["text"]],
             ["Input: publisher", req["publisher"]],
             ["Output: risk, label", f"{resp['risk_score']}, {resp['credibility_label']}; needs_verification = {str(resp['needs_verification']).lower()}"],
             ["Output: classifier", f"model_fake_probability = null, confidence_level = null; status {resp['analysis_status']}, method {resp['analysis_method']}"],
             ["Output: dimensions", f"sentiment {d['sentiment']}, bias {d['bias']}, objectivity {d['objectivity']}, readability {d['readability']}, propaganda {d['propaganda']}, headline accuracy {d['headline_accuracy']}, source credibility null, content quality {d['content_quality']}"],
             ["Output: reasoning", resp["ai_reasoning"]]],
            [3.4, 12.5], size=9.5, first_bold=True),
    ]

    # ════════════════════════════════ Chapter 4 ════════════════════════════════
    B += [
        H1("4", "Coding"),
        P("The backend is a FastAPI application whose lifespan starts the scheduler. The analysis engine was first "
          "written in TypeScript for live feeds and then ported to Python, so both servers use one scoring method; "
          "`js_round()` reproduces JavaScript's `Math.round` to give identical numbers. To run the system: execute "
          "`supabase_complete_setup.sql` in Supabase; in `backend`, install `requirements.txt`, set `SUPABASE_URL` and "
          "`SUPABASE_SERVICE_ROLE_KEY` and start `uvicorn main:app`; in `frontend`, set the public Supabase URL and anon "
          "key and run `npm install` and `npm run dev`."),
        H2("4.1", "Code snippets"),
        P("The excerpts below are copied unchanged from the source; file and line numbers are given in each caption. "
          "{lst:rule} defines the risk constants and turns the scored dimensions into a rule-based risk: a dimension "
          "that is `None` is skipped, and no score is returned below 65 % of the weight."),
        CODE("rule", f"Weights, thresholds and rule_risk() ({rule_src})", rule_risk),
        P("{lst:pipe} is the core of `analyze_article()`: the final risk is the mean of the rule-based risk and the "
          "classifier's fake-class score when the classifier ran, and each verification condition adds a readable "
          "reason."),
        CODE("pipe", f"Risk combination and verification flags ({pipe_src})", pipe),
        P("The BERT-tiny configuration does not name its labels, so the fake label is configurable "
          "(`FAKE_NEWS_FAKE_LABEL`, default `LABEL_1`). {lst:clf} derives the fake-class score and the confidence and "
          "rejects unexpected labels instead of guessing."),
        CODE("clf", f"Label mapping in classify_fake_news() ({clf_src})", clf),
        P("{lst:repo} shows the read path: the Next.js server reads the edition directly from Supabase with the anon "
          "key and caches it for 60 seconds; on failure or an empty table it returns `null` and the live-feed fallback "
          "is used. The server PDF link exists only for database articles when a backend URL is configured."),
        CODE("repo", f"loadDatabaseArticles() ({repo_src}) and server PDF link ({repo2_src.replace(', lines', ', lines')})",
             repo + "\n...\n" + repo2),
    ]

    # ════════════════════════════════ Chapter 5 ════════════════════════════════
    B += [
        H1("5", "Testing Process"),
        P("Testing verifies that each module produces the specified output, never invents a missing value and handles "
          "failures. It does not measure model accuracy, which would require a labelled dataset and the installed "
          "models."),
        H2("5.1", "Test Planning"),
        TAB("plan", "Test plan",
            ["Item", "Plan"],
            [["Scope", "All backend services and the API; frontend scoring, grouping, search, PDF generator and news card; build, lint and type check."],
             ["Out of scope", "Model accuracy and calibration; load testing; live feeds and live Supabase in the automated suite."],
             ["Test doubles", "FakePipeline with fixed label scores; in-memory FakeSupabase client; httpx MockTransport for feeds; mocked fetch for GDELT and GNews."],
             ["Tools", "pytest 9.1.1; Vitest 4.0.18 with Testing Library and jsdom; ESLint; TypeScript compiler; Next.js build."],
             ["Entry / exit criteria", "Entry: module implemented and runnable. Exit: all automated tests pass, lint and type check clean, build succeeds; opt-in tests that cannot run are reported as not executed."],
             ["Opt-in tests", "RUN_MODEL_TESTS=1 (real models); RUN_LIVE_TESTS=1 (real feeds and Supabase)."]],
            [3.0, 12.9], size=10, first_bold=True),
        P("{tab:plan} summarises the plan. External services were replaced by test doubles, so the suites run without "
          "network access, credentials or model downloads."),
        H2("5.2", "Software Testing Life Cycle (STLC)"),
        TAB("stlc", "STLC phases as applied",
            ["Phase", "Activities and output"],
            [["Requirement analysis", "Testable rules extracted from the code: thresholds (0.35, 0.65, 150 characters, 0.32), null rules, status values, API limits."],
             ["Test planning", "Levels, tools, test doubles, opt-in tests and exit criteria fixed ({tab:plan})."],
             ["Test case design", "66 backend and 32 frontend test cases, including boundary values (risk 0.35/0.36/0.65/0.66) and failure cases (HTTP 500 feed, model load failure, database down)."],
             ["Environment set-up", "pytest markers, conftest fixtures (fake_models, no_models, ENABLE_SCHEDULER=0), shared scoring vectors, Vitest with jsdom."],
             ["Test execution", "Suites run after each change and again on 25 November 2026 ({tab:exec})."],
             ["Test closure", "Defects fixed with regression tests (e.g. Al Jazeera source score); untested areas recorded in Chapter 8."]],
            [3.4, 12.5], size=10, first_bold=True),
        H2("5.3", "Types of Testing"),
        TAB("types", "Types of testing",
            ["Type", "Done", "How"],
            [["Unit", "Yes", "Dimension rules, label mapping, extractive summary, URL normalisation, search ranking, risk thresholds."],
             ["Integration (with fakes)", "Yes", "Pipeline with FakePipeline models; store-and-group with the in-memory database; feeds with a mock transport."],
             ["API", "Yes", "TestClient: 422 validation, 404, 503 without leaked errors, PDF response, CORS, ingest token, 429 rate limit."],
             ["Parity", "Yes", "Python and TypeScript outputs compared on ten reference inputs (shared/scoring_vectors.json)."],
             ["Regression / UI component", "Yes", "Tests for fixed defects; NewsCard rendering; PDF generator output."],
             ["Build and static checks", "Yes", "npm run build, npm run lint, tsc --noEmit."],
             ["End-to-end demonstration", "Manual", "41 real items processed in rules-only mode and viewed in the running application (Section 3.10)."],
             ["Model accuracy / calibration", "No", "No labelled dataset; models not installed."],
             ["Live integration / load", "No", "Opt-in live and model tests not executed (no network or credentials); no load test."]],
            [4.0, 1.5, 10.4], size=10, first_bold=True),
        H2("5.4", "Sample Test Cases"),
        P("{tab:cases} lists representative test cases from the test files (function names in brackets)."),
        TAB("cases", "Sample test cases (run of 25 November 2026)",
            ["ID", "Module (test)", "Input", "Expected result", "Status"],
            [["TC01", "Scoring parity (test_dimension_service, scoringParity.test)", "10 shared reference inputs", "Identical Python and TypeScript scores and explanations", "Pass"],
             ["TC02", "Risk labels (test_risk_thresholds)", "0.35 / 0.36 / 0.65 / 0.66", "Low / Moderate / Moderate / High", "Pass"],
             ["TC03", "Rule risk (test_rule_risk_requires_enough_weight)", "Only 0.50 of the weight scored", "No risk score", "Pass"],
             ["TC04", "Pipeline (test_headline_only_is_unavailable_never_low_risk)", "Headline only, unknown publisher", "Risk and label NULL, status unavailable, flagged", "Pass"],
             ["TC05", "Pipeline (test_low_model_confidence_flags_verification)", "Fake model: LABEL_0 0.52, LABEL_1 0.48", "Flagged; reason cites classifier confidence", "Pass"],
             ["TC06", "Pipeline (test_disagreement_flags_verification)", "LABEL_1 0.98 for a reputable article", "Flagged; reason cites disagreement", "Pass"],
             ["TC07", "AI service (test_model_load_failure_returns_unavailable)", "Model loading raises an error", "Status unavailable; no score invented", "Pass"],
             ["TC08", "RSS fetcher (test_failed_feed_does_not_stop_the_run)", "Two feeds, one returns HTTP 500", "Other feed collected; failure listed", "Pass"],
             ["TC09", "Storage (test_stores_new_articles_and_skips_duplicates)", "Stored title; stored URL with tracking parameter", "1 inserted, 2 duplicates; label NULL", "Pass"],
             ["TC10", "Grouping (test_reports_far_apart_in_time_are_not_grouped)", "Same story 1 h and 40 h old", "Not grouped (gap > 36 h)", "Pass"],
             ["TC11", "API (test_analyze_validation)", "Empty text; 20,001 characters", "HTTP 422", "Pass"],
             ["TC12", "API (test_rate_limit)", "3 requests, limit 2", "200, 200, 429", "Pass"],
             ["TC13", "Frontend (NewsCard.test)", "Article without risk score", "\"not assessed\", no default label", "Pass"],
             ["TC14", "Live model (test_real_models_load_and_return_scores)", "RUN_MODEL_TESTS=1", "Real models return scores", "Skipped"]],
            [1.2, 5.1, 3.7, 4.5, 1.4], size=9),
        TAB("exec", "Test execution summary (25 November 2026)",
            ["Suite / check", "Command", "Observed result"],
            [["Backend tests", "python3 -m pytest -q", "63 passed, 3 skipped (opt-in)"],
             ["Frontend tests", "npx vitest run", "32 passed in 5 files"],
             ["Lint / type check", "npm run lint; npx tsc --noEmit -p .", "No errors"],
             ["Production build", "npm run build", "Compiled successfully; 13 routes"],
             ["End-to-end demonstration", "BBC and Al Jazeera items → pipeline → app", "41 articles shown, 5 multi-source events"],
             ["Real models / live services", "RUN_MODEL_TESTS=1, RUN_LIVE_TESTS=1", "Not executed"]],
            [4.4, 6.0, 5.5], size=10, first_bold=True),
        P("{tab:exec} records the observed results. No accuracy, precision, recall or F1 figures are reported, because "
          "the classifier was never run on real weights and no labelled dataset was evaluated; "
          "`backend/scripts/validate_models.py` only prints raw outputs on six hand-picked examples and is documented as "
          "\"not a benchmark\"."),
    ]

    # ════════════════════════════════ Chapter 6 ════════════════════════════════
    B += [
        H1("6", "Reports"),
        P("The system produces two reports: a PDF report for one article and an analytics dashboard for the edition."),
        P("**Article PDF report.** Two independent generators produce the same content: the server report "
          "(`backend/services/report_service.py`, ReportLab, streamed by GET /api/report/{id} and never stored) and the "
          "browser report (`frontend/src/lib/pdfReportGenerator.ts`, jsPDF), which works for every article including "
          "live items. Each contains a header with the generation time, the article metadata and link, the publisher "
          "excerpt and extractive summary, the credibility block (risk label and score, classifier fake score and "
          "confidence, verification flag, reasoning), the eight scores with scales and explanations, the analysis "
          "method and a disclaimer. Missing values are printed as \"Not available\", \"Not reported\" or \"n/a\". "
          "{fig:pdf} shows page 1 of a server report for the BBC article of Section 3.10, with status \"partial\" and "
          "method \"rules\"."),
        FIG("pdf", IMG / "out_report.jpg", "Server-generated PDF report, page 1 (rules-only analysis)", max_h=12),
        P("**Analytics dashboard.** The page /analytics, \"The News Intelligence Report\", shows four headline figures "
          "and seven charts: reports per section, risk labels, tone, average dimension scores, a 36-hour timeline, "
          "publishers, and publishers per event. Each average uses only articles in which the dimension was scored. For "
          "the demonstration edition ({fig:analytics}) it reports 41 reports, 5 multi-source events (10 reports "
          "grouped), 41 flagged for verification and an average Source Credibility of 89 (BBC 93, Al Jazeera 86). "
          "GET /api/analytics returns comparable statistics as JSON."),
        FIG("analytics", IMG / "out_analytics.jpg", "Analytics dashboard (41 reports, rules-only analysis)", width=14),
    ]

    # ════════════════════════════════ Chapter 7 ════════════════════════════════
    B += [
        H1("7", "Summary/Conclusion/Interpretation"),
        P("**Summary.** The project delivers a working news aggregator with transparent credibility and content "
          "analysis: scheduled collection and de-duplication; eight explained scores, a rule-based risk (combined with "
          "BERT-tiny when installed), sentiment and a verification flag; cross-source grouping; a REST API, dashboard, "
          "analytics and PDF reports. All automated tests that could run passed."),
        P("**Conclusion.** The main achievement is honest output: a risk score appears only when scored dimensions "
          "carry at least 65 % of the weight, unmeasurable dimensions stay empty, model scores are labelled uncalibrated, "
          "and unanalysed articles are no longer marked \"Low Risk\". The final audit fixed three defects (no source score "
          "for backend \"AlJazeera\" rows, a 60-character name limit against the database's 40, and rules-only rows "
          "labelled as model-analysed). The accurate status is **implemented and unit-tested, demonstrated in rules-only "
          "mode**: the models are integrated and tested with fake pipelines but were never run on real weights, so no "
          "accuracy is claimed. In the demonstration all 41 articles were flagged because RSS excerpts are shorter than "
          "150 characters, and all were Low Risk because both publishers are reputable and neutral in tone."),
        P("**Interpretation.** {tab:synvs} compares the synopsis with the implementation: plain software features were "
          "built and tested, while features that need a labelled dataset or a generative model were not."),
        TAB("synvs", "Synopsis versus implementation",
            ["Synopsis feature", "Status", "Implementation"],
            [["RSS collection, cleaning, 30-min schedule", "Fully", "11 feeds, 15 s timeout, overlap lock"],
             ["Remove duplicate / highly similar entries", "Partially", "Exact title/URL only; similar reports grouped"],
             ["BERT credibility risk with confidence", "Fully (not run)", "Mean of rule risk and fake score"],
             ["Sentiment positive / negative / neutral", "Partially", "Binary SST-2 model plus 41–59 neutral band"],
             ["Short AI-generated summaries", "Not implemented", "Extractive summary instead"],
             ["Calibrated confidence and its evaluation", "Not implemented", "Raw scores; uncertainty band and thresholds"],
             ["Eight dimensions; Needs Verification", "Fully", "Seven lexical rules; five flag conditions"],
             ["Cross-source comparison", "Partially", "TF-IDF groups; no framing analysis"],
             ["Supabase storage, search and filters", "Fully", "One articles table; user_profiles unused"],
             ["FastAPI incl. /categories, /sources", "Partially", "8 routes; no /categories or /sources"],
             ["Frontend data through FastAPI", "Different design", "Next.js reads Supabase directly"],
             ["Recharts analytics; PDF report", "Fully", "Analytics page; ReportLab and jsPDF reports"],
             ["Accuracy, precision, recall, F1", "Not implemented", "No labelled dataset; model test not executed"],
             ["Live fallback, external search, registration, RLS", "Extra", "Implemented and tested"]],
            [6.2, 3.2, 6.5], size=9.5),
    ]

    # ════════════════════════════════ Chapter 8 ════════════════════════════════
    B += [
        H1("8", "Limitations of System"),
        P("{tab:limits} lists the known limitations."),
        TAB("limits", "Limitations of the system",
            ["Area", "Limitation"],
            [["Short text", "Feeds supply a headline and one or two sentences; most articles are flagged, few receive a summary, and text-based dimensions describe the excerpt, not the article."],
             ["Models not verified", "BERT-tiny and DistilBERT were never run on real weights; the mapping LABEL_1 = fake is a configurable assumption."],
             ["No evaluation or calibration", "Scores are raw softmax outputs; no accuracy, precision, recall, F1 or calibration measure exists."],
             ["Lexicon rules", "Seven dimensions use word lists (e.g. \"won't\" matches the positive word \"won\"); a sensational text from an unknown site reached only Moderate risk (0.57) without the classifier."],
             ["Source table", "Fourteen hand-curated newsrooms; other publishers remain unscored."],
             ["Grouping and duplicates", "Text similarity may group different events on one topic or miss differently worded reports; only exact duplicates are removed."],
             ["Coverage and scale", "English only; fixed feed lists; in-memory rate limit per process; name-only registration; no load test."]],
            [3.6, 12.3], size=10.5, first_bold=True),
    ]

    # ════════════════════════════════ Chapter 9 ════════════════════════════════
    B += [
        H1("9", "Proposed Enhancements / Future Scope"),
        P("{tab:future} lists the proposed enhancements in order of priority."),
        TAB("future", "Proposed enhancements",
            ["Enhancement", "Purpose"],
            [["Install the models; run validate_models.py and the opt-in tests", "Obtain real model evidence and confirm the label mapping."],
             ["Evaluate on a labelled news dataset", "Report accuracy, precision, recall and F1 of the classifier and of the combined risk."],
             ["Calibrate the scores", "Apply temperature scaling and report the expected calibration error [7]."],
             ["Fetch full article text where permitted", "Improve every dimension and enable meaningful summaries."],
             ["Abstractive summaries", "Generate short summaries with a summarisation model, checked against the source."],
             ["Trained classifiers for bias, objectivity and propaganda", "Replace the word lists."],
             ["Sentence embeddings for grouping", "Reduce topic-level false matches and detect near-duplicates."],
             ["More sources, Indian languages, user accounts", "Wider coverage; saved topics through the existing user_profiles table and Supabase Auth."]],
            [6.6, 9.3], size=10.5, first_bold=True),
    ]

    # ════════════════════════════════ Chapter 10 ════════════════════════════════
    B += [
        H1("10", "Key Learnings from Project"),
        BL("**Full-stack design:** separating collection, analysis, storage, API and presentation, and assigning each "
           "data path to one server (FastAPI writes, Next.js reads Supabase directly).",
           "**Responsible use of NLP models:** pre-trained transformers are easy to call but their output must be "
           "interpreted carefully; a softmax score is not a probability of truth.",
           "**Explainable heuristics:** documented rules with an explanation per score are easier to defend and to "
           "criticise than one opaque number.",
           "**Missing data:** a missing value must remain missing; a \"Low Risk\" database default produced misleading "
           "output and had to be removed.",
           "**Testing with test doubles:** fake models, an in-memory database and mocked HTTP made both suites run "
           "offline in seconds; parity vectors kept Python and TypeScript identical.",
           "**Security and documentation:** Row Level Security, separate keys, CORS and rate limiting matter even in an "
           "academic project, and a report must describe what was built and state what was not.",
           "**Teamwork:** dividing work into modules with clear interfaces, reviewing code and integrating through "
           "version control."),
    ]

    # ════════════════════════════════ Chapter 11 ════════════════════════════════
    refs = [
        "J. Devlin, M.-W. Chang, K. Lee and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,\" in *Proc. NAACL-HLT*, 2019, pp. 4171–4186.",
        "V. Sanh, L. Debut, J. Chaumond and T. Wolf, \"DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter,\" arXiv:1910.01108, 2019.",
        "K. Shu, A. Sliva, S. Wang, J. Tang and H. Liu, \"Fake News Detection on Social Media: A Data Mining Perspective,\" *ACM SIGKDD Explorations Newsletter*, vol. 19, no. 1, pp. 22–36, 2017.",
        "R. Socher et al., \"Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank,\" in *Proc. EMNLP*, 2013, pp. 1631–1642.",
        "R. Flesch, \"A New Readability Yardstick,\" *Journal of Applied Psychology*, vol. 32, no. 3, pp. 221–233, 1948.",
        "G. Salton and C. Buckley, \"Term-weighting approaches in automatic text retrieval,\" *Information Processing & Management*, vol. 24, no. 5, pp. 513–523, 1988.",
        "C. Guo, G. Pleiss, Y. Sun and K. Q. Weinberger, \"On Calibration of Modern Neural Networks,\" in *Proc. ICML*, 2017, pp. 1321–1330.",
        "T. Wolf et al., \"Transformers: State-of-the-Art Natural Language Processing,\" in *Proc. EMNLP: System Demonstrations*, 2020, pp. 38–45.",
        "M. Romero, \"bert-tiny-finetuned-fake-news-detection,\" Hugging Face model card. [Online]. Available: https://huggingface.co/mrm8488/bert-tiny-finetuned-fake-news-detection",
        "Hugging Face, \"distilbert-base-uncased-finetuned-sst-2-english,\" model card. [Online]. Available: https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english",
        "FastAPI documentation. [Online]. Available: https://fastapi.tiangolo.com/",
        "Supabase documentation (PostgreSQL, Row Level Security). [Online]. Available: https://supabase.com/docs",
        "Next.js documentation. [Online]. Available: https://nextjs.org/docs",
        "React documentation. [Online]. Available: https://react.dev/",
        "Recharts documentation. [Online]. Available: https://recharts.org/",
        "APScheduler documentation. [Online]. Available: https://apscheduler.readthedocs.io/",
        "feedparser documentation. [Online]. Available: https://feedparser.readthedocs.io/",
        "ReportLab User Guide. [Online]. Available: https://docs.reportlab.com/",
        "jsPDF documentation. [Online]. Available: https://github.com/parallax/jsPDF",
        "pytest documentation. [Online]. Available: https://docs.pytest.org/",
        "Vitest documentation. [Online]. Available: https://vitest.dev/",
        "The GDELT Project, \"GDELT DOC 2.0 API.\" [Online]. Available: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/",
        "RSS Advisory Board, \"RSS 2.0 Specification.\" [Online]. Available: https://www.rssboard.org/rss-specification",
    ]
    B += [H1("11", "Bibliography")]
    B += [("ref", f"[{i + 1}]\t{r}") for i, r in enumerate(refs)]
    return B


# ─── numbering, captions and rendering ──────────────────────────────────────────────────────

def numbered():
    """Assign numbers per chapter. Returns (blocks, refs) where refs maps 'fig:key' -> '3.1'."""
    bl = blocks()
    refs = {}
    chap = None
    counters = {}
    for b in bl:
        if b[0] == "h1":
            chap = b[1]
            counters = {"fig": 0, "tab": 0, "lst": 0}
        kind = {"table": "tab", "fig": "fig", "code": "lst"}.get(b[0])
        if kind:
            counters[kind] += 1
            refs[f"{kind}:{b[1]}"] = f"{chap}.{counters[kind]}"
    return bl, refs


def resolve(text, refs):
    def rep(m):
        kind, key = m.group(1), m.group(2)
        word = {"fig": "Figure", "tab": "Table", "lst": "Listing"}[kind]
        return f"{word} {refs[kind + ':' + key]}"
    return re.sub(r"\{(fig|tab|lst):([a-z0-9_]+)\}", rep, text)


def collect_captions():
    bl, refs = numbered()
    figs = [(refs[f"fig:{b[1]}"], b[3]) for b in bl if b[0] == "fig"]
    tabs = [(refs[f"tab:{b[1]}"], b[2]) for b in bl if b[0] == "table"]
    return figs, tabs


def write_chapters(B):
    bl, refs = numbered()
    first = True
    for n, b in enumerate(bl):
        k = b[0]
        last = n + 1 == len(bl) or bl[n + 1][0] == "h1"
        if k == "h1":
            h = B.heading(1, b[1], b[2])
            if first:
                h.paragraph_format.page_break_before = False
                first = False
        elif k == "h2":
            B.heading(2, b[1], b[2])
        elif k == "h3":
            B.heading(3, None, b[2])
        elif k == "p":
            B.p(resolve(b[1], refs))
        elif k == "bullets":
            B.bullets([resolve(x, refs) for x in b[1]])
        elif k == "table":
            _, key, cap, header, rows, widths, size, fb = b
            B.table(refs[f"tab:{key}"], cap, header, [[resolve(c, refs) for c in r] for r in rows], widths, size, fb,
                    gap=not last)
        elif k == "fig":
            _, key, path, cap, width, max_h, own_page = b
            B.figure(refs[f"fig:{key}"], path, cap, width, max_h, own_page=own_page)
        elif k == "code":
            _, key, cap, text, size = b
            B.code(refs[f"lst:{key}"], cap, text, size, gap=not last)
        elif k == "ref":
            B.p(b[1], style="Reference")
