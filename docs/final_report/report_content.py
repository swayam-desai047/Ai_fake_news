"""Chapter text of the final report. Every number below comes from the code (file named next to it)
or from the test runs of 25 Nov 2026. Figures, tables and listings are numbered per chapter;
{fig:key}, {tab:key} and {lst:key} in the text are replaced by "Figure 3.1", "Table 1.2", ...
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNG = Path(__file__).resolve().parent / "png"
IMG = ROOT / "docs" / "report" / "img"


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
def FIG(key, path, caption, width=None, max_h=19.5): return ("fig", key, path, caption, width, max_h)
def CODE(key, caption, text, size=8.5): return ("code", key, caption, text, size)
def BR(): return ("break",)


def analyze_example_text():
    ex = json.loads((ROOT / "docs" / "report" / "analyze_example.json").read_text())
    req = json.dumps(ex["request"], indent=2, ensure_ascii=False)
    r = ex["response"]
    keep = {k: r[k] for k in ("risk_score", "credibility_label", "needs_verification", "confidence_level",
                              "model_fake_probability", "analysis_status", "analysis_method", "model_version")}
    dims = {k: v for k, v in r["dimensions"].items() if k != "explanations"}
    resp = json.dumps(keep, indent=2) + "\n" + '"dimensions": ' + json.dumps(dims) + "\n" + \
        '"ai_reasoning": ' + json.dumps(r["ai_reasoning"])
    # wrap long lines for the code box
    out = []
    for line in ("POST /api/analyze\n" + req + "\n\nResponse (abridged):\n" + resp).split("\n"):
        while len(line) > 100:
            cut = line.rfind(" ", 0, 100)
            cut = cut if cut > 20 else 100
            out.append(line[:cut])
            line = "    " + line[cut:].lstrip()
        out.append(line)
    return "\n".join(out)


def blocks():
    rr1, a1 = C("backend/services/dimension_service.py", "MIN_EVIDENCE_CHARS = 150", "UNCERTAINTY_BAND = (0.4, 0.6)")
    rr2, a2 = C("backend/services/dimension_service.py", "def rule_risk(dims", "return round2(1 - composite), weight")
    rule_risk = rr1 + "\n...\n" + rr2
    rule_src = a1 + " and " + a2.split(", ")[1]
    pipe, pipe_src = C("backend/services/analysis_pipeline.py", "rule_score, _ = rule_risk(dims)", "needs_verification = bool(flags)")
    clf, clf_src = C("backend/services/ai_service.py", 'fake = scores.get(FAKE_LABEL, scores.get("FAKE"))', 16)
    clu, clu_src = C("backend/services/clustering_service.py", "assigned: set = set()", '"similarity": round(min(sims), 3) if sims else None,')
    rss, rss_src = C("backend/services/rss_fetcher.py", "def parse_feed(", "return out")
    api, api_src = C("backend/api/router.py", '@api_router.get("/report/{article_id}")', 15)
    repo, repo_src = C("frontend/src/lib/repository.ts", "async function loadDatabaseArticles()", 17)
    repo2, repo2_src = C("frontend/src/components/analysis/ReportDownload.tsx", "const serverReport = backendUrl", ": null;")
    sc, sc_src = C("frontend/src/lib/scoring.ts", "const { score, availableWeight } = ruleRisk(dimensions);", "const needsVerification = score === null || ambiguous || thin;")

    B = []
    # ════════════════════════════════ Chapter 1 ════════════════════════════════
    B += [
        H1("1", "Introduction"),
        P("News is now read mostly online. Every day many publishers post hundreds of reports, and the same event "
          "appears under different headlines with different wording and detail. A reader who wants a quick and balanced "
          "picture has to open several websites, and it is not easy to see which reports use emotional or one-sided "
          "language, which headlines are not supported by the text, and which stories come from established newsrooms."),
        P("This project, **AI-Powered News Aggregator with Advanced Credibility and Content Analysis**, is a web "
          "application that collects news from selected RSS feeds, removes exact duplicates, analyses each article with "
          "transparent rules and (when installed) two transformer models, groups reports of the same event from "
          "different publishers, and presents the results in a newspaper-style dashboard called *The Daily Signal*. "
          "For each article the system shows a credibility-risk indicator, a sentiment label, eight content-analysis "
          "scores with plain-language explanations, a Needs Verification flag, an extractive summary when the text is "
          "long enough, the other publishers that reported the same event, and a downloadable PDF report."),
        P("The system does not decide whether an article is true or false. Its outputs are indicators that help a "
          "reader decide which reports deserve a closer look, and the link to the original publisher is always kept. "
          "This report describes the system exactly as it is implemented in the project repository; where the "
          "implementation differs from the synopsis, the difference is stated (see Section 7.3)."),

        H2("1.1", "Existing System"),
        P("Before this project, a reader typically used one of three kinds of service, each with a gap:"),
        BL("**Publisher websites and apps** show one newsroom only. Comparing how an event is covered requires visiting "
           "several sites and reading each report separately.",
           "**General news aggregators** collect headlines from many sources, but they give no explanation of tone, "
           "balance, sensational framing or how well a headline is supported by the text.",
           "**Fact-checking websites** examine individual claims manually. They are reliable, but they cover a small "
           "number of viral stories and cannot keep up with the daily flow of news."),
        P("Research on automatic fake-news detection usually trains a classifier on labelled articles and outputs a "
          "single label [3]. Such a label is difficult for a reader to interpret: it does not say *why* an article looks "
          "risky, and it gives no indication of how much text the decision was based on. The first version of this "
          "project's own code had similar problems, found during the analysis phase: articles were stored without the "
          "eight dimension scores, a database default labelled every stored article \"Low Risk\" even when no risk had "
          "been computed, and the public database key could insert and update articles. These problems were corrected "
          "in the implemented version (see Section 7.2)."),

        H2("1.2", "Need for System"),
        P("The system is needed for the following reasons:"),
        BL("To reduce the time spent visiting several sources for the same event, by collecting articles automatically "
           "and showing related reports together.",
           "To remove repeated entries of the same report from the news feed.",
           "To replace a single unexplained number with several explained indicators: a risk score with its reasoning, "
           "eight dimension scores, each with a one-line explanation, and a separate verification flag.",
           "To show clearly when the available text is too short to support a judgement, instead of displaying an "
           "invented or default score.",
           "To keep the original publisher link so that every indicator can be checked against the full article."),

        H2("1.3", "Scope of System"),
        P("**In scope.** English-language news from public RSS feeds: the backend collects 11 feeds in five categories "
          "(BBC, CNN, Yahoo and Al Jazeera; `backend/services/rss_fetcher.py`). When the database is not configured or "
          "is empty, the frontend reads 31 feed URLs of its own in eight sections (Google News topic feeds, BBC, The "
          "Guardian, Al Jazeera, The Hindu, NDTV, The Indian Express, Mint, TechCrunch; `frontend/src/lib/sections.ts`). "
          "A search with few local matches can also query Google News RSS, GNews or the GDELT DOC 2.0 API "
          "(`frontend/src/lib/externalSearch.ts`). The system analyses the text that the feed supplies (headline and "
          "short description), collects news every 30 minutes, scores risk, sentiment and eight dimensions, writes "
          "extractive summaries, groups related reports, supports search and filters, shows analytics charts, produces "
          "PDF reports and offers a REST API."),
        P("**Out of scope.** Verifying the facts of a claim; downloading full article bodies from publisher websites; "
          "languages other than English; user accounts with passwords (only a display name is stored); training or "
          "fine-tuning machine-learning models; and measuring model accuracy (no labelled dataset was used)."),

        H2("1.4", "Operating Environment - Hardware and Software"),
        P("The repository does not state a hardware requirement, so {tab:hw} gives a recommended configuration based on "
          "the components used. It is an assumption, not a measurement: the transformer models were not executed in "
          "the development environment. {tab:sw} lists the software needed to run the system; the version numbers are "
          "the minimum versions declared in `backend/requirements.txt` and `frontend/package.json`."),
        TAB("hw", "Hardware requirements (recommended; not measured)",
            ["Component", "Minimum", "Recommended"],
            [["Processor", "Dual-core 64-bit CPU", "Quad-core 64-bit CPU"],
             ["RAM", "4 GB (rules-only mode)", "8 GB (both models, API and frontend on one machine)"],
             ["Storage", "2 GB free (packages)", "5 GB free (packages and model files)"],
             ["Network", "Internet access to the RSS feeds and Supabase", "Also Hugging Face Hub for the first model download"],
             ["Client device", "Any device with a modern web browser", "Desktop or mobile browser (responsive layout)"]],
            [3.2, 5.6, 7.1], first_bold=True),
        TAB("sw", "Software requirements",
            ["Software", "Version", "Purpose in this project"],
            [["Operating system", "Windows 10/11, Linux or macOS", "Development and hosting"],
             ["Python", "3.10 or later (Dockerfile: python:3.10-slim)", "Backend, analysis pipeline, scheduler"],
             ["Node.js", "20 or later (required by Next.js 16)", "Next.js frontend server"],
             ["Supabase (PostgreSQL)", "Hosted cloud project", "Database with Row Level Security"],
             ["Web browser", "Current Chrome, Edge or Firefox", "User interface"],
             ["Docker (optional)", "Any current version", "Container image of the backend (port 7860)"]],
            [3.6, 5.4, 6.9], first_bold=True),
        P("The tests reported in Chapter 5 were run with Python 3.13.18 and Node.js 22.23.5."),

        H2("1.5", "Brief Description of Technology Used"),
        P("{tab:tech} lists every technology used and explains its role in this project. The backend is written in "
          "Python and the frontend in TypeScript; the two share one scoring method, implemented twice and checked by "
          "common test vectors (`shared/scoring_vectors.json`)."),
        TAB("tech", "Technology stack and the role of each technology in this project",
            ["Technology (version)", "Role in this project"],
            [["Python, FastAPI >=0.110, Uvicorn >=0.28, Pydantic >=2.6", "REST API (`backend/main.py`, `backend/api/router.py`): eight endpoints under /api and /api/v1, request validation, CORS allow-list, rate limit, error handling."],
             ["feedparser >=6.0, httpx >=0.27, BeautifulSoup4 >=4.12", "Download each RSS feed with a 15 s timeout, parse the entries and strip HTML from titles and excerpts (`rss_fetcher.py`)."],
             ["APScheduler >=3.11", "Runs the collect-analyse-store-group job every 30 minutes without overlapping runs (`scheduler.py`)."],
             ["Hugging Face Transformers >=4.38, PyTorch >=2.2", "Loads, on first use, `mrm8488/bert-tiny-finetuned-fake-news-detection` (fake-class score) and `distilbert-base-uncased-finetuned-sst-2-english` (sentiment) in `ai_service.py`. Optional: without them the pipeline runs in rules-only mode."],
             ["Supabase (PostgreSQL), supabase-py >=2.3, supabase-js ^2.97", "Stores articles (JSONB dimensions) and reader names; Row Level Security makes articles read-only for the public key. The backend writes with the service-role key; the frontend reads with the anon key."],
             ["ReportLab >=4.1", "Builds the A4 server-side PDF report (`report_service.py`, GET /api/report/{id})."],
             ["Next.js 16.1.6, React 19.2.3, TypeScript ^5", "Server-rendered pages (front page, sections, article, search, compare, analytics) and six Next.js API routes; `repository.ts` is the single data-access module."],
             ["Tailwind CSS ^4", "Responsive newspaper-style layout of The Daily Signal."],
             ["Recharts ^3.7", "Eight-dimension radar chart and the analytics bar and timeline charts."],
             ["jsPDF ^4.2", "PDF report generated in the browser for any article (`pdfReportGenerator.ts`)."],
             ["pytest >=8.2, Vitest ^4.0, Testing Library, jsdom", "Automated backend (66 tests, 3 of them opt-in) and frontend (32 tests) test suites."],
             ["Docker (python:3.10-slim)", "Optional container image of the backend listening on port 7860 (`backend/Dockerfile`)."]],
            [5.4, 10.5]),
        P("**How the NLP parts work.** A transformer model reads the headline and excerpt as tokens and outputs a score "
          "for each label of its classification head. BERT-tiny is a very small BERT model [1] fine-tuned for fake-news "
          "detection; its fake-class softmax score is used as one input to the risk score. DistilBERT [2] fine-tuned on "
          "the binary SST-2 sentiment dataset [4] gives a positive-class score, which the project maps to a 0–100 "
          "sentiment score with a neutral band. Readability uses the Flesch Reading Ease formula [5]. Event grouping "
          "uses TF-IDF term weighting and cosine similarity [6]. All these outputs are raw scores; none of them has been "
          "calibrated (Section 8)."),
    ]

    # ════════════════════════════════ Chapter 2 ════════════════════════════════
    B += [
        H1("2", "Proposed System"),
        P("The proposed system turns a stream of RSS entries into analysed, grouped and searchable articles. Its main "
          "idea is to give several small, explained indicators instead of one verdict, and to say clearly when the "
          "available text is not enough to judge. It consists of an automated backend pipeline (FastAPI, scheduler, "
          "analysis services), a Supabase PostgreSQL database and a Next.js web application."),
        H2("2.1", "Feasibility Study"),
        P("{tab:feas} summarises the feasibility study. The wording reflects what was actually verified: the software was "
          "built and its automated tests passed, but the transformer models were not executed during development."),
        TAB("feas", "Feasibility study",
            ["Aspect", "Assessment"],
            [["Technical", "All components are mature open-source libraries. The two models are small (BERT-tiny and DistilBERT) and are expected to run on a CPU, but this was not measured: the models were not installed in the development environment. Every other part was built and tested. Supabase provides a hosted PostgreSQL database, so no database server has to be maintained."],
             ["Economic", "All libraries are free and open source. Supabase, the Hugging Face models and the RSS feeds are available at no cost for a project of this size. The only cost is development time."],
             ["Operational", "The reader needs no training: the interface looks like a newspaper and every score has a short explanation. Collection runs automatically every 30 minutes. A failing feed, model or database call is logged and the rest of the system continues."],
             ["Schedule", "The work was divided into stages (requirements, collection, cleaning, models, sentiment, summary, risk interpretation, grouping, eight dimensions, database and API, reports and analytics, testing and documentation), which fitted the semester."]],
            [3.0, 12.9], first_bold=True),
        H2("2.2", "Objectives of Proposed System"),
        P("The synopsis listed thirteen objectives. {tab:obj} shows each objective as planned, what was delivered, and "
          "the remaining gap. Eight objectives are met (two of them by a different method or without verification on "
          "real model weights), three are partly met, and two, AI-generated summaries and model evaluation, are not met."),
        TAB("obj", "Objectives: planned, delivered and gap",
            ["Planned objective (synopsis)", "Delivered", "Gap"],
            [["Collect recent articles from multiple RSS sources", "11 backend feeds every 30 min; 31-URL live fallback in the frontend", "None"],
             ["Clean, normalise and preprocess articles", "HTML stripped, URLs and titles normalised, ISO-8601 UTC dates", "None"],
             ["Identify and reduce duplicate or highly similar entries", "Exact duplicates removed by normalised title and URL; similar reports are grouped", "Near-duplicates are grouped, not removed"],
             ["Transformer credibility-risk classification with confidence", "BERT-tiny fake-class score averaged with a rule-based risk; confidence = max(p, 1 − p)", "Wired in and unit-tested with fake pipelines; not run on real weights"],
             ["Improve interpretation and calibration of confidence", "Scores labelled raw/uncalibrated; 0.40–0.60 band, confidence < 0.60 and disagreement checks", "No calibration performed"],
             ["Sentiment Positive / Negative / Neutral", "DistilBERT SST-2 (binary) mapped to 0–100; 41–59 read as neutral; word-list fallback", "Neutral is a band, not a model class"],
             ["Concise AI-generated summaries", "Extractive summary (two sentences selected by word frequency) when the excerpt has ≥ 3 sentences", "No abstractive (AI-generated) summary"],
             ["Compare articles on the same event, show coverage and framing", "TF-IDF grouping and the /compare page with per-publisher columns", "No automatic framing analysis"],
             ["Eight-dimension analysis", "All eight dimensions with explanations, mirrored in Python and TypeScript", "Seven of eight are lexical rules"],
             ["Needs Verification indication", "Raised by five conditions (Section 3.1)", "None"],
             ["Store in Supabase and provide search and filtering", "articles table, search and six filters", "None"],
             ["Visual analytics and downloadable PDF report", "Analytics page with seven charts; server and browser PDF", "None"],
             ["Evaluate with classification, calibration and quality measures", "Software tests only (Chapter 5)", "No accuracy, precision, recall, F1 or calibration figures"]],
            [5.0, 6.2, 4.7], size=10),
        H2("2.3", "Users of System"),
        P("The system has the three kinds of user listed in {tab:users}. The Scheduler is not a person but is treated as "
          "an actor because it starts the ingestion use case on its own."),
        TAB("users", "Users of the system",
            ["User", "Description", "What the user can do"],
            [["Reader", "Any visitor of The Daily Signal (no password; display name only)", "Register a display name, read the front page and sections, search and filter, open the article analysis, compare coverage, view analytics, download PDF reports"],
             ["Operator / API client", "Developer or administrator using the REST API (Swagger at /docs, curl)", "Analyse any text with POST /api/analyze, read articles, groups and analytics, trigger ingestion with POST /api/ingest when an ingest token is configured"],
             ["Scheduler (system actor)", "APScheduler job inside the FastAPI process", "Collect, de-duplicate, analyse, store and group articles every 30 minutes"]],
            [3.4, 5.4, 7.1], first_bold=True),
    ]

    # ════════════════════════════════ Chapter 3 ════════════════════════════════
    B += [
        H1("3", "Analysis and Design"),
        P("This chapter gives the requirements, the eight design diagrams required by the college format, additional "
          "data-flow, workflow and entity-relationship diagrams, the database schema, the REST interfaces, and sample "
          "input and output screens. All diagrams were drawn from the implemented code, not from the synopsis."),
        H2("3.1", "System Requirements (Functional and Non-Functional requirements)"),
        H3("Functional requirements"),
        TAB("fr", "Functional requirements",
            ["No.", "Requirement", "Implemented in"],
            [["FR1", "Collect title, publisher, URL, category, excerpt and time from the RSS feeds every 30 minutes.", "rss_fetcher.py, scheduler.py"],
             ["FR2", "Clean HTML and skip duplicates by normalised title and URL, within a batch and against the database.", "rss_fetcher.py, db_service.py"],
             ["FR3", "Score eight dimensions, each with an explanation; leave a dimension unscored when it cannot be measured.", "dimension_service.py, scoring.ts"],
             ["FR4", "Run the fake-news classifier and the sentiment model when available; report \"unavailable\" otherwise.", "ai_service.py"],
             ["FR5", "Compute a risk score and a label (Low / Moderate / High, or not assessed) and a Needs Verification flag.", "analysis_pipeline.py"],
             ["FR6", "Group reports of the same event from at least two publishers.", "clustering_service.py, clustering.ts"],
             ["FR7", "Search by keywords and filter by section, publisher, risk, verification flag and date.", "search/page.tsx, repository.ts, search.ts"],
             ["FR8", "Show the article page with credibility panel, radar chart and dimension table.", "article/[id]/page.tsx"],
             ["FR9", "Show analytics: sections, risk labels, tone, dimension averages, timeline, publishers, coverage.", "analytics/page.tsx"],
             ["FR10", "Download a PDF report of an article.", "report_service.py, pdfReportGenerator.ts"],
             ["FR11", "Register a reader display name (1–40 characters).", "NameAuthModal.tsx, api/auth/profile/route.ts"],
             ["FR12", "Analyse custom text through the API without storing it.", "router.py (POST /analyze)"]],
            [1.4, 10.0, 4.5]),
        H3("Non-functional requirements"),
        TAB("nfr", "Non-functional requirements",
            ["Requirement", "How it is met"],
            [["Usability", "Newspaper layout, plain-language explanations, responsive design for mobile screens."],
             ["Reliability", "Feed timeouts (15 s backend, 8 s frontend); a failed feed, model or database call is logged and the run continues; a lock prevents overlapping scheduler runs."],
             ["Transparency", "Every score has an explanation; model scores are labelled raw and uncalibrated; missing values are shown as \"n/a\", \"Not available\" or \"Not reported\", never as defaults."],
             ["Security", "The public key can only read articles (RLS); the service-role key stays on the server; CORS allow-list; input validation; rate limit of 30 requests per minute per client on /analyze and /report; internal errors are not shown."],
             ["Maintainability", "Separate modules for collection, analysis, storage, API and UI; one scoring method mirrored in Python and TypeScript and checked by shared test vectors; idempotent SQL migrations."],
             ["Performance", "Models load lazily, once; the frontend caches the 500-row edition for 60 seconds and live feeds for 2 minutes. No load test was carried out."]],
            [3.2, 12.7], first_bold=True),
        P("The risk score and the verification flag are central to the system. The rule-based risk is the inverse of a "
          "weighted average of five dimensions ({tab:risk}). Only dimensions that could be scored are used; if they carry "
          "less than 65% of the weight, no risk score is given. When the classifier runs, the final risk is the mean of "
          "the rule-based risk and the classifier's fake-class score. These values are heuristics, not calibrated "
          "probabilities."),
        TAB("risk", "Risk weights, label thresholds and Needs Verification conditions",
            ["Item", "Value (source: dimension_service.py, analysis_pipeline.py)"],
            [["Rule weights", "Source Credibility 0.35; Propaganda 0.20; Objectivity 0.15; Bias 0.15; Headline Accuracy 0.15"],
             ["Rule-based risk", "1 − Σ(score × weight) / Σ(weight) / 100, over the scored dimensions; none if Σ(weight) < 0.65"],
             ["Final risk", "mean(rule risk, classifier fake score) when the classifier ran; otherwise the rule risk alone"],
             ["Labels", "Low Risk ≤ 0.35; Moderate Risk ≤ 0.65; High Risk > 0.65; no score = not assessed"],
             ["Needs Verification", "Any of: no risk score; score within 0.40–0.60; fewer than 150 characters of publisher text; classifier confidence < 0.60; |classifier score − rule risk| ≥ 0.50"],
             ["Analysis status", "complete (both models ran), partial (rules only or one model), unavailable (no score)"]],
            [3.5, 12.4], first_bold=True),
        P("{tab:dims} lists the eight dimensions. All are scored from 0 to 100 from the headline and the feed excerpt; "
          "the formulas are identical in `dimension_service.py` and `scoring.ts`."),
        TAB("dims", "The eight content dimensions",
            ["Dimension", "How it is measured (0–100)", "Left unscored when"],
            [["Sentiment", "50 + 9 × (positive − negative cue words), limited to 5–95; replaced by DistilBERT positive score × 100 when the model ran. ≥ 60 positive, ≤ 40 negative, 41–59 neutral", "never"],
             ["Bias", "90 − 15 per loaded term, − 6 if a body has no attribution word (\"said\", \"according to\", ...); minimum 20", "never"],
             ["Objectivity", "92 − 14 per evaluative adjective (\"terrible\", \"amazing\", ...); minimum 20", "never"],
             ["Readability", "Flesch Reading Ease of headline and excerpt", "headline only"],
             ["Propaganda / Manipulation", "95 − 22 per clickbait pattern (11 patterns, e.g. \"shocking\", \"!!\") − 10 per shouted word in the headline; minimum 5", "never"],
             ["Headline Accuracy", "45 + 50 × share of headline key terms found in the excerpt", "no excerpt"],
             ["Source Credibility", "Hand-curated table of 14 newsrooms (e.g. Reuters 95, BBC 93, Al Jazeera 86, Yahoo 78)", "publisher not in table"],
             ["Content Quality", "35 + min(characters, 600)/12 + 5 × min(sentences, 4)", "no excerpt"]],
            [3.3, 9.7, 2.9], size=10, first_bold=True),

        H2("3.2", "Module Hierarchy Diagram"),
        P("{fig:modules} shows how the source code is organised. The backend has six module groups and the frontend "
          "seven; the shared parity vectors connect the Python and TypeScript scoring code. {tab:modules} describes the "
          "responsibility of each group."),
        FIG("modules", PNG / "modules.png", "Module hierarchy of the implemented system (backend/, frontend/src/, shared/)", max_h=18.5),
        TAB("modules", "Module descriptions",
            ["Module group", "Responsibility", "Source files"],
            [["Collection", "Download each feed (15 s timeout, at most 8 entries per feed), strip HTML, convert dates to UTC, drop repeats; run the job every 30 minutes with a lock against overlapping runs.", "rss_fetcher.py, scheduler.py"],
             ["Analysis", "Score the eight dimensions and the rule-based risk; load and run the two models; combine them into risk, label, verification flag, summary and status.", "dimension_service.py, ai_service.py, analysis_pipeline.py"],
             ["Grouping", "TF-IDF cosine similarity of headline (counted twice) and lead sentence; threshold 0.32, 48-hour window, members within 36 hours of the seed, at least two publishers.", "clustering_service.py, clustering.ts"],
             ["Storage", "Skip stored articles before analysis, insert rows, update groups; SQL scripts create tables, constraints and policies.", "db_service.py, db/supabase.py, db/*.sql"],
             ["API & Reports", "REST endpoints with validation; CORS, rate limit and error handling; PDF generation.", "main.py, api/router.py, report_service.py"],
             ["Scripts", "Re-analyse legacy rows; print raw model outputs on six hand-picked examples (\"not a benchmark\").", "reanalyze.py, validate_models.py"],
             ["Frontend data access", "Load the edition (500 rows, 60 s cache) or live feeds; search with accent folding, aliases and ranking; parse query strings.", "repository.ts, supabase.ts, search.ts, query.ts"],
             ["Live & external news", "Live RSS fallback (31 URLs, 8 sections) and external search (Google News RSS, GNews, GDELT).", "liveNewsService.ts, sections.ts, externalSearch.ts"],
             ["Frontend scoring & reports", "Same rules as the backend for live items; TF-IDF grouping; browser PDF.", "scoring.ts, clustering.ts, pdfReportGenerator.ts"],
             ["Pages, API routes, components", "Server-rendered pages, six Next.js API routes and React components (NameAuthModal, NewsCard, DimensionRadarChart, CrossSourceView, ...).", "app/, components/"]],
            [3.2, 8.4, 4.3], size=10, first_bold=True),

        H2("3.3", "Architecture Diagram"),
        P("{fig:arch} shows the architecture as built. There are two independent paths. The **ingestion path** runs "
          "inside the FastAPI process: the scheduler fetches the publisher feeds, the analysis pipeline scores each new "
          "article, and `db_service.py` writes it to Supabase with the service-role key. The **read path** does not "
          "use FastAPI: the Next.js server reads Supabase directly with the read-only anon key (`repository.ts`, 500 "
          "newest rows, 60-second cache) and renders the pages. FastAPI is contacted by the browser only for the "
          "optional server-side PDF, and only when `NEXT_PUBLIC_API_URL` is set. When the database is empty or not "
          "configured, Next.js falls back to live publisher feeds scored with the same rules in TypeScript, and a search "
          "with few local matches can query external news services."),
        FIG("arch", PNG / "architecture.png", "Architecture diagram: ingestion through FastAPI, reading directly from Supabase", max_h=17),
        P("The REST interfaces of both servers are listed in {tab:api} and {tab:nextapi}. Each FastAPI route is mounted "
          "twice, under `/api` and `/api/v1`. The Next.js API routes are a separate server with different response "
          "shapes; some have the same paths."),
        TAB("api", "FastAPI endpoints (backend/api/router.py; each under /api and /api/v1)",
            ["Method", "Path", "Input", "Output"],
            [["GET", "/health", "–", "Status, database configured, model state, last ingestion run"],
             ["POST", "/analyze", "text (1–20,000 chars), title (≤ 500), publisher (≤ 120)", "Full analysis, not stored; 422 on invalid input; rate-limited"],
             ["GET", "/articles", "limit 1–200, offset, category, risk, q (≤ 120), needs_verification", "Article list, newest first; 503 on database error"],
             ["GET", "/article/{id}", "UUID", "One article; 404 if not found; 422 for a non-UUID"],
             ["GET", "/groups", "–", "Groups covered by ≥ 2 publishers, with per-publisher coverage"],
             ["GET", "/analytics", "limit 1–2000 (default 500)", "Counts by category, sentiment, risk, status; dimension averages"],
             ["GET", "/report/{id}", "UUID", "application/pdf attachment; 404; rate-limited"],
             ["POST", "/ingest", "X-Ingest-Token header", "Run summary; 404 unless INGEST_TOKEN is set; 403 for a wrong token"]],
            [1.5, 2.6, 5.9, 5.9], size=10),
        TAB("nextapi", "Next.js API routes (frontend/src/app/api/)",
            ["Method", "Path", "Input", "Output"],
            [["GET", "/api/articles", "q, section, publisher, risk, verify, sort, since, page, limit (1–100)", "Page of articles plus search information"],
             ["GET", "/api/article/[id]", "article id", "{article}; 404 if not in the current edition"],
             ["GET", "/api/groups", "–", "Cross-source groups of the edition"],
             ["GET", "/api/analytics", "–", "Analytics summary of the edition"],
             ["GET", "/api/search/external", "q (≤ 120), since", "External results; 400 if q is empty, 502 if unavailable"],
             ["POST", "/api/auth/profile", "{name}", "Visitor record in named_visitors; 400 if the name is empty"]],
            [1.5, 3.6, 5.6, 5.2], size=10),
        H3("Data Flow Diagrams"),
        P("The context diagram ({fig:dfd0}) shows the system as a single process with its external entities: the "
          "publisher feeds supply RSS entries, the Hugging Face Hub supplies model weights on first use, the external "
          "news services answer searches, and the reader sends a name, queries and filters and receives pages, "
          "analysis and PDF reports."),
        FIG("dfd0", PNG / "dfd0.png", "Data flow diagram, Level 0 (context diagram)", max_h=12),
        P("The Level 1 diagram ({fig:dfd1}) opens the process into eight sub-processes and two data stores. Processes "
          "1.0 to 5.0 form the ingestion path (backend); processes 6.0 to 8.0 serve the reader. Duplicate removal reads "
          "the titles and URLs already in D1 before an article is analysed, and grouping (4.0) reads recent rows and "
          "writes their group_id back."),
        FIG("dfd1", PNG / "dfd1.png", "Data flow diagram, Level 1", max_h=18),
        H3("Application Workflow"),
        P("{fig:workflow} shows the workflow of a reader. On the first visit the reader registers a display name; the "
          "name is kept in the browser (`localStorage`) so the modal is not shown again. The front page is built from "
          "the current edition, and the reader can then browse a section, search, compare coverage or view analytics. "
          "Section, search and compare pages lead to the article page, where the PDF report can be downloaded."),
        FIG("workflow", PNG / "workflow.png", "Application workflow of a reader", max_h=18.5),

        H2("3.4", "Class Diagram"),
        P("The class diagram ({fig:class}) shows the core data of the system. Each Article belongs to one source and "
          "has exactly one CredibilityResult, one SentimentResult and one DimensionAnalysis; it may have a Summary and "
          "may belong to an ArticleGroup (a group has at least two articles). The backend is written in a functional "
          "style, so the operations shown with «function» are module-level Python functions, not methods; Source is "
          "conceptual (the `RSS_SOURCES` dictionary and the `source_domain` column). Multiplicity [0..1] on an attribute "
          "means the value may be missing (\"not measured\"), never zero."),
        FIG("class", PNG / "class.png", "Class diagram of the core data (operations are module-level functions)", max_h=16),
        H3("Data model: entity relationship diagram and database schema"),
        P("In the database all article data is stored in a single `articles` table, with the eight scores and their "
          "explanations in one JSONB column. {fig:erd} shows the three tables created by "
          "`backend/db/supabase_complete_setup.sql`. The `articles` table has no foreign key; related reports share a "
          "`group_id` value (a logical group). `named_visitors` stores reader display names. `user_profiles` references "
          "Supabase's `auth.users` table one-to-one; it is defined in the SQL but **no code reads or writes it**."),
        FIG("erd", PNG / "erd.png", "Entity relationship diagram (from supabase_complete_setup.sql)", max_h=13),
        P("{tab:articles} and {tab:othertables} give the schema. Row Level Security is enabled on all three tables: the "
          "public key can only read articles, may read and insert visitor names, and a user could access only their own "
          "profile row."),
        TAB("articles", "Table articles (columns, types and constraints)",
            ["Column", "Type", "Constraint / default", "Description"],
            [["id", "uuid", "PK, gen_random_uuid()", "Article identifier"],
             ["title", "text", "NOT NULL, UNIQUE", "Headline (database-level duplicate check)"],
             ["source_domain, source_url", "text", "source_url indexed", "Publisher name and original link"],
             ["content_summary", "text", "–", "Excerpt supplied by the feed"],
             ["category", "text", "default 'general'", "Feed category"],
             ["published_at, created_at", "timestamptz", "default now()", "Publication time; ingestion time"],
             ["sentiment", "text", "–", "positive / neutral / negative"],
             ["risk_score", "real", "CHECK 0–1 or NULL", "Combined heuristic risk"],
             ["credibility_label", "text", "CHECK Low/Moderate/High Risk or NULL; no default", "NULL = not assessed"],
             ["needs_verification", "boolean", "default false", "Verification flag"],
             ["confidence_level, model_fake_probability", "real", "–", "Classifier top-class and fake-class scores (uncalibrated)"],
             ["is_fake, credibility_score", "boolean, real", "–", "Legacy classifier fields (NULL without the model)"],
             ["dimensions", "jsonb", "default '{}'", "Eight scores (or null) and explanations"],
             ["ai_reasoning", "text", "–", "Explanation of risk and verification"],
             ["ai_summary, summary_method", "text", "–", "Extractive summary and its method"],
             ["group_id, event_title", "text", "group_id indexed", "Cross-source group"],
             ["analysis_status", "text", "CHECK complete/partial/unavailable/pending/legacy", "Completeness of the analysis"],
             ["analysis_method, model_version, analyzed_at", "text, text, timestamptz", "–", "Provenance (e.g. \"rules\", \"pipeline 2.0; rules only\")"]],
            [4.3, 2.4, 4.4, 4.8], size=10),
        TAB("othertables", "Tables named_visitors and user_profiles",
            ["Table.column", "Type", "Constraint", "Description"],
            [["named_visitors.id", "uuid", "PK, gen_random_uuid()", "Visitor identifier"],
             ["named_visitors.name", "text", "UNIQUE, NOT NULL, 1–40 characters", "Display name entered on the first visit"],
             ["named_visitors.created_at", "timestamptz", "default now()", "Registration time"],
             ["user_profiles.id", "uuid", "PK, FK → auth.users(id) ON DELETE CASCADE", "Defined but not used by the code"],
             ["user_profiles.name, saved_topics, created_at", "text, text[], timestamptz", "RLS: own row only", "Reserved for future user accounts"]],
            [4.6, 2.8, 4.4, 4.1], size=10),

        H2("3.5", "Use-case Diagram"),
        P("{fig:usecase} shows the use cases. The Scheduler starts the ingestion cycle every 30 minutes; the cycle "
          "includes collecting the feeds, removing duplicates, analysing the articles and grouping events. The Operator "
          "(or any API client) can start the same cycle with POST /api/ingest when an ingest token is configured, and "
          "can analyse custom text. The Reader has eight use cases; searching is extended by an external news search "
          "when there are few local matches."),
        FIG("usecase", PNG / "usecase.png", "Use-case diagram", max_h=18),

        H2("3.6", "Sequence Diagram"),
        P("{fig:sequence} shows a reader opening an article and downloading its report. The article page is a Next.js "
          "server component. It calls `getEdition()`, which reads the 500 newest rows from Supabase only when the cached "
          "edition is older than 60 seconds, and then finds the article in the edition (an article older than the "
          "edition is read by id as a fallback). The PDF can be produced in two ways: by FastAPI with ReportLab "
          "(GET /api/v1/report/{id}, shown only for database articles when the backend URL is configured), or in the "
          "browser with jsPDF (\"Export in browser\"), which needs no server."),
        FIG("sequence", PNG / "sequence.png", "Sequence diagram: viewing an article and downloading its PDF report", max_h=18.5),

        H2("3.7", "Activity Diagram"),
        P("{fig:activity} shows one scheduled ingestion run (`fetch_and_store_job`). The first loop downloads every feed; "
          "a failed feed is logged and the run continues. The batch is then de-duplicated. The second loop processes "
          "every article: an article already in the database is skipped before analysis; otherwise the eight "
          "dimensions are scored, the models run if available, the risk is computed or marked not assessed, the Needs "
          "Verification flag is set and the article is inserted. After the loop, articles of the last 48 hours are "
          "re-grouped."),
        FIG("activity", PNG / "activity.png", "Activity diagram of one ingestion run", max_h=20),

        H2("3.8", "Component Diagram"),
        P("{fig:component} shows the software components in UML 2 notation. The Next.js subsystem provides the HTML pages "
          "and `/api/*` routes; `repository.ts` is its only data-access component and depends on the live-feed, "
          "external-search and scoring components. The FastAPI subsystem provides the REST API; the router depends on "
          "the analysis pipeline, the storage service and the report service, and the scheduler drives the RSS fetcher "
          "and the storage service. Supabase provides one interface (its PostgREST API) that both subsystems require: "
          "Next.js with the anon key for reading, FastAPI with the service-role key for writing."),
        FIG("component", PNG / "component.png", "Component diagram (UML 2)", max_h=17),

        H2("3.9", "Deployment Diagram"),
        P("{fig:deployment} shows the deployment architecture supported by the code. The reader's browser talks to a "
          "Next.js server (Node.js 20 or later) and, only for the optional server PDF, to the backend. The backend runs "
          "on Python 3.10+ with Uvicorn; the repository contains a Dockerfile that builds a python:3.10-slim image "
          "listening on port 7860. Both servers connect to the Supabase cloud database over HTTPS with different keys. "
          "The backend downloads model weights from the Hugging Face Hub on first use and fetches the publisher RSS "
          "feeds; the Next.js server contacts the live feeds and external news services. The project was run locally "
          "during development; no production deployment is claimed."),
        FIG("deployment", PNG / "deployment.png", "Deployment diagram (UML 2)", max_h=17),

        H2("3.10", "Sample Input and Output Screens"),
        P("The screens below were captured from the running application on 25 November 2026. The articles are 41 real "
          "items from the BBC World and Al Jazeera RSS feeds, processed by the implemented backend pipeline and served "
          "from the database. The transformer models were **not installed** in that environment, so every article was "
          "analysed in rules-only mode: the status is \"partial\", \"Classifier fake score\" shows \"Not available\" and "
          "\"Classifier confidence\" shows \"Not reported\". Because RSS excerpts are short, all 41 articles are flagged "
          "Needs Verification, and all received the label Low Risk (reputable publishers, neutral wording). "
          "{tab:pages} lists the pages of the application."),
        TAB("pages", "Pages of the application (frontend/src/app/)",
            ["Page (URL)", "Purpose"],
            [["/", "Front page: latest articles, breaking news with \"Also reporting this story\", daily feed, risk counts, featured stories, most-covered events, section blocks."],
             ["/section/[slug]", "All articles of one of eight sections (world, india, politics, business, technology, science, culture, sports)."],
             ["/article/[id]", "Excerpt, original link, credibility panel, PDF download, \"Also reported by\", analysis supplement with radar chart and table."],
             ["/search", "Keyword search with six filters, 20 results per page; external results when fewer than five reports match every term."],
             ["/compare", "\"One story, many newsrooms\": each event with one column per publisher."],
             ["/analytics", "\"The News Intelligence Report\" with seven figures."]],
            [3.4, 12.5]),
        H3("Input 1: Reader registration"),
        P("On the first visit the reader enters a display name of 1–40 characters ({fig:register}). It is sent to "
          "POST /api/auth/profile, stored in the `named_visitors` table and kept in the browser."),
        FIG("register", IMG / "ui_register.jpg", "Input: reader registration modal (first visit)", width=12.5),
        H3("Output 1: Front page"),
        P("{fig:home} shows the front page built from the ingestion database (41 reports from two publishers). Every "
          "card shows the risk mark and the \"Needs verification\" tag."),
        FIG("home", IMG / "ui_home.jpg", "Output: front page of The Daily Signal (rules-only analysis; all items flagged for verification)", width=12.5),
        H3("Input/Output 2: Search and filters"),
        P("The reader types keywords and can filter by section, publisher, credibility risk (including \"Not "
          "assessed\"), order, date range and \"Needs verification only\". {fig:search} shows a search for \"russia\" "
          "(six reports match every term) and {fig:verify} the Sports section combined with the verification filter "
          "(three reports)."),
        FIG("search", IMG / "io_search.jpg", "Input and output: search for \"russia\", newest first", width=11),
        FIG("verify", IMG / "io_verify.jpg", "Input and output: Sports section with \"Needs verification only\"", width=11.5),
        H3("Output 2: Article page and credibility panel"),
        P("The article page ({fig:article}) shows the stored excerpt, the link to the original report and the credibility "
          "panel. For this BBC article the rule-based risk is 0.15 (Low Risk); the classifier fields are \"Not "
          "available\" and \"Not reported\" because the models were not installed, and the article needs verification "
          "because the feed supplied only 52 characters (minimum 150). \"Also reported by\" lists the grouped Al Jazeera "
          "report."),
        FIG("article", IMG / "out_article_top.jpg", "Output: article page with credibility panel (classifier \"Not available\", status partial)", width=11),
        H3("Output 3: Eight-dimension analysis"),
        P("The analysis supplement ({fig:analysis}) shows the radar chart and the table of the eight scores with the "
          "meaning of each scale and an explanation. Here Readability, Headline Accuracy and Content Quality describe a "
          "one-sentence excerpt, not the full article."),
        FIG("analysis", IMG / "out_article_analysis.jpg", "Output: eight-dimension radar chart and score table", width=14),
        H3("Output 4: Cross-source comparison"),
        P("The compare page ({fig:compare}) lists the five events that were covered by both publishers. The first event "
          "shows the accent folding of the grouping step: \"Ábrego García\" (BBC) and \"Abrego Garcia\" (Al Jazeera) are "
          "matched."),
        FIG("compare", IMG / "out_compare.jpg", "Output: events covered by more than one publisher", width=11),
        H3("Output 5: Responsive mobile view"),
        P("{fig:mobile} shows the same article page on a mobile screen."),
        FIG("mobile", IMG / "ui_mobile.jpg", "Output: article page on a mobile screen", max_h=11),
        H3("Input/Output 6: Analyse-text API"),
        P("POST /api/analyze accepts any text and returns the full analysis without storing it. {lst:analyze} shows a "
          "real request and response of the implemented API (`docs/report/analyze_example.json`), produced in rules-only "
          "mode. The deliberately sensational text receives Propaganda 5, but only Moderate Risk 0.57, because the "
          "unknown blog has no Source Credibility score and the remaining dimensions dilute the propaganda penalty; "
          "this limitation is discussed in Chapter 8."),
        CODE("analyze", "Request and response of POST /api/analyze (rules-only mode)", analyze_example_text(), 8),
    ]

    # ════════════════════════════════ Chapter 4 ════════════════════════════════
    B += [
        H1("4", "Coding"),
        P("The backend is a FastAPI application (`backend/main.py`) whose lifespan starts the scheduler. The analysis "
          "engine was first written in TypeScript for live feeds and then ported line by line to Python, so that the "
          "backend and the frontend use one scoring method; `js_round()` in Python reproduces JavaScript's "
          "`Math.round` so that both give identical numbers. Database changes are delivered as idempotent SQL "
          "migrations. The steps to run the system are: (1) run `supabase_complete_setup.sql` in Supabase; (2) in "
          "`backend`, install `requirements.txt`, set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` and start "
          "`uvicorn main:app`; (3) in `frontend`, set the public Supabase URL and anon key and run `npm install` and "
          "`npm run dev`."),
        H2("4.1", "Code snippets"),
        P("The following excerpts are copied unchanged from the project source code; the file and line numbers are "
          "given in each caption."),
        H3("Rule-based risk"),
        P("{lst:rule} defines the constants of the risk method and the function that turns the scored dimensions into "
          "a rule-based risk. A dimension that is `None` is skipped, and no score is returned when less than 65% of the "
          "weight is available."),
        CODE("rule", f"Weights, thresholds and rule_risk() ({rule_src})", rule_risk),
        H3("Combining rules and classifier; Needs Verification"),
        P("{lst:pipe} is the core of `analyze_article()`. The final risk is the mean of the rule-based risk and the "
          "classifier's fake-class score when the classifier ran; each verification condition adds a readable reason."),
        CODE("pipe", f"Risk combination and verification flags ({pipe_src})", pipe),
        H3("Fake-news classifier label mapping"),
        P("The model configuration of BERT-tiny does not name its labels, so the label that means \"fake\" is "
          "configurable (`FAKE_NEWS_FAKE_LABEL`, default `LABEL_1`). {lst:clf} reads the fake-class score, derives the "
          "confidence, and rejects unexpected labels instead of guessing."),
        CODE("clf", f"Label mapping in classify_fake_news() ({clf_src})", clf),
        H3("Seed-based cross-source grouping"),
        P("In {lst:clu} each unassigned article is a seed; later articles within 36 hours whose TF-IDF cosine similarity "
          "to the seed is at least 0.32 join it. Only one article per publisher is kept, and a group needs at least two "
          "publishers."),
        CODE("clu", f"Grouping loop of cluster_articles() ({clu_src})", clu),
        H3("RSS parsing"),
        CODE("rss", f"parse_feed() ({rss_src})", rss),
        P("{lst:rss} turns one feed document into article records. Entries without a title or link are skipped, and an "
          "excerpt equal to the title is stored as empty, so that later analysis can tell a headline-only item from real "
          "body text."),
        H3("API endpoint"),
        P("{lst:api} is the PDF endpoint. FastAPI validates the path parameter as a UUID (a malformed id returns 422), "
          "database errors become a generic 503, and ReportLab is imported only when a report is requested."),
        CODE("api", f"GET /report/{{article_id}} ({api_src})", api),
        H3("Frontend data access and report link"),
        P("{lst:repo} shows how the Next.js server reads the edition directly from Supabase with the anon key and caches "
          "it for 60 seconds; when the call fails or the table is empty it returns `null` and the live-feed fallback is "
          "used. {lst:report} shows that the server PDF link exists only for database articles when a backend URL is "
          "configured."),
        CODE("repo", f"loadDatabaseArticles() ({repo_src})", repo),
        CODE("report", f"Server PDF link in ReportDownload ({repo2_src})", repo2),
        H3("Browser scoring of live items"),
        P("{lst:scoring} is the TypeScript counterpart used for live-feed items. Because the browser has no classifier, "
          "only the first three verification conditions apply, and the confidence is always null."),
        CODE("scoring", f"Risk label and verification in analyseText() ({sc_src})", sc),
    ]

    # ════════════════════════════════ Chapter 5 ════════════════════════════════
    B += [
        H1("5", "Testing Process"),
        P("Testing in this project checks that the software behaves as specified: that every module produces the "
          "documented output for given inputs, never invents a missing value, and handles failures. It does not measure "
          "how accurate the models are; that would need a labelled dataset and the installed models, which were not "
          "available (see Section 5.3)."),
        H2("5.1", "Test Planning"),
        P("{tab:plan} summarises the test plan. External services were replaced by test doubles so that every automated "
          "test can run without network access, credentials or model downloads."),
        TAB("plan", "Test plan",
            ["Item", "Plan"],
            [["Objective", "Verify collection, cleaning, de-duplication, scoring, risk, verification, grouping, storage, API, reports and UI components against the specification; confirm that missing values are never replaced by defaults."],
             ["Scope", "All backend services and the API; frontend scoring, grouping, search, PDF generator and news card; production build, lint and type check."],
             ["Out of scope", "Model accuracy and calibration (no labelled data, models not installed); load and performance testing; live feeds and live Supabase in the automated suite."],
             ["Test doubles", "FakePipeline with fixed label scores (no model download); in-memory FakeSupabase client; httpx MockTransport for RSS feeds; mocked fetch for GDELT and GNews."],
             ["Tools", "pytest 9.1.1 (backend), Vitest 4.0.18 with Testing Library and jsdom (frontend), ESLint, TypeScript compiler, Next.js build."],
             ["Entry / exit criteria", "Entry: module implemented and runnable. Exit: all automated tests pass, lint and type check report no errors, the production build succeeds; opt-in tests that cannot run are listed as not executed."],
             ["Opt-in tests", "RUN_MODEL_TESTS=1 (downloads and runs the real models); RUN_LIVE_TESTS=1 (real RSS feeds and Supabase connectivity)."]],
            [3.2, 12.7], first_bold=True),
        H2("5.2", "Software Testing Life Cycle (STLC)"),
        P("The STLC was applied in six phases, adapted to a small team and an automated test suite ({tab:stlc})."),
        TAB("stlc", "STLC phases as applied in this project",
            ["Phase", "Activities in this project", "Output"],
            [["Requirement analysis", "Testable rules taken from the synopsis and the code: thresholds (0.35, 0.65, 150 characters, 0.32), null rules, status values, API validation limits.", "List of testable requirements ({tab:fr}, {tab:risk})"],
             ["Test planning", "Levels, tools, test doubles, opt-in tests and exit criteria chosen.", "Test plan ({tab:plan})"],
             ["Test case design", "Test functions written per module, including boundary values (risk 0.35/0.36/0.65/0.66) and failure cases (feed returns 500, model fails to load, database down).", "66 backend and 32 frontend test cases"],
             ["Environment set-up", "pytest.ini markers, conftest fixtures (fake_models, no_models, ENABLE_SCHEDULER=0), shared scoring vectors, Vitest with jsdom.", "Repeatable offline test environment"],
             ["Test execution", "Suites run after each change and again for this report on 25 November 2026; build, lint and type check run.", "Results in {tab:exec}"],
             ["Test closure", "Defects found by the audit fixed and regression tests added (e.g. Al Jazeera source score); untested areas documented.", "This chapter and Chapter 8"]],
            [3.2, 8.4, 4.3], size=10, first_bold=True),
        H2("5.3", "Types of Testing"),
        P("{tab:types} lists the types of testing that were carried out and those that were not."),
        TAB("types", "Types of testing",
            ["Type", "Done?", "How it was done"],
            [["Unit testing", "Yes", "Each function tested in isolation: dimension rules, label mapping, extractive summary, URL normalisation, search ranking, risk thresholds."],
             ["Integration testing (with fakes)", "Yes", "Pipeline with FakePipeline models; store-and-group with the in-memory database; feed fetching with a mock HTTP transport."],
             ["API testing", "Yes", "FastAPI TestClient: validation (422), not found (404), errors not leaked (503), PDF response, CORS, ingest token, rate limit (429)."],
             ["Parity testing", "Yes", "Python and TypeScript outputs compared with the same ten reference inputs in shared/scoring_vectors.json."],
             ["Regression testing", "Yes", "Tests added for fixed defects (null label never \"Low Risk\", Al Jazeera feed name in the reference table); full suites re-run after every change."],
             ["Component (UI) testing", "Yes", "NewsCard rendered with Testing Library; PDF generator output checked."],
             ["Build and static checks", "Yes", "npm run build, npm run lint, tsc --noEmit."],
             ["End-to-end demonstration", "Yes (manual)", "41 real BBC World and Al Jazeera items processed by the backend pipeline (rules-only) and viewed in the running application; screens in Section 3.10."],
             ["Model accuracy / calibration", "No", "No labelled dataset; models not installed. No accuracy, precision, recall, F1 or calibration figures exist."],
             ["Live integration", "No", "RUN_LIVE_TESTS (real feeds, Supabase) and RUN_MODEL_TESTS were not executed: no network access or credentials in the test environment."],
             ["Load / performance", "No", "Not carried out."]],
            [3.6, 1.8, 10.5], size=10, first_bold=True),
        H2("5.4", "Sample Test Cases"),
        P("{tab:cases} gives representative test cases taken from the real test files; the name of each test function "
          "is given in brackets. All passed in the run of 25 November 2026."),
        TAB("cases", "Sample test cases",
            ["ID", "Module", "Input", "Expected result", "Actual result", "Status"],
            [["TC01", "Scoring parity (test_dimension_service, scoringParity.test)", "10 reference inputs of shared/scoring_vectors.json", "Python and TypeScript give identical scores and explanations", "Identical", "Pass"],
             ["TC02", "Risk labels (test_risk_thresholds)", "Scores 0.35 / 0.36 / 0.65 / 0.66", "Low / Moderate / Moderate / High", "As expected", "Pass"],
             ["TC03", "Rule risk (test_rule_risk_requires_enough_weight)", "Only propaganda, objectivity, bias scored (0.50 of weight)", "No risk score (below 0.65)", "None returned", "Pass"],
             ["TC04", "Pipeline (test_headline_only_is_unavailable_never_low_risk)", "Headline \"Markets fall\", no excerpt, \"Unknown Blog\"", "risk and label NULL, status unavailable, needs verification", "As expected", "Pass"],
             ["TC05", "Pipeline (test_low_model_confidence_flags_verification)", "Fake model returns LABEL_0 0.52 / LABEL_1 0.48", "Needs verification; reason mentions classifier confidence", "As expected", "Pass"],
             ["TC06", "Pipeline (test_disagreement_flags_verification)", "Fake model returns LABEL_1 0.98 for a reputable article", "Needs verification; reason mentions disagreement", "As expected", "Pass"],
             ["TC07", "AI service (test_label_1_is_read_as_fake)", "FakePipeline with LABEL_1 as the higher score", "fake_probability = LABEL_1 score, predicted \"fake\"", "As expected", "Pass"],
             ["TC08", "AI service (test_model_load_failure_returns_unavailable)", "Model loading raises an error", "Status unavailable, no score invented", "As expected", "Pass"],
             ["TC09", "RSS fetcher (test_failed_feed_does_not_stop_the_run)", "Two feeds, one returns HTTP 500", "Other feed collected; failed feed listed", "failed = [\"Bad\"], 2 articles", "Pass"],
             ["TC10", "Storage (test_stores_new_articles_and_skips_duplicates)", "Batch with a stored title and a stored URL plus tracking parameter", "1 inserted, 2 duplicates; label NULL, not \"Low Risk\"", "As expected", "Pass"],
             ["TC11", "Grouping (test_groups_same_event_across_publishers)", "BBC and AlJazeera Eurovision reports and an unrelated CNN report", "One group of BBC and AlJazeera", "group ev-1", "Pass"],
             ["TC12", "Grouping (test_reports_far_apart_in_time_are_not_grouped)", "Same story 1 h and 40 h old", "Not grouped (gap > 36 h)", "No group", "Pass"],
             ["TC13", "API (test_analyze_validation)", "Empty text; 20,001 characters; missing body", "HTTP 422", "422", "Pass"],
             ["TC14", "API (test_rate_limit)", "3 requests to /api/analyze with limit set to 2", "200, 200, 429", "200, 200, 429", "Pass"],
             ["TC15", "API (test_ingest_disabled_without_token)", "POST /api/ingest without INGEST_TOKEN; with a wrong token", "404; 403", "404; 403", "Pass"],
             ["TC16", "Frontend (NewsCard.test)", "Article without a risk score", "Shows \"not assessed\", never a default label", "As expected", "Pass"],
             ["TC17", "Frontend search (search.test)", "\"Facebook lawsuit 2026\"", "Finds the Meta report through the alias and the year", "As expected", "Pass"],
             ["TC18", "Live model test (test_real_models_load_and_return_scores)", "RUN_MODEL_TESTS=1", "Real models load and return scores", "Not executed", "Skipped"]],
            [1.2, 4.3, 3.3, 3.3, 2.3, 1.4], size=9),
        P("{tab:exec} summarises the execution of all suites. The numbers were observed when the commands were run for "
          "this report on 25 November 2026."),
        TAB("exec", "Test execution summary (25 November 2026)",
            ["Suite / check", "Command", "Result"],
            [["Backend unit, integration and API tests", "python3 -m pytest -q", "63 passed, 3 skipped (opt-in)"],
             ["Frontend tests", "npx vitest run", "32 passed in 5 files"],
             ["Frontend lint", "npm run lint", "No errors"],
             ["Frontend type check", "npx tsc --noEmit -p .", "No errors"],
             ["Frontend production build", "npm run build", "Compiled successfully; 13 routes"],
             ["End-to-end demonstration", "Real BBC and Al Jazeera items → pipeline → app", "41 articles stored and shown, 5 multi-source events"],
             ["Real model inference", "RUN_MODEL_TESTS=1", "Not executed (models not installed)"],
             ["Live RSS and Supabase", "RUN_LIVE_TESTS=1", "Not executed (no network access or credentials)"]],
            [4.8, 5.4, 5.7], first_bold=True),
        P("No accuracy, precision, recall or F1 figures are reported, because the classifier was never run on real "
          "weights and no labelled news dataset was evaluated. `backend/scripts/validate_models.py` is provided to print "
          "the raw model outputs on six hand-picked examples once the models are installed; its own documentation says "
          "that it is not a benchmark."),
    ]

    # ════════════════════════════════ Chapter 6 ════════════════════════════════
    B += [
        H1("6", "Reports"),
        P("The system produces two kinds of report: a downloadable PDF report for one article, and an analytics "
          "dashboard for the whole edition."),
        H3("Article PDF report"),
        P("The PDF report can be generated by two independent generators with the same content ({tab:pdf}). The server "
          "report is built by `backend/services/report_service.py` with ReportLab and streamed by GET /api/report/{id}; "
          "it is not stored. The browser report is built by `frontend/src/lib/pdfReportGenerator.ts` with jsPDF and "
          "works for every article, including live-feed items. Missing values are printed as \"Not recorded\", \"Not "
          "computed\", \"Not available\" or \"Not reported\", and \"n/a\" for an unscored dimension."),
        TAB("pdf", "Contents of the PDF report",
            ["Section", "Server report (ReportLab)", "Browser report (jsPDF)"],
            [["Header", "The Daily Signal, Article Intelligence Report, generation time (UTC), MIT-WPU M.Sc Computer Science, Group 17", "The Daily Signal, Article Intelligence Report, generation time, analysis method"],
             ["Article", "Category, publisher, title, published time, source link", "Same"],
             ["Text", "Publisher excerpt box; extractive summary box", "Same"],
             ["Credibility", "Risk label, risk score, classifier fake score, classifier confidence, verification, reasoning", "Same"],
             ["Dimensions", "Eight scores with scale and explanation", "Same, plus a score bar per dimension"],
             ["Method", "Method note; status, method, model version, analysis time; disclaimer", "Method note for heuristic or model analysis; disclaimer"],
             ["Footer", "The Daily Signal, MIT-WPU, Group 17; page number", "The Daily Signal, MIT-WPU M.Sc Computer Science, Group 17; \"Page p of n\""]],
            [2.6, 7.0, 6.3], size=10, first_bold=True),
        P("{fig:pdf} shows page 1 of a server report for the BBC article of Section 3.10. It shows status \"partial\" and "
          "method \"rules\", consistent with the rules-only run."),
        FIG("pdf", IMG / "out_report.jpg", "Server-generated PDF report, page 1 (GET /api/report/{id}, rules-only analysis)", max_h=17),
        H3("Analytics dashboard"),
        P("The page /analytics, \"The News Intelligence Report\", summarises the edition in four headline figures and seven "
          "charts: reports per section, credibility-risk labels, tone, average dimension scores, publication timeline "
          "over the last 36 hours, publishers, and publishers per event. Each dimension average uses only the articles "
          "where that dimension could be scored. {fig:analytics} shows the dashboard for the 41-article demonstration "
          "edition: 41 reports, 5 multi-source events (10 reports grouped), 41 flagged for verification (100%), and an "
          "average Source Credibility of 89 (BBC 93 and Al Jazeera 86). The FastAPI endpoint GET /api/analytics returns "
          "the same kind of statistics as JSON."),
        FIG("analytics", IMG / "out_analytics.jpg", "Analytics dashboard (41 reports, rules-only analysis)", width=15),
    ]

    # ════════════════════════════════ Chapter 7 ════════════════════════════════
    B += [
        H1("7", "Summary/Conclusion/Interpretation"),
        H2("7.1", "Summary"),
        P("The project delivers a working news aggregator with transparent credibility and content analysis. News is "
          "collected automatically every 30 minutes, cleaned, and exact duplicates are removed. Each new article is "
          "analysed with eight explained dimension scores, a rule-based risk (combined with the BERT-tiny classifier "
          "when it is installed), a sentiment label and a Needs Verification flag; related reports are grouped across "
          "publishers; and the results are available through a REST API, a responsive dashboard, an analytics page and "
          "PDF reports. The automated tests that could run in the development environment passed: backend 63 passed with "
          "3 opt-in tests skipped, frontend 32 passed, with a clean lint, type check and production build."),
        H2("7.2", "Conclusion"),
        P("The main achievement is honesty of the output. A risk score is given only when the scored dimensions carry at "
          "least 65% of the weight; otherwise the article is shown as \"not assessed\". Readability, Headline Accuracy, "
          "Content Quality and the Source Credibility of an unknown publisher are left empty for headline-only items "
          "instead of receiving a default value. Model scores are labelled as uncalibrated, and the database no longer "
          "marks unanalysed articles as \"Low Risk\". During the final audit three defects were found and fixed: "
          "backend-ingested Al Jazeera rows (stored as \"AlJazeera\") received no source score; the registration form "
          "accepted names up to 60 characters while the database allows 40; and rule-only rows were labelled as "
          "model-analysed in the frontend. Regression tests were added where applicable."),
        P("The honest summary for the viva is: **implemented and unit-tested, demonstrated in rules-only mode**. The "
          "transformer models are wired in and their handling is tested with fake pipelines, but they were never run on "
          "real weights, so no claim about their accuracy is made. The system is an aid for critical reading, not a "
          "fact-checking authority."),
        H2("7.3", "Interpretation: synopsis versus implementation"),
        P("{tab:synvs} compares each feature promised in the synopsis with the implementation. The pattern is "
          "consistent: everything that is plain software was built and tested, while everything that needs a labelled "
          "dataset or a generative model was not."),
        TAB("synvs", "Synopsis versus implementation",
            ["Synopsis feature", "Status", "Source file(s) and what the code does"],
            [["RSS collection from multiple sources", "Fully", "rss_fetcher.py: 11 feeds, 5 categories, ≤ 8 entries per feed, 15 s timeout"],
             ["Cleaning and normalisation", "Fully", "rss_fetcher.py: HTML stripping, URL/title normalisation, UTC dates"],
             ["30-minute scheduled ingestion", "Fully", "scheduler.py: APScheduler, overlap lock, max_instances = 1"],
             ["Remove duplicate or highly similar entries", "Partially", "rss_fetcher.py, db_service.py: exact normalised title/URL only; similar reports are grouped"],
             ["BERT credibility-risk with confidence", "Fully (not run on real weights)", "ai_service.py, analysis_pipeline.py: mean of rule risk and fake score; rules alone if the model fails"],
             ["Sentiment Positive / Negative / Neutral", "Partially (different method)", "ai_service.py, dimension_service.py: binary SST-2 plus 41–59 neutral band; word-list fallback"],
             ["Short AI-generated summaries", "Not implemented", "analysis_pipeline.py: extractive summary instead (≥ 3 sentences); frontend takes the first two sentences"],
             ["Calibrated confidence / calibration evaluation", "Not implemented", "Scores labelled raw and uncalibrated; uncertainty band and thresholds only"],
             ["Eight-dimension analysis", "Fully", "dimension_service.py = scoring.ts (seven lexical rules plus model sentiment)"],
             ["Needs Verification", "Fully (broader)", "analysis_pipeline.py: five conditions"],
             ["Cross-source comparison", "Partially", "clustering_service.py = clustering.ts, /compare page; no automatic framing analysis"],
             ["Supabase storage, search and filters", "Fully", "supabase_complete_setup.sql, db_service.py, repository.ts, search.ts"],
             ["FastAPI endpoints incl. /categories, /sources", "Partially", "router.py: 8 routes; no /categories or /sources"],
             ["Frontend retrieves data through FastAPI", "Not implemented (different design)", "repository.ts: Next.js reads Supabase directly; FastAPI only for the server PDF"],
             ["Recharts analytics", "Fully", "analytics/page.tsx, DashboardAnalytics.tsx, DimensionRadarChart.tsx"],
             ["Downloadable PDF report", "Fully", "report_service.py (ReportLab), pdfReportGenerator.ts (jsPDF)"],
             ["Separate Source, Summary, Report entities", "Not implemented", "Single articles table with JSONB dimensions; user_profiles defined but unused"],
             ["Model evaluation (accuracy, precision, recall, F1)", "Not implemented", "validate_models.py prints six examples; opt-in model test not run"],
             ["Live-RSS fallback edition", "Extra", "liveNewsService.ts, sections.ts (31 feed URLs)"],
             ["External news search", "Extra", "externalSearch.ts (Google News RSS, GNews, GDELT)"],
             ["Name-only reader registration", "Extra", "NameAuthModal.tsx, api/auth/profile/route.ts, named_visitors"],
             ["Custom-text analysis and token ingestion API", "Extra", "router.py: POST /analyze, POST /ingest"],
             ["Rate limit, CORS allow-list, RLS hardening", "Extra", "main.py, 02_integrity_and_security.sql"],
             ["Python/TypeScript parity tests, re-analysis CLI", "Extra", "shared/scoring_vectors.json, scripts/reanalyze.py"]],
            [4.4, 3.0, 8.5], size=9),
        P("Two results of the demonstration need interpretation. First, all 41 articles were flagged Needs Verification. "
          "This follows from the input, not from a fault: RSS excerpts are usually shorter than the 150-character "
          "evidence threshold. Second, all 41 articles were labelled Low Risk. They come from two reputable publishers "
          "with neutral wording, so the rule-based dimensions are high; the verification flag, not the label, carries the "
          "uncertainty in this case."),
    ]

    # ════════════════════════════════ Chapter 8 ════════════════════════════════
    B += [
        H1("8", "Limitations of System"),
        P("{tab:limits} lists the known limitations of the system."),
        TAB("limits", "Limitations of the system",
            ["Area", "Limitation"],
            [["Short text", "RSS feeds supply only a headline and one or two sentences. Most articles have fewer than 150 characters, so most carry the verification flag, few receive a summary, and Headline Accuracy and Content Quality describe the excerpt, not the article."],
             ["Models not verified", "BERT-tiny and DistilBERT were never run on real weights in this project. The meaning of LABEL_1 = fake is an assumption (configurable), not confirmed."],
             ["No evaluation or calibration", "Scores are raw softmax outputs. No accuracy, precision, recall, F1 or calibration measure exists."],
             ["Lexicon rules", "Seven dimensions use word lists and patterns. For example, \"won't\" matches the positive word \"won\", and an obviously sensational text from an unknown site reached only Moderate risk (0.57) without the classifier."],
             ["Source table", "Source Credibility uses a hand-made list of 14 newsrooms; publishers outside it are left unscored and no source history is kept."],
             ["Grouping", "Text similarity can group different events on the same topic and can miss reports worded very differently. Grouping is not claim verification."],
             ["Duplicates", "Only exact duplicates (normalised title or URL) are removed."],
             ["Summaries", "Extractive only, and only when the excerpt has at least three sentences."],
             ["Language and sources", "English only; fixed feed lists."],
             ["Security and scale", "The rate limit is kept in memory per server process; registration is name-only; no load test was done."]],
            [3.4, 12.5], first_bold=True),
    ]

    # ════════════════════════════════ Chapter 9 ════════════════════════════════
    B += [
        H1("9", "Proposed Enhancements / Future Scope"),
        P("{tab:future} lists the proposed enhancements, in order of priority."),
        TAB("future", "Proposed enhancements",
            ["Enhancement", "Purpose"],
            [["Install the models and run validate_models.py and the opt-in tests", "Replace the main weakness, never having executed the transformer models, with real evidence; confirm the label mapping."],
             ["Evaluate on a labelled news dataset", "Report accuracy, precision, recall and F1 of the classifier and of the combined risk."],
             ["Calibrate the scores", "Apply temperature scaling and report the expected calibration error (ECE) [7]."],
             ["Fetch full article text where permitted", "Improve every dimension and allow meaningful summaries."],
             ["Abstractive summaries", "Generate short summaries with a summarisation model, with a check against the source text."],
             ["Trained models for bias, objectivity and propaganda", "Replace the word lists with classifiers."],
             ["Sentence embeddings for grouping", "Reduce topic-level false matches; detect near-duplicates."],
             ["More sources and Indian languages", "Wider coverage."],
             ["User accounts with saved topics", "Use the existing user_profiles table with Supabase Auth."]],
            [6.0, 9.9], first_bold=True),
    ]

    # ════════════════════════════════ Chapter 10 ════════════════════════════════
    B += [
        H1("10", "Key Learnings from Project"),
        BL("**Full-stack design.** We learned to separate collection, analysis, storage, API and presentation, and to "
           "decide which server should own which data path (Next.js reading Supabase directly, FastAPI writing).",
           "**Applying NLP models responsibly.** Using pre-trained transformers through Hugging Face pipelines is easy; "
           "interpreting their output is not. We learned to label raw scores as uncalibrated, to handle missing models, "
           "and to avoid presenting a softmax score as a probability of truth.",
           "**Explainable heuristics.** Simple, documented rules with an explanation for each score are easier to "
           "defend than a single opaque number, and their weaknesses are easier to see.",
           "**Honest handling of missing data.** A missing value must stay missing. A database default of \"Low "
           "Risk\" for articles that had never been analysed produced misleading output and had to be removed.",
           "**Testing with test doubles.** Fake model pipelines, an in-memory database and mock HTTP responses made "
           "both suites run offline in a few seconds, and parity vectors kept the Python and TypeScript scoring "
           "identical.",
           "**Database security.** Row Level Security, separate anon and service-role keys, a CORS allow-list and "
           "rate limiting are needed even in an academic project.",
           "**Documentation discipline.** Comparing the synopsis with the code showed that a report must describe what "
           "was built, state what was not, and never claim results that were not measured.",
           "**Teamwork.** We learned to divide the work into modules with clear interfaces, review each other's code "
           "and integrate it through version control."),
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
        "T. Wolf et al., \"Transformers: State-of-the-Art Natural Language Processing,\" in *Proc. EMNLP: System Demonstrations*, 2020; documentation: https://huggingface.co/docs/transformers",
        "M. Romero, \"bert-tiny-finetuned-fake-news-detection,\" Hugging Face model card: https://huggingface.co/mrm8488/bert-tiny-finetuned-fake-news-detection",
        "Hugging Face, \"distilbert-base-uncased-finetuned-sst-2-english,\" model card: https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english",
        "PyTorch documentation: https://pytorch.org/docs/",
        "FastAPI documentation: https://fastapi.tiangolo.com/",
        "Supabase documentation (PostgreSQL, Row Level Security): https://supabase.com/docs",
        "Next.js documentation: https://nextjs.org/docs",
        "React documentation: https://react.dev/",
        "Tailwind CSS documentation: https://tailwindcss.com/docs",
        "Recharts documentation: https://recharts.org/",
        "APScheduler documentation: https://apscheduler.readthedocs.io/",
        "feedparser documentation: https://feedparser.readthedocs.io/",
        "Beautiful Soup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/",
        "ReportLab User Guide: https://docs.reportlab.com/",
        "jsPDF documentation: https://github.com/parallax/jsPDF",
        "pytest documentation: https://docs.pytest.org/",
        "Vitest documentation: https://vitest.dev/",
        "The GDELT Project, \"GDELT DOC 2.0 API\": https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/",
        "GNews API documentation: https://gnews.io/docs/",
        "RSS Advisory Board, \"RSS 2.0 Specification\": https://www.rssboard.org/rss-specification",
        "W3Schools (supplementary programming reference): https://www.w3schools.com/",
        "Stack Overflow (supplementary problem-solving reference): https://stackoverflow.com/",
        "Project repository: AI-Powered News Aggregator (GitHub repository maintained by the project group).",
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
    for b in bl:
        k = b[0]
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
            B.table(refs[f"tab:{key}"], cap, header, [[resolve(c, refs) for c in r] for r in rows], widths, size, fb)
        elif k == "fig":
            _, key, path, cap, width, max_h = b
            B.figure(refs[f"fig:{key}"], path, cap, width, max_h)
        elif k == "code":
            _, key, cap, text, size = b
            B.code(refs[f"lst:{key}"], cap, text, size)
        elif k == "ref":
            B.p(b[1], style="Reference")
        elif k == "break":
            B.page_break()
