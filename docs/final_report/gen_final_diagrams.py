"""The eight design diagrams of the final project report (docs/final_report/diagrams/*.svg).

Exactly the diagrams named in the college index: 3.2 module hierarchy, 3.3 architecture, 3.4 class,
3.5 use case, 3.6 sequence, 3.7 activity, 3.8 component, 3.9 deployment. Every diagram is drawn from
the code (backend/, frontend/src/, backend/db/*.sql), not from the synopsis.

Page fit: each diagram is printed alone on a portrait A4 page at the full text width (15.92 cm =
451 pt). Canvases are therefore at most 620 units wide and about 880 high, and no text is smaller
than 11 units, so the smallest label prints at >= 11 x 451 / 620 = 8.0 pt.

Run:  python3 docs/final_report/gen_final_diagrams.py   then  node docs/final_report/render_png.js
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "report"))
import gen_diagrams as gd  # noqa: E402
from gen_diagrams import SVG, INK, FILL, Box  # noqa: E402

OUT = HERE / "diagrams"
OUT.mkdir(exist_ok=True)
gd.OUT = OUT  # the helpers' save() writes into gd.OUT
W = 620       # canvas width of every diagram
MIN = 11      # smallest font size used


# ─── drawing helpers ────────────────────────────────────────────────────────────────────────

def box(s, x, y, w, h, lines, size=12, fill=FILL, r=5, bold_first=False, dash=False):
    b = s.rect(x, y, w, h, r=r, fill=fill, dash=dash)
    lh = size + 3
    top = y + h / 2 - (len(lines) - 1) * lh / 2 + size * 0.35
    for i, l in enumerate(lines):
        s.text(x + w / 2, top + i * lh, l, size, weight="bold" if (bold_first and i == 0) else "normal")
    return b


def lab(s, x, y, txt, anchor="start", bg=False, size=MIN):
    """Italic connector label (one or more lines)."""
    for i, t in enumerate(txt.split("\n")):
        s.text(x, y + i * (size + 3), t, size, anchor=anchor, style="italic", bg=bg)


def comp_icon(s, x, y):
    """UML 2 component icon (top-right corner of a component box)."""
    s.add(f"<rect x='{x}' y='{y}' width='13' height='15' fill='white' stroke='{INK}' stroke-width='1'/>"
          f"<rect x='{x - 4}' y='{y + 3}' width='8' height='3.5' fill='white' stroke='{INK}' stroke-width='1'/>"
          f"<rect x='{x - 4}' y='{y + 9}' width='8' height='3.5' fill='white' stroke='{INK}' stroke-width='1'/>")


def component(s, x, y, w, h, lines, size=12):
    b = s.rect(x, y, w, h, r=0, fill="white", sw=1.2)
    comp_icon(s, x + w - 18, y + 5)
    s.text(x + w / 2 - 5, y + 15, "«component»", MIN, style="italic")
    for i, l in enumerate(lines):
        s.text(x + w / 2 - 5, y + 31 + i * (size + 2), l, size, weight="bold" if i == 0 else "normal")
    return b


def node3d(s, x, y, w, h, title, stereo="«node»", d=10, size=12):
    s.add(f"<polygon points='{x},{y} {x + d},{y - d} {x + w + d},{y - d} {x + w},{y}' fill='#e6e6e6' stroke='{INK}' stroke-width='1.2'/>")
    s.add(f"<polygon points='{x + w},{y} {x + w + d},{y - d} {x + w + d},{y + h - d} {x + w},{y + h}' fill='#d9d9d9' stroke='{INK}' stroke-width='1.2'/>")
    s.rect(x, y, w, h, fill=FILL, sw=1.3)
    s.text(x + w / 2, y + 16, stereo, MIN, style="italic")
    for i, t in enumerate(title.split("\n")):
        s.text(x + w / 2, y + 31 + i * (size + 3), t, size, weight="bold")
    return Box(x, y, w, h)


def inner(s, x, y, w, h, stereo, lines, size=MIN, fill="#fafafa", icon=False):
    s.rect(x, y, w, h, fill=fill, sw=1.1)
    if icon:
        ix, iy = x + w - 15, y + 5
        s.add(f"<path d='M{ix},{iy} h7 l4,4 v10 h-11 z M{ix + 7},{iy} v4 h4' fill='white' stroke='{INK}' stroke-width='0.9'/>")
    s.text(x + w / 2, y + 14, stereo, MIN, style="italic")
    for i, l in enumerate(lines):
        s.text(x + w / 2, y + 29 + i * (size + 3), l, size + (0.5 if i == 0 else 0), weight="bold" if i == 0 else "normal")


def note(s, x, y, w, lines, size=MIN):
    h = 12 + len(lines) * (size + 3)
    f = 12
    s.add(f"<path d='M{x},{y} H{x + w - f} L{x + w},{y + f} V{y + h} H{x} Z' fill='#fffff2' stroke='{INK}' stroke-width='1.1'/>"
          f"<path d='M{x + w - f},{y} V{y + f} H{x + w}' fill='none' stroke='{INK}' stroke-width='1.1'/>")
    for i, l in enumerate(lines):
        s.text(x + 8, y + 17 + i * (size + 3), l, size, anchor="start")
    return Box(x, y, w, h)


def uml(s, x, y, w, title, attrs, ops=None):
    return s.uml(x, y, w, title, attrs, ops, size=MIN)


def ball(s, x, y, r=8):
    s.add(f"<circle cx='{x}' cy='{y}' r='{r}' fill='white' stroke='{INK}' stroke-width='1.3'/>")


def final_node(s, x, y):
    s.add(f"<circle cx='{x}' cy='{y}' r='11' fill='white' stroke='{INK}' stroke-width='1.5'/>"
          f"<circle cx='{x}' cy='{y}' r='6.5' fill='{INK}'/>")


# ─── 3.2 Module hierarchy ───────────────────────────────────────────────────────────────────

def modules():
    s = SVG(W, 860)
    root = box(s, 200, 10, 220, 38, ["AI News Aggregator"], 15, bold_first=True)
    backend = [
        ("Collection", ["services/rss_fetcher.py", "services/scheduler.py"]),
        ("Analysis", ["services/dimension_service.py", "services/ai_service.py", "services/analysis_pipeline.py"]),
        ("Grouping", ["services/clustering_service.py"]),
        ("Storage", ["services/db_service.py", "db/supabase.py", "db/*.sql (schema,", "  migrations)"]),
        ("API &\nReports", ["main.py", "api/router.py", "services/report_service.py"]),
        ("Scripts", ["scripts/reanalyze.py", "scripts/validate_models.py"]),
    ]
    frontend = [
        ("Data\naccess", ["lib/repository.ts", "lib/supabase.ts", "lib/search.ts", "lib/query.ts"]),
        ("Live &\nexternal", ["lib/liveNewsService.ts", "lib/sections.ts", "lib/externalSearch.ts"]),
        ("Scoring", ["lib/scoring.ts", "lib/clustering.ts"]),
        ("Reports", ["lib/pdfReportGenerator.ts"]),
        ("Pages", ["app/page.tsx (front page)", "app/section/[slug]", "app/article/[id]", "app/search",
                   "app/compare", "app/analytics"]),
        ("API\nroutes", ["app/api/articles", "app/api/article/[id]", "app/api/groups", "app/api/analytics",
                         "app/api/search/external", "app/api/auth/profile"]),
        ("Components", ["NameAuthModal, NewsCard", "DimensionRadarChart", "ReportDownload",
                        "CrossSourceView", "DashboardAnalytics"]),
    ]

    def column(x0, title, rows):
        head = box(s, x0, 82, 296, 40, title.split("\n"), 12.5, fill="#e4e4e4", bold_first=True)
        spine = x0 + 10
        y = 136
        last_mid = None
        for name, files in rows:
            h = max(28, len(files) * 15 + 9)
            names = name.split("\n")
            box(s, x0 + 22, y, 84, h, names, 12)
            s.rect(x0 + 116, y, 180, h, r=3, fill="white")
            for i, f in enumerate(files):
                s.text(x0 + 122, y + 17 + i * 15, f, MIN + 0.5, anchor="start")
            s.line(spine, y + h / 2, x0 + 22, y + h / 2)
            s.line(x0 + 106, y + h / 2, x0 + 116, y + h / 2)
            last_mid = y + h / 2
            y += h + 9
        s.line(spine, head.bottom, spine, last_mid)
        return head, y

    hb, yb = column(8, "Backend (backend/)\nPython + FastAPI", backend)
    hf, yf = column(316, "Frontend (frontend/src/)\nNext.js + TypeScript", frontend)
    s.line(310, root.bottom, 310, 66)
    s.line(hb.cx, 66, hf.cx, 66)
    s.line(hb.cx, 66, hb.cx, hb.top)
    s.line(hf.cx, 66, hf.cx, hf.top)
    ys = yb + 20
    sh = box(s, 30, ys, 250, 52, ["Shared: shared/scoring_vectors.json", "parity vectors used by the Python", "and TypeScript tests"], MIN + 0.5)
    # the shared node hangs from the root through the gap between the columns
    s.path([(310, 66), (310, ys + 26), (sh.right, ys + 26)])
    s.h = max(yf, ys + 52) + 10
    s.save("modules")


# ─── 3.3 Architecture ───────────────────────────────────────────────────────────────────────

def architecture():
    s = SVG(W, 850)
    br = box(s, 10, 14, 290, 54, ["Reader's web browser", "React UI · Recharts · jsPDF (browser PDF)"], 12, bold_first=True)
    ac = box(s, 400, 14, 210, 54, ["API client", "Swagger UI (/docs), curl"], 12, bold_first=True)
    # Next.js server
    nx = s.rect(10, 150, 290, 290, r=6, fill="#f7f7f7", sw=1.4)
    s.text(155, 172, "Next.js 16 server (Node.js)", 13, weight="bold")
    for i, t in enumerate([["Pages (server-rendered React)"], ["Next.js API routes (/api/*)"],
                           ["repository.ts", "getEdition · search · analytics"],
                           ["liveNewsService.ts", "externalSearch.ts"], ["scoring.ts · clustering.ts", "(same rules in TypeScript)"]]):
        y = [186, 224, 262, 314, 366][i]
        box(s, 24, y, 262, 30 if len(t) == 1 else 44, t, 12, fill="white", r=3)
    # FastAPI backend
    fx = s.rect(320, 150, 290, 290, r=6, fill="#f7f7f7", sw=1.4)
    s.text(465, 172, "FastAPI backend (Python)", 13, weight="bold")
    for i, t in enumerate([["main.py · api/router.py", "(/api and /api/v1)"], ["scheduler.py (every 30 min)", "→ rss_fetcher.py"],
                           ["analysis_pipeline.py"], ["dimension_service · ai_service", "clustering_service"],
                           ["db_service.py · report_service.py"]]):
        y = [186, 238, 290, 328, 380][i]
        box(s, 334, y, 262, 30 if len(t) == 1 else 44, t, 12, fill="white", r=3)
    # browser <-> next.js
    s.line(120, br.bottom, 120, nx.top, end="solid", start="solid")
    lab(s, 127, 104, "HTTPS: pages,\n/api/* routes")
    # browser -> FastAPI, optional server PDF
    s.path([(br.right, 41), (350, 41), (350, fx.top)], end="solid", dash=True)
    lab(s, 356, 92, "GET /api/v1/report/{id}\n(optional server PDF)")
    # API client -> FastAPI
    s.line(560, ac.bottom, 560, fx.top, end="solid")
    lab(s, 566, 135, "REST")
    # bottom row
    by = 600
    ext = box(s, 10, by, 140, 96, ["External news", "live RSS (31 URLs)", "Google News RSS", "GNews · GDELT"], 12, bold_first=True)
    db = box(s, 165, by, 205, 96, ["Supabase", "(PostgreSQL)", "articles · named_visitors", "user_profiles (unused)", "Row Level Security"], 12, bold_first=True)
    rss = box(s, 385, by, 105, 96, ["Publisher", "RSS feeds", "(11 feeds)"], 12, bold_first=True)
    hf = box(s, 505, by, 105, 96, ["Hugging Face", "Hub", "(model weights,", "first use)"], 12, bold_first=True)
    s.line(60, nx.bottom, 60, by, end="solid")
    lab(s, 66, 470, "fallback\nwhen the DB\nis empty;\nexternal\nsearch")
    s.line(230, nx.bottom, 230, by, end="solid")
    lab(s, 236, 470, "SELECT\n(anon key):\n500 rows,\n60 s cache;\nINSERT\nnamed_visitors")
    s.line(345, fx.bottom, 345, by, end="solid")
    lab(s, 351, 470, "SELECT /\nINSERT /\nUPDATE\n(service-\nrole key)")
    s.line(437, fx.bottom, 437, by, end="solid")
    lab(s, 443, 470, "fetch\nfeeds")
    s.line(557, fx.bottom, 557, by, end="solid")
    lab(s, 563, 470, "download\nweights")
    note(s, 10, 730, 600, ["Solid arrows show the direction of each request; the dashed arrow is used only when",
                           "NEXT_PUBLIC_API_URL is set. Pages are rendered from data that Next.js reads directly",
                           "from Supabase; readers reach FastAPI only for the optional server-side PDF report."])
    s.h = 800
    s.save("architecture")


# ─── 3.4 Class diagram ──────────────────────────────────────────────────────────────────────

def class_diagram():
    s = SVG(W, 700)
    src = uml(s, 8, 20, 165, "«conceptual» Source", ["- name : String", "- feedUrl : String", "- category : String"],
              ["fetch_articles()"])
    art = uml(s, 236, 20, 166, "Article", ["- id : UUID", "- title : String {unique}", "- sourceUrl : String",
                                         "- excerpt : String", "- category : String", "- publishedAt : DateTime"],
              ["analyze_article()"])
    grp = uml(s, 452, 20, 160, "ArticleGroup", ["- groupId : String", "- eventTitle : String", "- publishers : String[*]"],
              ["cluster_articles()"])
    yy = 64
    s.line(src.right, yy, art.left, yy)
    s.text(src.right + 5, yy - 5, "1", MIN, anchor="start"); s.text(art.left - 5, yy - 5, "0..*", MIN, anchor="end")
    lab(s, (src.right + art.left) / 2, yy + 16, "publishes", anchor="middle")
    s.line(art.right, yy, grp.left, yy)
    s.text(art.right + 5, yy - 5, "2..*", MIN, anchor="start"); s.text(grp.left - 5, yy - 5, "0..1", MIN, anchor="end")
    lab(s, (art.right + grp.left) / 2, yy + 16, "groups", anchor="middle")
    # Report (dependency on Article)
    rep = uml(s, 452, 150, 160, "Report", ["- articleId : UUID", "- format : A4 PDF"], ["build_article_report()"])
    s.line(rep.left, rep.y + 50, art.right, rep.y + 50, dash=True, end="open")
    lab(s, (rep.left + art.right) / 2, rep.y + 44, "«use»", anchor="middle")
    # composition parts
    y2 = 290
    bus = 262
    cred = uml(s, 8, y2, 206, "CredibilityResult", ["- riskScore : float [0..1]", "- label : RiskLabel [0..1]",
                                                     "- classifierFakeScore : float [0..1]", "- classifierConfidence : float [0..1]",
                                                     "- needsVerification : Boolean", "- status : String"])
    dim = uml(s, 226, y2, 186, "DimensionAnalysis", ["- sentiment : int [0..1]", "- bias : int [0..1]",
                                                      "- objectivity : int [0..1]", "- readability : int [0..1]",
                                                      "- propaganda : int [0..1]", "- headlineAccuracy : int [0..1]",
                                                      "- sourceCredibility : int [0..1]", "- contentQuality : int [0..1]",
                                                      "- explanations : Map"], ["rule_risk()"])
    sen = uml(s, 452, y2, 160, "SentimentResult", ["- label : Sentiment", "- score : int"])
    summ = uml(s, 452, 420, 160, "Summary", ["- text : String", "- method : String"])
    s.line(art.cx, art.bottom, art.cx, bus, start="diamond")
    s.text(art.cx + 8, art.bottom + 20, "1", MIN, anchor="start")
    s.line(cred.cx, bus, 432, bus)
    for b, mult in ((cred, "1"), (dim, "1")):
        s.line(b.cx, bus, b.cx, b.top)
        s.text(b.cx + 6, b.top - 6, mult, MIN, anchor="start")
    s.path([(432, bus), (sen.cx, bus), (sen.cx, sen.top)])
    s.text(sen.cx + 6, sen.top - 6, "1", MIN, anchor="start")
    s.path([(432, bus), (432, summ.y + 40), (summ.left, summ.y + 40)])
    s.text(summ.left - 4, summ.y + 34, "0..1", MIN, anchor="end")
    note(s, 8, 520, 604, [
        "Operations are module-level Python functions (e.g. analysis_pipeline.analyze_article), not methods.",
        "Article, its result parts, Summary (extractive) and groupId are columns of the single articles",
        "table; the eight scores and their explanations are one JSONB column. Source is conceptual",
        "(RSS_SOURCES dictionary and source_domain column); Report is streamed, never stored.",
        "[0..1] marks a value that may be missing (not measured); it is never replaced by a default."])
    s.h = 620
    s.save("class")


# ─── 3.5 Use-case diagram ───────────────────────────────────────────────────────────────────

def use_case():
    s = SVG(W, 750)
    s.rect(100, 14, 412, 724, fill="white", sw=1.4)
    s.text(306, 38, "AI-Powered News Aggregator", 14, weight="bold")
    base = (428, 165)
    s.ellipse(*base, 76, 26, "Run ingestion\ncycle", size=12)
    inc = ["Collect RSS feeds", "Remove duplicates", "Analyse articles\n(risk, sentiment, 8 dims)", "Group cross-source\nevents"]
    for i, u in enumerate(inc):
        y = 78 + i * 60
        s.ellipse(210, y, 96, 25, u, size=12)
        s.line(base[0] - 76, base[1], 306, y, dash=True, end="open")
    lab(s, 330, 98, "«include»", anchor="middle", bg=True)
    lab(s, 330, 248, "«include»", anchor="middle", bg=True)
    ax, ay = s.actor(566, 70, "Scheduler\n(every 30 min)")
    s.line(ax - 18, ay, base[0] + 76, base[1])
    reader_uc = ["Register display name", "View front page", "Browse sections", "Search & filter articles",
                 "View article analysis", "Compare coverage", "View analytics", "Download PDF report"]
    ys = []
    for i, u in enumerate(reader_uc):
        y = 350 + i * 48
        ys.append(y)
        s.ellipse(222, y, 100, 20, u, size=12)
    rx, ry = s.actor(46, 470, "Reader")
    for y in ys:
        s.line(rx + 18, ry, 122, y)
    ext = (420, 535)
    s.ellipse(*ext, 86, 27, "Search external\nnews (Google News,\nGNews, GDELT)", size=MIN)
    s.line(ext[0] - 60, ext[1] - 20, 300, ys[3] + 14, dash=True, end="open")
    lab(s, 336, 500, "«extend»", anchor="start", bg=True)
    an = (420, 660)
    s.ellipse(*an, 86, 26, "Analyse custom text\n(POST /api/analyze)", size=MIN)
    ox, oy = s.actor(566, 400, "Operator /\nAPI client")
    s.line(ox - 18, oy, base[0] + 40, base[1] + 22)
    lab(s, 522, 290, "POST /api/ingest\n(ingest token)")
    s.line(ox - 18, oy, an[0] + 60, an[1] - 19)
    s.save("usecase")


# ─── 3.6 Sequence diagram ───────────────────────────────────────────────────────────────────

def sequence():
    s = SVG(W, 870)
    X = {"reader": 56, "next": 220, "db": 390, "api": 545}
    s.actor(X["reader"], 14, "")
    s.text(X["reader"], 100, "Reader (browser)", 12, weight="bold")
    for key, name in (("next", "Next.js server"), ("db", "Supabase"), ("api", "FastAPI backend")):
        s.rect(X[key] - 64, 60, 128, 34, r=4)
        s.text(X[key], 82, name, 12.5, weight="bold")
    for k, x in X.items():
        s.line(x, 108 if k == "reader" else 94, x, 858, dash=True, sw=0.9)

    def act(x, y1, y2):
        s.rect(x - 6, y1, 12, y2 - y1, fill="white", sw=1.1)

    def msg(x1, x2, y, text, ret=False):
        off = 6 if x2 > x1 else -6
        s.line(x1 + off, y, x2 - off, y, dash=ret, end="open" if ret else "solid")
        lines = text.split("\n")
        for i, t in enumerate(lines):
            s.text((x1 + x2) / 2, y - 6 - (len(lines) - 1 - i) * 14, t, MIN, style="italic", bg=True)

    def self_msg(x, y, text, h=18):
        s.path([(x + 6, y), (x + 36, y), (x + 36, y + h), (x + 12, y + h)], end="solid")
        for i, t in enumerate(text.split("\n")):
            s.text(x + 42, y + 8 + i * 14, t, MIN, anchor="start", style="italic", bg=True)

    def frame(x1, y1, x2, y2, guard, sep=None, guard2=None):
        s.rect(x1, y1, x2 - x1, y2 - y1, fill="none", sw=1.1)
        s.add(f"<polygon points='{x1},{y1} {x1 + 36},{y1} {x1 + 36},{y1 + 12} {x1 + 28},{y1 + 20} {x1},{y1 + 20}' fill='white' stroke='{INK}' stroke-width='1.1'/>")
        s.text(x1 + 16, y1 + 14, "alt", MIN + 0.5, weight="bold")
        for i, g in enumerate(guard.split("\n")):
            s.text(x1 + 44, y1 + 15 + i * 14, g, MIN, anchor="start", style="italic", bg=True)
        if sep:
            s.line(x1, sep, x2, sep, dash=True, sw=1)
            s.text(x1 + 8, sep + 15, guard2, MIN, anchor="start", style="italic", bg=True)

    act(X["reader"], 126, 840)
    act(X["next"], 140, 420)
    msg(X["reader"], X["next"], 140, "1: GET /article/{id}")
    frame(150, 160, 470, 350, "[edition cache older than 60 s]", 296, "[else]")
    act(X["db"], 236, 270)
    msg(X["next"], X["db"], 236, "2: select * from articles\norder by published_at desc\nlimit 500")
    msg(X["db"], X["next"], 268, "3: rows (≤ 500)", ret=True)
    self_msg(X["next"], 316, "3': reuse cached edition")
    self_msg(X["next"], 366, "4: find article by id;\ngroup and related reports", h=22)
    msg(X["next"], X["reader"], 414, "5: rendered article\npage (HTML)", ret=True)
    frame(14, 446, 608, 852, "[Download PDF report: backend URL set\nand article read from the database]", 750, "[Export in browser]")
    act(X["api"], 520, 712)
    msg(X["reader"], X["api"], 520, "6: GET /api/v1/report/{id}")
    act(X["db"], 568, 606)
    msg(X["api"], X["db"], 568, "7: get_article_by_id(id)")
    msg(X["db"], X["api"], 604, "8: article row", ret=True)
    s.path([(X["api"] + 6, 632), (X["api"] + 36, 632), (X["api"] + 36, 652), (X["api"] + 12, 652)], end="solid")
    s.text(X["api"] - 12, 660, "9: build_article_report()", MIN, anchor="end", style="italic", bg=True)
    msg(X["api"], X["reader"], 708, "10: application/pdf (attachment)", ret=True)
    self_msg(X["reader"], 786, "11: generateIntelligencePdf(article)\nwith jsPDF; file saved locally", h=22)
    s.save("sequence")


# ─── 3.7 Activity diagram (one ingestion run, fetch_and_store_job) ─────────────────────────

def activity():
    s = SVG(W, 880)
    cx, rx = 270, 500
    AW = 270

    def act(x, y, text, w=AW):
        lines = text.split("\n")
        h = 14 + 15 * len(lines)
        b = s.rect(x - w / 2, y, w, h, r=13)
        for i, l in enumerate(lines):
            s.text(x, y + h / 2 + 4 + (i - (len(lines) - 1) / 2) * 15, l, 12)
        return b

    def arrow(y1, y2, x=cx):
        s.line(x, y1, x, y2, end="open")

    def guard(x, y, t, anchor="start"):
        s.text(x, y, t, MIN, anchor=anchor)

    s.add(f"<circle cx='{cx}' cy='16' r='9' fill='{INK}'/>")
    lab(s, cx + 16, 20, "every 30 minutes")
    dl = s.diamond(cx, 52, 190, 36, "Previous run still running?", size=MIN); arrow(25, dl.top)
    s.line(dl.right, dl.cy, rx - 12, dl.cy, end="open"); guard(dl.right + 6, dl.cy - 5, "[yes]")
    lab(s, rx - 12, dl.cy + 22, "skip this trigger", anchor="middle")
    s.add(f"<circle cx='{rx}' cy='{dl.cy}' r='11' fill='white' stroke='{INK}' stroke-width='1.4'/>"
          f"<path d='M{rx - 7.8},{dl.cy - 7.8} L{rx + 7.8},{dl.cy + 7.8} M{rx - 7.8},{dl.cy + 7.8} L{rx + 7.8},{dl.cy - 7.8}' stroke='{INK}' stroke-width='1.4'/>")
    guard(cx + 7, dl.bottom + 12, "[no]")
    mark = len(s.items)
    m1 = s.diamond(cx, 48, 22, 22); arrow(dl.bottom - 50, m1.top)
    a = act(cx, 72, "Download next RSS feed (15 s timeout)"); arrow(m1.bottom, a.top)
    d1 = s.diamond(cx, 136, 140, 36, "Request failed?", size=12); arrow(a.bottom, d1.top)
    b = act(rx, d1.cy - 22, "Log failure and\nrecord feed name", 170)
    s.line(d1.right, d1.cy, b.left, d1.cy, end="open"); guard(d1.right + 6, d1.cy - 5, "[yes]")
    c = act(cx, 170, "Parse entries, clean HTML, UTC date"); arrow(d1.bottom, c.top)
    guard(cx + 7, d1.bottom + 12, "[no]")
    m2 = s.diamond(cx, 222, 22, 22); arrow(c.bottom, m2.top)
    s.path([(rx, b.bottom), (rx, m2.cy), (m2.right, m2.cy)], end="open")
    d2 = s.diamond(cx, 264, 130, 36, "More feeds?", size=12); arrow(m2.bottom, d2.top)
    s.path([(d2.left, d2.cy), (40, d2.cy), (40, m1.cy), (m1.left, m1.cy)], end="open")
    guard(d2.left - 6, d2.cy - 5, "[yes]", "end")
    e = act(cx, 298, "Remove repeats in batch (title, URL)"); arrow(d2.bottom, e.top)
    guard(cx + 7, d2.bottom + 12, "[no]")
    m3 = s.diamond(cx, 350, 22, 22); arrow(e.bottom, m3.top)
    d3 = s.diamond(cx, 394, 160, 36, "Already in database?", size=12); arrow(m3.bottom, d3.top)
    sk = act(rx, d3.cy - 14.5, "Skip (duplicate)", 150)
    s.line(d3.right, d3.cy, sk.left, d3.cy, end="open"); guard(d3.right + 6, d3.cy - 5, "[yes]")
    f = act(cx, 428, "Score 8 dimensions (rules);\nrun models if available"); arrow(d3.bottom, f.top)
    guard(cx + 7, d3.bottom + 12, "[no]")
    d4 = s.diamond(cx, 510, 210, 50, "Scored dimensions carry\n≥ 65 % of the risk weight?", size=MIN); arrow(f.bottom, d4.top)
    g1 = act(140, 550, "Compute risk;\nLow / Moderate / High", 190)
    g2 = act(410, 550, "No risk score;\nlabel = not assessed", 180)
    s.path([(d4.left, d4.cy), (140, d4.cy), (140, g1.top)], end="open"); guard(d4.left - 6, d4.cy - 5, "[yes]", "end")
    s.path([(d4.right, d4.cy), (410, d4.cy), (410, g2.top)], end="open"); guard(d4.right + 6, d4.cy - 5, "[no]")
    m4 = s.diamond(cx, 616, 22, 22)
    s.path([(140, g1.bottom), (140, m4.cy), (m4.left, m4.cy)], end="open")
    s.path([(410, g2.bottom), (410, m4.cy), (m4.right, m4.cy)], end="open")
    h = act(cx, 642, "Set Needs Verification if any rule applies *", 300); arrow(m4.bottom, h.top)
    i = act(cx, 686, "Insert article into Supabase\n(error: log, count as failed)"); arrow(h.bottom, i.top)
    m5 = s.diamond(cx, 746, 22, 22); arrow(i.bottom, m5.top)
    # skip path routed outside the "not assessed" branch, so no line crosses an action
    s.path([(sk.right, sk.cy), (606, sk.cy), (606, m5.cy), (m5.right, m5.cy)], end="open")
    d5 = s.diamond(cx, 790, 130, 36, "More articles?", size=12); arrow(m5.bottom, d5.top)
    s.path([(d5.left, d5.cy), (18, d5.cy), (18, m3.cy), (m3.left, m3.cy)], end="open")
    guard(d5.left - 6, d5.cy - 5, "[yes]", "end")
    j = act(rx, d5.cy - 22, "Re-group articles of the\nlast 48 hours (TF-IDF)", 180)
    s.line(d5.right, d5.cy, j.left, d5.cy, end="open")
    guard(d5.right + 6, d5.cy - 5, "[no]")
    s.line(j.cx, j.bottom, j.cx, 830, end="open")
    final_node(s, j.cx, 842)
    # shift everything after the lock decision down by 52 units
    s.items[mark:] = ["<g transform='translate(0,52)'>"] + s.items[mark:] + ["</g>"]
    s.text(8, 920, "* no score; score 0.40–0.60; excerpt < 150 characters; classifier confidence < 0.60;", MIN, anchor="start", style="italic")
    s.text(8, 934, "  or classifier score and rule risk differ by ≥ 0.50", MIN, anchor="start", style="italic")
    s.h = 948
    s.save("activity")


# ─── 3.8 Component diagram (UML 2) ──────────────────────────────────────────────────────────

def component_diagram():
    s = SVG(W, 860)
    cw, ch = 176, 54
    cols = [22, 222, 422]

    def dep(pts):
        s.path(pts, dash=True, end="open")

    # Next.js subsystem with its provided interface on top
    ball(s, 310, 18)
    s.line(310, 26, 310, 46)
    lab(s, 324, 22, "HTTP pages and /api/* routes")
    nb = s.rect(8, 46, 604, 236, fill="#f7f7f7", sw=1.4)
    s.text(310, 66, "«subsystem» Next.js web application", 13, weight="bold")
    r1, r2 = 84, 180
    pdf = component(s, cols[0], r1, cw, ch, ["pdfReport-", "Generator (jsPDF)"])
    pages = component(s, cols[1], r1, cw, ch, ["Pages & UI", "React components"])
    routes = component(s, cols[2], r1, cw, ch, ["API routes", "app/api/*"])
    live = component(s, cols[0], r2, cw, ch, ["liveNewsService", "externalSearch"])
    repo = component(s, cols[1], r2, cw, ch, ["repository.ts", "data access"])
    score = component(s, cols[2], r2, cw, ch, ["scoring.ts", "clustering.ts"])
    dep([(pages.left, pages.cy), (pdf.right, pages.cy)])
    dep([(290, pages.bottom), (290, repo.top)])
    dep([(470, routes.bottom), (470, 159), (340, 159), (340, repo.top)])
    dep([(repo.left, repo.cy), (live.right, repo.cy)])
    dep([(repo.right, repo.cy), (score.left, repo.cy)])
    dep([(110, live.bottom), (110, 262), (510, 262), (510, score.bottom)])

    # Supabase between the subsystems: provided interface (ball), required by both (sockets)
    sb = s.rect(190, 316, 220, 66, fill="white", sw=1.3)
    comp_icon(s, 390, 321)
    s.text(295, 334, "«component» «database»", MIN, style="italic")
    s.text(295, 352, "Supabase PostgreSQL", 12.5, weight="bold")
    s.text(295, 369, "articles · named_visitors", MIN + 0.5)
    # Next.js (read) and FastAPI (write) each require Supabase's PostgREST interface through their own
    # assembly connector; no line joins the two subsystems directly.
    bx, by = 120, 349
    ball(s, bx, by)
    s.line(bx + 8, by, sb.left, by)
    lab(s, bx - 14, by + 26, "PostgREST", anchor="middle", size=MIN)
    s.line(bx, nb.bottom, bx, by - 14)
    s.add(f"<path d='M{bx - 14},{by - 4} A14,14 0 0 1 {bx + 14},{by - 4}' fill='none' stroke='{INK}' stroke-width='1.3'/>")
    lab(s, bx - 8, 306, "read (anon key)", anchor="end")
    b2x, b2y = 295, 392
    s.line(b2x, sb.bottom, b2x, b2y - 8)
    ball(s, b2x, b2y)
    s.add(f"<path d='M{b2x - 14},{b2y + 4} A14,14 0 0 0 {b2x + 14},{b2y + 4}' fill='none' stroke='{INK}' stroke-width='1.3'/>")
    s.line(b2x, b2y + 14, b2x, 412)
    lab(s, b2x + 20, 398, "PostgREST")
    lab(s, b2x - 22, 405, "write (service-role key)", anchor="end")
    ext = box(s, 450, 316, 162, 66, ["External news", "live RSS · Google News", "GNews · GDELT"], MIN + 0.5, fill="white", r=0, bold_first=True)
    dep([(531, nb.bottom), (531, ext.top)])
    lab(s, 537, 304, "«use»")

    # FastAPI subsystem
    fb = s.rect(8, 412, 604, 340, fill="#f7f7f7", sw=1.4)
    s.text(310, 432, "«subsystem» FastAPI backend", 13, weight="bold")
    q1, q2, q3 = 450, 556, 662
    report = component(s, cols[0], q1, cw, ch, ["report_service", "ReportLab PDF"])
    router = component(s, cols[1], q1, cw, ch, ["router.py", "REST endpoints"])
    sched = component(s, cols[2], q1, cw, ch, ["scheduler.py", "APScheduler"])
    pipe = component(s, cols[0], q2, cw, ch, ["analysis_", "pipeline.py"])
    dbs = component(s, cols[1], q2, cw, ch, ["db_service.py", "storage"])
    rssc = component(s, cols[2], q2, cw, ch, ["rss_fetcher.py", "feeds, cleaning"])
    dim = component(s, cols[0], q3, cw, ch, ["dimension_service", "ai_service"])
    clu = component(s, cols[1], q3, cw, ch, ["clustering_", "service.py"])
    dep([(router.left, router.cy), (report.right, router.cy)])
    dep([(250, router.bottom), (250, 532), (110, 532), (110, pipe.top)])
    dep([(320, router.bottom), (320, dbs.top)])
    dep([(sched.cx, sched.bottom), (sched.cx, rssc.top)])
    dep([(450, sched.bottom), (450, 532), (370, 532), (370, dbs.top)])
    dep([(dbs.left, dbs.cy), (pipe.right, dbs.cy)])
    dep([(pipe.cx - 5, pipe.bottom), (pipe.cx - 5, dim.top)])
    dep([(dbs.cx - 5, dbs.bottom), (dbs.cx - 5, clu.top)])
    dep([(dbs.right, dbs.cy + 14), (rssc.left, dbs.cy + 14)])
    # provided REST interface at the bottom of the FastAPI subsystem
    ball(s, 310, 788)
    s.line(310, fb.bottom, 310, 780)
    lab(s, 310, 814, "REST API\n(/api, /api/v1)", anchor="middle")
    hf = box(s, 8, 784, 200, 54, ["Hugging Face models", "(transformers)"], MIN + 0.5, fill="white", r=0, bold_first=True)
    rss = box(s, 412, 784, 200, 54, ["Publisher RSS feeds", "(11 feeds)"], MIN + 0.5, fill="white", r=0, bold_first=True)
    dep([(dim.cx - 5, dim.bottom), (dim.cx - 5, hf.top)])
    dep([(rssc.cx - 5, rssc.bottom), (rssc.cx - 5, rss.top)])
    lab(s, dim.cx + 2, 776, "«use»")
    lab(s, rssc.cx + 2, 776, "«use»")
    s.text(8, 856, "Dashed arrows: «use» dependencies. Ball: provided interface; socket: required interface.", MIN, anchor="start", style="italic")
    s.h = 864
    s.save("component")


# ─── 3.9 Deployment diagram (UML 2) ─────────────────────────────────────────────────────────

def deployment():
    s = SVG(W, 800)
    dev = node3d(s, 150, 24, 300, 118, "Reader's computer or phone", "«device»")
    inner(s, 172, 64, 256, 62, "«executionEnvironment»", ["Web browser", "React UI · Recharts · jsPDF report"])
    nx = node3d(s, 8, 240, 290, 236, "Next.js server")
    inner(s, 22, 280, 262, 182, "«executionEnvironment»", ["Node.js 20 or later"])
    inner(s, 34, 330, 238, 118, "«artifact»", ["frontend", "(next build / next start)", "env: NEXT_PUBLIC_SUPABASE_URL,",
                                               "NEXT_PUBLIC_SUPABASE_ANON_KEY,", "NEXT_PUBLIC_API_URL (optional)"],
          fill="white", icon=True)
    be = node3d(s, 312, 240, 290, 236, "Backend server or container")
    inner(s, 326, 280, 262, 182, "«executionEnvironment»", ["Python 3.10+ · Uvicorn", "optional Dockerfile:",
                                                            "python:3.10-slim, port 7860"])
    inner(s, 338, 358, 238, 92, "«artifact»", ["backend", "(main.py, services, scheduler)", "env: SUPABASE_URL,",
                                               "SUPABASE_SERVICE_ROLE_KEY"], fill="white", icon=True)
    # bottom row
    yb = 620
    ns = node3d(s, 8, yb, 140, 118, "News sources")
    for k, t in enumerate(["live RSS (31)", "Google News", "GNews · GDELT"]):
        s.text(78, yb + 58 + k * 15, t, MIN + 0.5)
    sp = node3d(s, 164, yb, 196, 118, "Supabase cloud", "«cloud service»")
    s.rect(176, yb + 44, 172, 64, fill="white", sw=1.1)
    s.text(262, yb + 60, "«database» PostgreSQL", MIN, style="italic")
    s.text(262, yb + 77, "articles, named_visitors,", MIN + 0.5)
    s.text(262, yb + 93, "user_profiles (unused)", MIN + 0.5)
    rs = node3d(s, 376, yb, 104, 118, "Publisher\nRSS servers")
    s.text(428, yb + 82, "(11 backend", MIN + 0.5)
    s.text(428, yb + 97, "feeds)", MIN + 0.5)
    hf = node3d(s, 496, yb, 106, 118, "Hugging\nFace Hub", "«cloud service»")
    s.text(549, yb + 82, "model weights", MIN + 0.5)
    s.text(549, yb + 97, "(first use)", MIN + 0.5)
    # communication paths
    s.line(200, dev.bottom, 200, nx.top - 10)
    lab(s, 206, 196, "HTTPS")
    s.line(400, dev.bottom, 400, be.top - 10, dash=True)
    lab(s, 406, 186, "HTTPS (optional\nserver PDF)")
    s.line(70, nx.bottom, 70, yb - 10)
    lab(s, 76, 552, "HTTPS")
    s.line(230, nx.bottom, 230, yb - 10)
    lab(s, 236, 520, "HTTPS\n(anon key)")
    s.line(330, be.bottom, 330, yb - 10)
    lab(s, 336, 560, "HTTPS\n(service-\nrole key)")
    s.line(428, be.bottom, 428, yb - 10)
    lab(s, 434, 520, "HTTP(S)")
    s.line(549, be.bottom, 549, yb - 10)
    lab(s, 555, 560, "HTTPS")
    s.text(8, 766, "Deployment architecture supported by the code (a Dockerfile exists for the backend);", MIN, anchor="start", style="italic")
    s.text(8, 780, "the project was run locally during development and no production deployment is claimed.", MIN, anchor="start", style="italic")
    s.h = 790
    s.save("deployment")


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    for fn in (modules, architecture, class_diagram, use_case, sequence, activity, component_diagram, deployment):
        fn()
    print("written:", sorted(p.name for p in OUT.glob("*.svg")))
