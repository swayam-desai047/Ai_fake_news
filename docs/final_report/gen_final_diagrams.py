"""Diagrams for the final project report (docs/final_report/diagrams/*.svg).

Reuses the SVG helpers of docs/report/gen_diagrams.py. Every diagram is drawn from the code:
see the module docstrings referenced in the report (frontend/src/lib/repository.ts, backend/main.py ...).
Run:  python3 docs/final_report/gen_final_diagrams.py   then  node docs/final_report/render_png.js
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "report"))
import gen_diagrams as gd  # noqa: E402
from gen_diagrams import SVG, INK, FILL  # noqa: E402

OUT = HERE / "diagrams"
OUT.mkdir(exist_ok=True)
gd.OUT = OUT  # the helpers' save() writes into gd.OUT


# ─── extra drawing helpers ──────────────────────────────────────────────────────────────────

def mtext(s, x, y, lines, size=12, anchor="middle", weight="normal", style="normal", lh=None):
    lh = lh or size + 3
    for i, l in enumerate(lines):
        s.text(x, y + i * lh, l, size, anchor=anchor, weight=weight, style=style)


def box(s, x, y, w, h, lines, size=12, fill=FILL, r=5, bold_first=False, dash=False):
    b = s.rect(x, y, w, h, r=r, fill=fill, dash=dash)
    lh = size + 3
    top = y + h / 2 - (len(lines) - 1) * lh / 2 + size * 0.35
    for i, l in enumerate(lines):
        s.text(x + w / 2, top + i * lh, l, size, weight="bold" if (bold_first and i == 0) else "normal")
    return b


def circle_proc(s, cx, cy, r, lines, size=12):
    s.add(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{FILL}' stroke='{INK}' stroke-width='1.3'/>")
    lh = size + 3
    top = cy - (len(lines) - 1) * lh / 2 + size * 0.35
    for i, l in enumerate(lines):
        s.text(cx, top + i * lh, l, size, weight="bold" if i == 0 else "normal")


def store(s, x, y, w, h, sid, name, size=12):
    """DFD data store: open-ended box with an id compartment."""
    s.line(x, y, x + w, y, sw=1.3)
    s.line(x, y + h, x + w, y + h, sw=1.3)
    s.line(x, y, x, y + h, sw=1.3)
    s.line(x + 34, y, x + 34, y + h, sw=1.1)
    s.text(x + 17, y + h / 2 + 4, sid, size, weight="bold")
    s.text(x + 34 + (w - 34) / 2, y + h / 2 + 4, name, size)


def label(s, x, y, txt, size=11, anchor="middle", style="italic"):
    s.text(x, y, txt, size, anchor=anchor, style=style, bg=True)


def comp_icon(s, x, y):
    """UML 2 component icon (top-right corner of a component box)."""
    s.add(f"<rect x='{x}' y='{y}' width='14' height='16' fill='white' stroke='{INK}' stroke-width='1'/>"
          f"<rect x='{x - 4}' y='{y + 3}' width='8' height='3.5' fill='white' stroke='{INK}' stroke-width='1'/>"
          f"<rect x='{x - 4}' y='{y + 9.5}' width='8' height='3.5' fill='white' stroke='{INK}' stroke-width='1'/>")


def component(s, x, y, w, h, lines, size=11.5, stereo="«component»"):
    b = s.rect(x, y, w, h, r=0, fill="white", sw=1.2)
    comp_icon(s, x + w - 20, y + 5)
    s.text(x + w / 2 - 6, y + 14, stereo, 10, style="italic")
    lh = size + 2
    for i, l in enumerate(lines):
        s.text(x + w / 2 - 6, y + 29 + i * lh, l, size, weight="bold" if i == 0 else "normal")
    return b


def node3d(s, x, y, w, h, title, stereo="«device»", d=12, size=12):
    s.add(f"<polygon points='{x},{y} {x + d},{y - d} {x + w + d},{y - d} {x + w},{y}' fill='#e6e6e6' stroke='{INK}' stroke-width='1.2'/>")
    s.add(f"<polygon points='{x + w},{y} {x + w + d},{y - d} {x + w + d},{y + h - d} {x + w},{y + h}' fill='#d9d9d9' stroke='{INK}' stroke-width='1.2'/>")
    s.rect(x, y, w, h, fill=FILL, sw=1.3)
    s.text(x + w / 2, y + 16, stereo, 10.5, style="italic")
    s.text(x + w / 2, y + 31, title, size, weight="bold")


def artifact(s, x, y, w, h, lines, size=11, stereo="«artifact»"):
    s.rect(x, y, w, h, fill="white", sw=1.1)
    # document icon
    ix, iy = x + w - 16, y + 5
    s.add(f"<path d='M{ix},{iy} h7 l4,4 v10 h-11 z M{ix + 7},{iy} v4 h4' fill='white' stroke='{INK}' stroke-width='0.9'/>")
    s.text(x + w / 2 - 6, y + 13, stereo, 9.5, style="italic")
    for i, l in enumerate(lines):
        s.text(x + w / 2 - 6, y + 27 + i * (size + 2), l, size, weight="bold" if i == 0 else "normal")


def envbox(s, x, y, w, h, lines, size=11):
    s.rect(x, y, w, h, fill="#fafafa", sw=1.1, dash=False)
    s.text(x + w / 2, y + 13, "«executionEnvironment»", 9.5, style="italic")
    for i, l in enumerate(lines):
        s.text(x + w / 2, y + 27 + i * (size + 2), l, size, weight="bold" if i == 0 else "normal")


def note(s, x, y, w, h, lines, size=11):
    f = 12
    s.add(f"<path d='M{x},{y} H{x + w - f} L{x + w},{y + f} V{y + h} H{x} Z' fill='#fffff2' stroke='{INK}' stroke-width='1.1'/>"
          f"<path d='M{x + w - f},{y} V{y + f} H{x + w}' fill='none' stroke='{INK}' stroke-width='1.1'/>")
    for i, l in enumerate(lines):
        s.text(x + 8, y + 17 + i * (size + 3), l, size, anchor="start")


# ─── 3.2 Module hierarchy ───────────────────────────────────────────────────────────────────

def modules():
    s = SVG(780, 830)
    root = box(s, 270, 12, 240, 40, ["AI News Aggregator"], 15)
    backend = [
        ("Collection", ["services/rss_fetcher.py", "services/scheduler.py"]),
        ("Analysis", ["services/dimension_service.py", "services/ai_service.py", "services/analysis_pipeline.py"]),
        ("Grouping", ["services/clustering_service.py"]),
        ("Storage", ["services/db_service.py", "db/supabase.py", "db/*.sql (schema, migrations)"]),
        ("API & Reports", ["main.py", "api/router.py", "services/report_service.py"]),
        ("Scripts", ["scripts/reanalyze.py", "scripts/validate_models.py"]),
    ]
    frontend = [
        ("Data access", ["lib/repository.ts", "lib/supabase.ts", "lib/search.ts", "lib/query.ts"]),
        ("Live & external", ["lib/liveNewsService.ts", "lib/sections.ts", "lib/externalSearch.ts"]),
        ("Scoring", ["lib/scoring.ts", "lib/clustering.ts"]),
        ("Reports", ["lib/pdfReportGenerator.ts"]),
        ("Pages", ["app/page.tsx (front page)", "app/section/[slug]", "app/article/[id]",
                   "app/search, app/compare, app/analytics"]),
        ("API routes", ["app/api/articles, api/article/[id]", "app/api/groups, api/analytics",
                        "app/api/search/external", "app/api/auth/profile"]),
        ("Components", ["NameAuthModal, NewsCard, ...", "DimensionRadarChart, ReportDownload",
                        "CrossSourceView, DashboardAnalytics"]),
    ]

    def column(x0, title, rows):
        head = box(s, x0, 92, 360, 34, [title], 13.5, fill="#e4e4e4")
        spine = x0 + 14
        y = 142
        last_mid = None
        for name, files in rows:
            h = max(30, len(files) * 15 + 10)
            g = box(s, x0 + 28, y, 106, h, [name], 12)
            fb = s.rect(x0 + 150, y, 210, h, r=3, fill="white")
            for i, f in enumerate(files):
                s.text(x0 + 158, y + 17 + i * 15, f, 11.5, anchor="start")
            s.line(spine, y + h / 2, x0 + 28, y + h / 2)
            s.line(x0 + 134, y + h / 2, x0 + 150, y + h / 2)
            last_mid = y + h / 2
            y += h + 10
        s.line(spine, head.bottom, spine, last_mid)
        return head, y

    hb, yb = column(20, "Backend (backend/, Python + FastAPI)", backend)
    hf, yf = column(400, "Frontend (frontend/src/, Next.js + TypeScript)", frontend)
    s.line(390, root.bottom, 390, 72)
    s.line(hb.cx, 72, hf.cx, 72)
    s.line(hb.cx, 72, hb.cx, hb.top)
    s.line(hf.cx, 72, hf.cx, hf.top)
    ys = max(yb, yf) + 8
    sh = box(s, 250, ys, 280, 40, ["Shared: shared/scoring_vectors.json", "(parity vectors for Python and TypeScript tests)"], 11.5)
    # shared node hangs from the root through the gap between the two columns
    s.line(390, 72, 390, ys)
    s.h = ys + 52
    s.save("modules")


# ─── 3.3 Architecture ───────────────────────────────────────────────────────────────────────

def architecture():
    s = SVG(820, 600)
    box(s, 60, 20, 260, 56, ["Reader's web browser", "React UI · Recharts · jsPDF (browser PDF)"], 12, bold_first=True)
    box(s, 520, 20, 180, 56, ["API client", "Swagger /docs, curl"], 12, bold_first=True)
    nx = s.rect(20, 130, 340, 230, r=6, fill="#f7f7f7", sw=1.4)
    s.text(190, 151, "Next.js 16 server (Node.js)", 13.5, weight="bold")
    for i, t in enumerate(["Pages (server-rendered React)", "Next.js API routes (/api/*)",
                           "repository.ts (getEdition, search, analytics)",
                           "liveNewsService.ts · externalSearch.ts", "scoring.ts · clustering.ts (rules in TS)"]):
        box(s, 40, 164 + i * 38, 300, 30, [t], 12, fill="white", r=3)
    fx = s.rect(400, 130, 280, 230, r=6, fill="#f7f7f7", sw=1.4)
    s.text(540, 151, "FastAPI backend (Python)", 13.5, weight="bold")
    for i, t in enumerate(["main.py · router.py (/api, /api/v1)", "scheduler.py → rss_fetcher.py",
                           "analysis_pipeline.py", "dimension · ai · clustering services",
                           "db_service.py · report_service.py"]):
        box(s, 415, 164 + i * 38, 250, 30, [t], 12, fill="white", r=3)
    rss = box(s, 710, 150, 100, 84, ["Publisher", "RSS feeds", "(11 feeds,", "every 30 min)"], 11.5)
    hf = box(s, 710, 268, 100, 84, ["Hugging", "Face Hub", "(weights on", "first use)"], 11.5)
    s.line(fx.right, 192, rss.left, 192, end="solid")
    s.line(fx.right, 310, hf.left, 310, end="solid")
    db = box(s, 260, 450, 320, 70, ["Supabase (PostgreSQL)", "tables: articles, named_visitors,", "user_profiles (defined, unused) · RLS"], 12, bold_first=True)
    ext = box(s, 20, 450, 200, 84, ["External news (frontend)", "live publisher RSS (31 URLs)", "Google News RSS · GNews", "GDELT DOC 2.0"], 11.5, bold_first=True)
    # browser <-> next
    s.line(190, 76, 190, 130, end="solid", start="solid")
    s.text(197, 108, "HTTPS: pages, /api/*", 11, anchor="start", style="italic")
    # browser -> fastapi (optional PDF)
    s.path([(320, 48), (430, 48), (430, 130)], end="solid", dash=True)
    s.text(436, 96, "GET /api/v1/report/{id}", 11, anchor="start", style="italic")
    s.text(436, 111, "(optional server PDF)", 11, anchor="start", style="italic")
    # api client -> fastapi
    s.line(640, 76, 640, 130, end="solid")
    s.text(646, 104, "/api/analyze, ...", 11, anchor="start", style="italic")
    # next -> ext
    s.line(100, 360, 100, 450, end="solid")
    s.text(106, 393, "fallback when the", 11, anchor="start", style="italic")
    s.text(106, 407, "DB is empty; external", 11, anchor="start", style="italic")
    s.text(106, 421, "search", 11, anchor="start", style="italic")
    # next -> supabase
    s.line(320, 360, 320, 450, end="solid")
    s.text(326, 386, "SELECT (anon key)", 11, anchor="start", style="italic")
    s.text(326, 400, "500 rows, 60 s cache;", 11, anchor="start", style="italic")
    s.text(326, 414, "INSERT named_visitors", 11, anchor="start", style="italic")
    # fastapi -> supabase
    s.line(520, 360, 520, 450, end="solid")
    s.text(526, 393, "INSERT / UPDATE", 11, anchor="start", style="italic")
    s.text(526, 407, "(service-role key)", 11, anchor="start", style="italic")
    s.text(20, 575, "Solid arrows show the direction of each request; the dashed arrow is used only when NEXT_PUBLIC_API_URL is set.", 11, anchor="start", style="italic")
    s.text(20, 591, "Pages are rendered from data that Next.js reads directly from Supabase; FastAPI serves only the optional server PDF to readers.", 11, anchor="start", style="italic")
    s.save("architecture")


# ─── 3.3 Data flow diagrams ─────────────────────────────────────────────────────────────────

def dfd0():
    s = SVG(800, 470)
    circle_proc(s, 400, 235, 80, ["0", "AI-Powered", "News Aggregator"], 13)
    rss = box(s, 20, 205, 150, 60, ["Publisher", "RSS feeds"], 13, bold_first=True)
    rd = box(s, 630, 205, 150, 60, ["Reader"], 13, bold_first=True)
    hf = box(s, 310, 20, 180, 50, ["Hugging Face Hub"], 13, bold_first=True)
    ex = box(s, 280, 395, 240, 60, ["External news services", "(Google News, GNews, GDELT)"], 12, bold_first=True)
    s.line(170, 235, 320, 235, end="solid")
    label(s, 245, 227, "RSS entries")
    s.line(480, 220, 630, 220, end="solid")
    label(s, 555, 199, "pages, analysis,")
    label(s, 555, 213, "charts, PDF reports")
    s.line(630, 252, 480, 252, end="solid")
    label(s, 555, 270, "display name, query,")
    label(s, 555, 284, "filters, custom text")
    s.line(400, 70, 400, 155, end="solid")
    s.text(408, 118, "model weights (first use)", 11, anchor="start", style="italic")
    s.line(370, 312, 370, 395, end="solid")
    s.text(362, 358, "search query", 11, anchor="end", style="italic")
    s.line(430, 395, 430, 312, end="solid")
    s.text(438, 358, "news items", 11, anchor="start", style="italic")
    s.save("dfd0")


def dfd1():
    s = SVG(820, 690)
    R = 50
    box(s, 130, 20, 140, 46, ["Publisher RSS feeds"], 12, bold_first=True)
    box(s, 530, 20, 140, 46, ["Hugging Face Hub"], 12, bold_first=True)
    circle_proc(s, 200, 150, R, ["1.0", "Collect &", "clean"])
    circle_proc(s, 400, 150, R, ["2.0", "Remove", "duplicates"])
    circle_proc(s, 600, 150, R, ["3.0", "Analyse", "article"])
    circle_proc(s, 200, 320, R, ["4.0", "Group", "events"])
    circle_proc(s, 600, 320, R, ["5.0", "Store", "article"])
    store(s, 330, 305, 140, 30, "D1", "articles")
    circle_proc(s, 230, 485, 58, ["6.0", "Build edition,", "search, analytics"])
    circle_proc(s, 430, 485, R, ["7.0", "Generate", "PDF report"])
    circle_proc(s, 610, 485, R, ["8.0", "Register", "reader"])
    store(s, 690, 470, 120, 30, "D2", "named_visitors")
    box(s, 20, 450, 110, 70, ["External news", "(live RSS, Google", "News, GNews,", "GDELT)"], 11)
    rd = box(s, 360, 600, 140, 50, ["Reader"], 13, bold_first=True)
    # flows
    s.line(200, 66, 200, 100, end="solid"); s.text(206, 88, "RSS entries", 11, anchor="start", style="italic")
    s.line(600, 66, 600, 100, end="solid"); s.text(606, 88, "model weights", 11, anchor="start", style="italic")
    s.line(250, 150, 350, 150, end="solid"); label(s, 300, 142, "clean articles")
    s.line(450, 150, 550, 150, end="solid"); label(s, 500, 142, "new articles")
    s.line(400, 305, 400, 200, end="solid"); s.text(394, 262, "stored titles / URLs", 11, anchor="end", style="italic")
    s.line(600, 200, 600, 270, end="solid"); s.text(606, 240, "analysis results", 11, anchor="start", style="italic")
    s.line(550, 320, 470, 320, end="solid"); label(s, 510, 312, "article row")
    s.line(330, 311, 250, 311, end="solid"); label(s, 290, 303, "recent rows")
    s.line(250, 329, 330, 329, end="solid"); label(s, 290, 346, "group_id")
    s.path([(370, 335), (370, 400), (230, 400), (230, 427)], end="solid"); label(s, 300, 393, "articles (read-only)")
    s.line(430, 335, 430, 435, end="solid"); s.text(436, 380, "one article", 11, anchor="start", style="italic")
    s.line(130, 485, 172, 485, end="solid"); label(s, 151, 477, "items", 10.5)
    s.line(660, 485, 690, 485, end="solid")
    s.text(675, 462, "name", 10.5, style="italic")
    s.path([(200, 535), (200, 635), (360, 635)], end="solid"); label(s, 280, 628, "pages, analysis, charts")
    s.path([(360, 612), (258, 612), (258, 537)], end="solid"); label(s, 310, 605, "query, filters")
    s.line(430, 535, 430, 600, end="solid"); s.text(436, 572, "PDF file", 11, anchor="start", style="italic")
    s.path([(500, 625), (610, 625), (610, 535)], end="solid"); label(s, 555, 618, "display name")
    s.save("dfd1")


# ─── 3.3 Application workflow ───────────────────────────────────────────────────────────────

def workflow():
    s = SVG(780, 760)
    cx = 360

    def act(x, y, lines, w=300, h=None):
        h = h or (18 + 15 * len(lines))
        b = s.rect(x - w / 2, y, w, h, r=14)
        top = y + h / 2 - (len(lines) - 1) * 7.5 + 4
        for i, l in enumerate(lines):
            s.text(x, top + i * 15, l, 12)
        return b

    s.add(f"<circle cx='{cx}' cy='20' r='10' fill='{INK}'/>")
    a1 = act(cx, 46, ["Reader opens The Daily Signal (front page)"])
    s.line(cx, 30, cx, a1.top, end="open")
    d1 = s.diamond(cx, 125, 230, 50, "Display name already\nstored in the browser?")
    s.line(cx, a1.bottom, cx, d1.top, end="open")
    r1 = act(640, 100, ["Register display name", "POST /api/auth/profile", "(stored in named_visitors)"], w=230)
    s.line(d1.right, d1.cy, r1.left, d1.cy, end="open"); s.text(d1.right + 6, d1.cy - 6, "[no]", 11, anchor="start")
    m1 = s.diamond(cx, 200, 24, 24)
    s.line(cx, d1.bottom, cx, m1.top, end="open"); s.text(cx + 8, d1.bottom + 13, "[yes]", 11, anchor="start")
    s.path([(r1.cx, r1.bottom), (r1.cx, m1.cy), (m1.right, m1.cy)], end="open")
    a2 = act(cx, 235, ["Load edition: Supabase (500 newest rows)", "or live RSS feeds scored in TypeScript"], w=330)
    s.line(cx, m1.bottom, cx, a2.top, end="open")
    a3 = act(cx, 310, ["Front page: latest, breaking, daily feed,", "risk counts, most-covered events"], w=330)
    s.line(cx, a2.bottom, cx, a3.top, end="open")
    d2 = s.diamond(cx, 395, 170, 46, "Reader's choice")
    s.line(cx, a3.bottom, cx, d2.top, end="open")
    xs = [100, 280, 460, 660]
    labs = [["Browse a section", "/section/[slug]"], ["Search & filter", "/search (+ external)"],
            ["Compare coverage", "/compare"], ["View analytics", "/analytics"]]
    bus = 440
    s.line(cx, d2.bottom, cx, bus)
    s.line(xs[0], bus, xs[-1], bus)
    boxes = []
    for x, lab in zip(xs, labs):
        s.line(x, bus, x, 462, end="open")
        boxes.append(act(x, 462, lab, w=165))
    m2 = s.diamond(280, 560, 24, 24)
    for b in boxes[:3]:
        s.path([(b.cx, b.bottom), (b.cx, 540 if b.cx != 280 else m2.top)] + ([] if b.cx == 280 else [(b.cx, m2.cy), (m2.left if b.cx < 280 else m2.right, m2.cy)]), end="open")
    a4 = act(280, 595, ["Open article page: excerpt, credibility", "panel, 8-dimension radar and table"], w=320)
    s.line(280, m2.bottom, 280, a4.top, end="open")
    a5 = act(280, 670, ["Download PDF report", "(FastAPI ReportLab or browser jsPDF)"], w=300)
    s.line(280, a4.bottom, 280, a5.top, end="open")
    # end node
    ex, ey = 660, 690
    s.line(280 + 150, 694, ex - 14, 694, end="open")
    s.line(boxes[3].cx, boxes[3].bottom, ex, ey - 9, end="open")
    s.add(f"<circle cx='{ex}' cy='{ey + 4}' r='12' fill='white' stroke='{INK}' stroke-width='1.5'/>"
          f"<circle cx='{ex}' cy='{ey + 4}' r='7' fill='{INK}'/>")
    s.text(20, 745, "Section, search and compare pages link to the article page; the reader may return to the front page at any step.", 11, anchor="start", style="italic")
    s.save("workflow")


# ─── 3.4 Class diagram (data classes; operations are module-level functions) ───────────────

def class_diagram():
    s = SVG(900, 640)
    src = s.uml(20, 20, 220, "«conceptual» Source", ["- name : String", "- feedUrl : String", "- category : String"],
                ["«function» fetch_articles()"])
    art = s.uml(330, 20, 240, "Article", ["- id : UUID", "- title : String {unique}", "- sourceUrl : String",
                                          "- excerpt : String", "- category : String", "- publishedAt : DateTime"],
                ["«function» analyze_article()"])
    grp = s.uml(670, 20, 210, "ArticleGroup", ["- groupId : String", "- eventTitle : String", "- publishers : List<String>"],
                ["«function» cluster_articles()"])
    y2 = 330
    cred = s.uml(15, y2, 225, "CredibilityResult", ["- riskScore : float [0..1]", "- label : RiskLabel [0..1]",
                                                    "- classifierFakeScore : float [0..1]", "- classifierConfidence : float [0..1]",
                                                    "- needsVerification : bool", "- status : String"])
    dim = s.uml(255, y2, 220, "DimensionAnalysis", ["- sentiment : int [0..1]", "- bias : int [0..1]",
                                                     "- objectivity : int [0..1]", "- readability : int [0..1]",
                                                     "- propaganda : int [0..1]", "- headlineAccuracy : int [0..1]",
                                                     "- sourceCredibility : int [0..1]", "- contentQuality : int [0..1]",
                                                     "- explanations : Map"], ["«function» rule_risk()"])
    sen = s.uml(490, y2, 175, "SentimentResult", ["- label : Sentiment", "- score : int"])
    summ = s.uml(680, y2, 200, "Summary", ["- text : String", "- method : extractive"])
    rep = s.uml(680, 470, 200, "Report", ["- articleId : UUID", "- format : A4 PDF"], ["«function» build_article_report()"])
    yy = src.y + 40
    s.line(src.right, yy, art.left, yy)
    s.text(src.right + 8, yy - 6, "1", 11, anchor="start"); s.text(art.left - 8, yy - 6, "0..*", 11, anchor="end")
    s.text((src.right + art.left) / 2, yy + 16, "publishes", 11, style="italic")
    s.line(art.right, yy, grp.left, yy)
    s.text(art.right + 8, yy - 6, "2..*", 11, anchor="start"); s.text(grp.left - 8, yy - 6, "0..1", 11, anchor="end")
    s.text((art.right + grp.left) / 2, yy + 16, "groups", 11, style="italic")
    bus = 285
    s.line(art.cx, art.bottom, art.cx, bus, start="diamond")
    s.line(cred.cx, bus, summ.cx, bus)
    for b, mult in ((cred, "1"), (dim, "1"), (sen, "1"), (summ, "0..1")):
        s.line(b.cx, bus, b.cx, b.top)
        s.text(b.cx + 6, b.top - 6, mult, 11, anchor="start")
    s.text(art.cx + 10, art.bottom + 22, "1", 11, anchor="start")
    s.text(art.cx + 10, bus - 8, "composition", 11, anchor="start", style="italic")
    s.path([(rep.right - 20, rep.top), (rep.right - 20, 450), (892, 450), (892, art.y + 120), (art.right, art.y + 120)],
           dash=True, end="open")
    s.text(850, 444, "«uses»", 11, style="italic", bg=True)
    note(s, 15, 560, 640, 62, [
        "«function» marks a module-level Python function (e.g. analysis_pipeline.analyze_article), not a method.",
        "Article, its result parts, Summary and the group id are columns of the single articles table (JSONB dimensions).",
        "Source is conceptual (RSS_SOURCES dictionary + source_domain column); Report is streamed, never stored."], 11)
    s.save("class")


# ─── 3.4 Entity relationship diagram ────────────────────────────────────────────────────────

def erd():
    s = SVG(780, 495)

    def entity(x, y, w, name, rows, stereo=None):
        h = 28 + len(rows) * 15 + 8 + (14 if stereo else 0)
        s.rect(x, y, w, h, fill="white", sw=1.3)
        hh = 28 + (14 if stereo else 0)
        s.rect(x, y, w, hh, fill=FILL, sw=1.3)
        if stereo:
            s.text(x + w / 2, y + 14, stereo, 10.5, style="italic")
        s.text(x + w / 2, y + hh - 9, name, 13, weight="bold")
        for i, (k, c, t) in enumerate(rows):
            yy = y + hh + 16 + i * 15
            s.text(x + 8, yy, k, 10.5, anchor="start", weight="bold")
            s.text(x + 52, yy, c, 11.5, anchor="start")
            s.text(x + w - 8, yy, t, 11, anchor="end", style="italic")
        s.line(x + 46, y + hh, x + 46, y + h, sw=0.8)
        from gen_diagrams import Box
        return Box(x, y, w, h)

    rows = [("PK", "id", "uuid"), ("UK", "title", "text"), ("", "source_domain", "text"), ("", "source_url", "text"),
            ("", "content_summary", "text"), ("", "category", "text"), ("", "published_at", "timestamptz"),
            ("", "created_at", "timestamptz"), ("", "sentiment", "text"), ("", "risk_score", "real"),
            ("", "credibility_label", "text"), ("", "needs_verification", "boolean"), ("", "confidence_level", "real"),
            ("", "model_fake_probability", "real"), ("", "is_fake", "boolean"), ("", "credibility_score", "real"),
            ("", "dimensions", "jsonb"), ("", "ai_reasoning", "text"), ("", "ai_summary", "text"),
            ("", "summary_method", "text"), ("", "group_id", "text"), ("", "event_title", "text"),
            ("", "analysis_status", "text"), ("", "analysis_method", "text"), ("", "model_version", "text"),
            ("", "analyzed_at", "timestamptz")]
    a = entity(20, 20, 300, "articles", rows)
    nv = entity(470, 20, 290, "named_visitors", [("PK", "id", "uuid"), ("UK", "name", "text (1–40 chars)"),
                                                 ("", "created_at", "timestamptz")])
    up = entity(470, 170, 290, "user_profiles", [("PK,FK", "id", "uuid"), ("", "name", "text"),
                                                ("", "saved_topics", "text[]"), ("", "created_at", "timestamptz")],
                stereo="«defined, not used by the code»")
    au = entity(470, 400, 290, "auth.users", [("PK", "id", "uuid"), ("", "…", "managed by Supabase Auth")],
                stereo="«Supabase system table»")
    # one-to-one relation user_profiles -- auth.users (crow's-foot: two bars each end)
    x = 615
    s.line(x, up.bottom, x, au.top, sw=1.3)
    for yb in (up.bottom + 8, up.bottom + 14, au.top - 8, au.top - 14):
        s.line(x - 9, yb, x + 9, yb, sw=1.3)
    s.text(x + 14, (up.bottom + au.top) / 2 + 4, "is profile of (1 : 1)", 11, anchor="start", style="italic")
    # logical self-grouping of articles through group_id
    gy = a.y + 28 + 8 + 20 * 15
    s.path([(a.right, gy), (a.right + 40, gy), (a.right + 40, gy + 70), (a.right, gy + 70)], dash=True)
    s.text(a.right + 46, gy + 24, "logical group", 11, anchor="start", style="italic")
    s.text(a.right + 46, gy + 38, "via group_id", 11, anchor="start", style="italic")
    s.text(a.right + 46, gy + 52, "(no FK)", 11, anchor="start", style="italic")
    s.save("erd")


# ─── 3.5 Use-case diagram ───────────────────────────────────────────────────────────────────

def use_case():
    s = SVG(800, 690)
    s.rect(200, 20, 410, 655, fill="white", sw=1.4)
    s.text(405, 44, "AI-Powered News Aggregator", 14, weight="bold")
    base = (530, 150)
    s.ellipse(*base, 75, 24, "Run ingestion cycle")
    inc = ["Collect RSS feeds", "Remove duplicates", "Analyse articles\n(risk, sentiment, 8 dims)", "Group cross-source\nevents"]
    for i, u in enumerate(inc):
        y = 75 + i * 58
        s.ellipse(290, y, 85, 24, u, size=11.5)
        s.line(base[0] - 75, base[1], 375, y, dash=True, end="open")
    s.text(415, 105, "«include»", 10.5, style="italic", bg=True)
    s.text(415, 207, "«include»", 10.5, style="italic", bg=True)
    ax, ay = s.actor(710, 85, "Scheduler\n(every 30 min)")
    s.line(ax - 18, ay, base[0] + 75, base[1])
    reader_uc = ["Register display name", "View front page", "Browse sections", "Search & filter articles",
                 "View article analysis", "Compare coverage", "View analytics", "Download PDF report"]
    ys = []
    for i, u in enumerate(reader_uc):
        y = 330 + i * 42
        ys.append(y)
        s.ellipse(310, y, 98, 18, u, size=11.5)
    rx, ry = s.actor(90, 440, "Reader")
    for y in ys:
        s.line(rx + 18, ry, 212, y)
    ext = (515, 505)
    s.ellipse(*ext, 85, 22, "Search external news\n(Google News, GNews, GDELT)", size=10.5)
    s.line(ext[0] - 85, ext[1], 402, ys[3] + 10, dash=True, end="open")
    s.text(424, 486, "«extend»", 10.5, anchor="start", style="italic", bg=True)  #, 10.5, style="italic", bg=True)
    an = (515, 595)
    s.ellipse(*an, 85, 20, "Analyse custom text\n(POST /api/analyze)", size=10.5)
    ox, oy = s.actor(712, 400, "Operator /\nAPI client")
    s.line(ox - 18, oy, base[0] + 60, base[1] + 15)
    s.line(ox - 10, oy + 30, an[0] + 70, an[1] - 12)
    s.text(662, 300, "POST /api/ingest", 10.5, anchor="start", style="italic")
    s.text(668, 314, "(token)", 10.5, anchor="start", style="italic")
    s.save("usecase")


# ─── 3.6 Sequence diagram ───────────────────────────────────────────────────────────────────

def sequence():
    s = SVG(800, 760)
    X = {"reader": 80, "next": 290, "db": 500, "api": 700}
    s.actor(X["reader"], 16, "")
    s.text(X["reader"], 104, "Reader (browser)", 12, weight="bold")
    for key, name in (("next", "Next.js server"), ("db", "Supabase"), ("api", "FastAPI backend")):
        s.rect(X[key] - 78, 62, 156, 36, r=4)
        s.text(X[key], 85, name, 12.5, weight="bold")
    for k, x in X.items():
        s.line(x, 110 if k == "reader" else 98, x, 745, dash=True, sw=0.9)

    def act(x, y1, y2):
        s.rect(x - 6, y1, 12, y2 - y1, fill="white", sw=1.1)

    def msg(x1, x2, y, lab, ret=False, lab2=None):
        off = 6 if x2 > x1 else -6
        s.line(x1 + off, y, x2 - off, y, dash=ret, end="open" if ret else "solid")
        if lab2:
            s.text((x1 + x2) / 2, y - 20, lab, 11, style="italic", bg=True)
            s.text((x1 + x2) / 2, y - 6, lab2, 11, style="italic", bg=True)
        else:
            s.text((x1 + x2) / 2, y - 6, lab, 11, style="italic", bg=True)

    def self_msg(x, y, lab, h=18):
        s.path([(x + 6, y), (x + 40, y), (x + 40, y + h), (x + 12, y + h)], end="solid")
        s.text(x + 46, y + h / 2 + 4, lab, 11, anchor="start", style="italic", bg=True)

    def frame(x1, y1, x2, y2, guard, sep=None, guard2=None):
        s.rect(x1, y1, x2 - x1, y2 - y1, fill="none", sw=1.1)
        s.add(f"<polygon points='{x1},{y1} {x1 + 38},{y1} {x1 + 38},{y1 + 12} {x1 + 30},{y1 + 20} {x1},{y1 + 20}' fill='white' stroke='{INK}' stroke-width='1.1'/>")
        s.text(x1 + 17, y1 + 14, "alt", 11, weight="bold")
        s.text(x1 + 46, y1 + 15, guard, 11, anchor="start", style="italic", bg=True)
        if sep:
            s.line(x1, sep, x2, sep, dash=True, sw=1)
            s.text(x1 + 8, sep + 15, guard2, 11, anchor="start", style="italic", bg=True)

    act(X["reader"], 128, 720)
    act(X["next"], 140, 385)
    msg(X["reader"], X["next"], 140, "1: GET /article/{id}")
    frame(200, 160, 580, 318, "[edition cache older than 60 s]", 268, "[else]")
    act(X["db"], 222, 252)
    msg(X["next"], X["db"], 222, "2: select * from articles", lab2="order by published_at desc limit 500")
    msg(X["db"], X["next"], 252, "3: rows (≤ 500)", ret=True)
    self_msg(X["next"], 288, "3': reuse cached edition")
    self_msg(X["next"], 334, "4: find article by id, group, related")
    msg(X["next"], X["reader"], 380, "5: rendered article page (HTML)", ret=True)
    frame(30, 405, 780, 730, "[Download PDF report: backend URL set and article from the database]", 640, "[Export in browser]")
    act(X["api"], 455, 615)
    msg(X["reader"], X["api"], 455, "6: GET /api/v1/report/{id}")
    act(X["db"], 495, 530)
    msg(X["api"], X["db"], 495, "7: get_article_by_id(id)")
    msg(X["db"], X["api"], 530, "8: article row", ret=True)
    s.path([(X["api"] + 6, 555), (X["api"] + 40, 555), (X["api"] + 40, 575), (X["api"] + 12, 575)], end="solid")
    s.text(X["api"] - 10, 583, "9: build_article_report()", 11, anchor="end", style="italic", bg=True)
    msg(X["api"], X["reader"], 612, "10: application/pdf (attachment)", ret=True)
    self_msg(X["reader"], 675, "11: generateIntelligencePdf(article) with jsPDF; file saved locally", h=20)
    s.save("sequence")


# ─── 3.8 Component diagram (UML 2) ──────────────────────────────────────────────────────────

def component_diagram():
    s = SVG(800, 615)
    # provided interfaces at the top
    for (bx, lab, anc) in ((195, "HTTP pages and /api/* routes", "end"), (607, "REST API (/api, /api/v1)", "start")):
        s.add(f"<circle cx='{bx}' cy='34' r='9' fill='white' stroke='{INK}' stroke-width='1.3'/>")
        s.line(bx, 43, bx, 60)
        s.text(bx + (-16 if anc == "end" else 16), 38, lab, 11.5, anchor=anc, style="italic")
    nb = s.rect(20, 60, 350, 340, fill="#f7f7f7", sw=1.4)
    s.text(195, 78, "«subsystem» Next.js web application", 12.5, weight="bold")
    fb = s.rect(430, 60, 350, 340, fill="#f7f7f7", sw=1.4)
    s.text(605, 78, "«subsystem» FastAPI backend", 12.5, weight="bold")
    W, H = 140, 50
    c = {}
    c["pages"] = component(s, 40, 95, W, H, ["Pages & UI", "React components"])
    c["routes"] = component(s, 210, 95, W, H, ["API routes", "app/api/*"])
    c["repo"] = component(s, 125, 175, W, H, ["repository.ts", "data access"])
    c["live"] = component(s, 40, 255, W, H, ["liveNewsService", "externalSearch"])
    c["score"] = component(s, 210, 255, W, H, ["scoring.ts", "clustering.ts"])
    c["pdf"] = component(s, 40, 335, W, H, ["pdfReport-", "Generator (jsPDF)"])
    c["router"] = component(s, 450, 95, W, H, ["router.py", "REST endpoints"])
    c["sched"] = component(s, 625, 95, W, H, ["scheduler.py", "APScheduler"])
    c["report"] = component(s, 450, 175, W, H, ["report_service", "ReportLab PDF"])
    c["rss"] = component(s, 625, 175, W, H, ["rss_fetcher.py", "feeds, cleaning"])
    c["pipe"] = component(s, 450, 255, W, H, ["analysis_", "pipeline.py"])
    c["db"] = component(s, 625, 255, W, H, ["db_service.py", "storage"])
    c["dim"] = component(s, 450, 335, W, H, ["dimension_service", "ai_service"])
    c["clu"] = component(s, 625, 335, W, H, ["clustering_", "service.py"])

    def dep(pts):
        s.path(pts, dash=True, end="open")

    dep([(110, 145), (110, 160), (170, 160), (170, 175)])
    dep([(280, 145), (280, 160), (220, 160), (220, 175)])
    dep([(160, 225), (160, 240), (110, 240), (110, 255)])
    dep([(230, 225), (230, 240), (280, 240), (280, 255)])
    dep([(180, 280), (210, 280)])
    dep([(40, 120), (30, 120), (30, 360), (40, 360)])
    dep([(520, 145), (520, 175)])
    dep([(450, 120), (440, 120), (440, 280), (450, 280)])
    dep([(590, 112), (607, 112), (607, 265), (625, 265)])
    dep([(695, 145), (695, 175)])
    dep([(765, 120), (772, 120), (772, 280), (765, 280)])
    dep([(625, 290), (590, 290)])
    dep([(520, 305), (520, 335)])
    dep([(695, 305), (695, 335)])
    # Supabase with provided interface (ball) and two required interfaces (sockets)
    sb = s.rect(290, 490, 220, 64, fill="white", sw=1.3)
    comp_icon(s, 490, 495)
    s.text(395, 506, "«component» «database»", 10, style="italic")
    s.text(395, 524, "Supabase PostgreSQL", 12, weight="bold")
    s.text(395, 540, "articles · named_visitors", 11)
    bx, by = 400, 452
    s.line(bx, by + 9, bx, 490)
    s.add(f"<circle cx='{bx}' cy='{by}' r='9' fill='white' stroke='{INK}' stroke-width='1.3'/>")
    s.path([(250, 400), (250, by), (386, by)])
    s.add(f"<path d='M{bx - 4},{by - 14} A14,14 0 0 0 {bx - 4},{by + 14}' fill='none' stroke='{INK}' stroke-width='1.3'/>")
    s.path([(470, 400), (470, by), (414, by)])
    s.add(f"<path d='M{bx + 4},{by - 14} A14,14 0 0 1 {bx + 4},{by + 14}' fill='none' stroke='{INK}' stroke-width='1.3'/>")
    s.text(244, 440, "read (anon key)", 11, anchor="end", style="italic")
    s.text(476, 440, "write (service key)", 11, anchor="start", style="italic")
    s.text(410, 478, "PostgREST API", 11, anchor="start", style="italic")
    box(s, 20, 490, 200, 64, ["External news", "live RSS · Google News", "GNews · GDELT"], 11, fill="white", r=0, bold_first=True)
    s.line(110, 400, 110, 490, dash=True, end="open")
    box(s, 560, 490, 110, 64, ["Publisher", "RSS feeds", "(11 feeds)"], 11, fill="white", r=0, bold_first=True)
    s.line(615, 400, 615, 490, dash=True, end="open")
    box(s, 685, 490, 105, 64, ["Hugging Face", "models", "(transformers)"], 11, fill="white", r=0, bold_first=True)
    s.line(737, 400, 737, 490, dash=True, end="open")
    s.text(116, 450, "«use»", 10.5, anchor="start", style="italic")
    s.text(621, 450, "«use»", 10.5, anchor="start", style="italic")
    s.text(743, 450, "«use»", 10.5, anchor="start", style="italic")
    s.text(20, 584, "Dashed arrows are «use» dependencies. Ball = provided interface, socket = required interface.", 10.5, anchor="start", style="italic")
    s.text(20, 600, "pdfReportGenerator is loaded into the browser on demand; all other Next.js components run on the server.", 10.5, anchor="start", style="italic")
    s.save("component")


# ─── 3.9 Deployment diagram (UML 2) ─────────────────────────────────────────────────────────

def deployment():
    s = SVG(820, 640)
    # browser device
    node3d(s, 240, 30, 320, 120, "Reader's computer or phone", "«device»")
    envbox(s, 262, 68, 276, 58, ["Web browser", "React UI · Recharts · jsPDF report"])
    # next.js node
    node3d(s, 20, 230, 360, 170, "Next.js server", "«node»")
    envbox(s, 40, 268, 320, 120, ["Node.js 20 or later"])
    artifact(s, 58, 312, 284, 66, ["frontend (next build / next start)",
                                   "env: NEXT_PUBLIC_SUPABASE_URL, _ANON_KEY,", "NEXT_PUBLIC_API_URL (optional)"], 10.5)
    # fastapi node
    node3d(s, 430, 230, 360, 170, "Backend server or container", "«node»")
    envbox(s, 450, 268, 320, 120, ["Python 3.10+ · Uvicorn", "(optional Dockerfile: python:3.10-slim, port 7860)"], 10.5)
    artifact(s, 468, 314, 284, 68, ["backend (main.py, services, scheduler)",
                                    "env: SUPABASE_URL,", "SUPABASE_SERVICE_ROLE_KEY"], 10.5)
    # bottom row
    node3d(s, 20, 500, 200, 110, "News sources", "«node»", size=11.5)
    s.text(120, 556, "live publisher RSS (31)", 11)
    s.text(120, 572, "Google News · GNews", 11)
    s.text(120, 588, "GDELT DOC 2.0", 11)
    node3d(s, 270, 500, 230, 110, "Supabase cloud", "«cloud service»", size=11.5)
    s.rect(290, 545, 190, 52, fill="white", sw=1.1)
    s.text(385, 562, "«database» PostgreSQL", 10.5, style="italic")
    s.text(385, 578, "articles, named_visitors,", 11)
    s.text(385, 592, "user_profiles (unused)", 11)
    node3d(s, 545, 500, 115, 110, "Publisher", "«node»", size=11.5)
    s.text(602, 546, "RSS servers", 11.5, weight="bold")
    s.text(602, 570, "(11 backend", 11)
    s.text(602, 585, "feeds)", 11)
    node3d(s, 685, 500, 115, 110, "Hugging", "«cloud service»", size=11.5)
    s.text(742, 546, "Face Hub", 11.5, weight="bold")
    s.text(742, 570, "model weights", 11)
    s.text(742, 585, "(first use)", 11)
    # communication paths
    s.line(300, 150, 300, 218)
    s.text(306, 194, "HTTPS", 11, anchor="start", style="italic")
    s.line(500, 150, 500, 218, dash=True)
    s.text(506, 186, "HTTPS (optional", 11, anchor="start", style="italic")
    s.text(506, 200, "server PDF)", 11, anchor="start", style="italic")
    s.line(110, 400, 110, 488)
    s.text(116, 446, "HTTPS", 11, anchor="start", style="italic")
    s.line(320, 400, 320, 488)
    s.text(314, 440, "HTTPS (anon key)", 11, anchor="end", style="italic")
    s.line(460, 400, 460, 488)
    s.text(466, 440, "HTTPS (service key)", 11, anchor="start", style="italic")
    s.line(600, 400, 600, 488)
    s.text(606, 470, "HTTP(S)", 11, anchor="start", style="italic")
    s.line(740, 400, 740, 488)
    s.text(746, 440, "HTTPS", 11, anchor="start", style="italic")
    s.text(20, 632, "Deployment architecture supported by the code (a Dockerfile exists for the backend); no production deployment is claimed.", 10.5, anchor="start", style="italic")
    s.save("deployment")


# ─── 3.7 Activity diagram (copied from docs/report/gen_diagrams.py; skip path re-routed) ───

def activity():
    s = SVG(780, 1090)
    cx, rx = 340, 640
    W = 290

    def arrow(y1, y2, x=cx):
        s.line(x, y1, x, y2, end="open")

    s.add(f"<circle cx='{cx}' cy='20' r='10' fill='{INK}'/>")
    s.text(cx + 18, 24, "triggered every 30 minutes", 11, anchor="start", style="italic")
    m1 = s.diamond(cx, 65, 26, 26); arrow(30, m1.top)
    a = s.action(cx, 100, "Download next RSS feed (15 s timeout)", W); arrow(m1.bottom, a.top)
    d1 = s.diamond(cx, 175, 150, 44, "Request failed?"); arrow(a.bottom, d1.top)
    b = s.action(rx, d1.cy - 17, "Log failure, record feed name", 220)
    s.line(d1.right, d1.cy, b.left, d1.cy, end="open"); s.text(d1.right + 8, d1.cy - 6, "[yes]", 11, anchor="start")
    c = s.action(cx, 230, "Parse entries, clean HTML, ISO date", W); arrow(d1.bottom, c.top)
    s.text(cx + 8, d1.bottom + 12, "[no]", 11, anchor="start")
    m2 = s.diamond(cx, 300, 26, 26); arrow(c.bottom, m2.top)
    s.path([(rx, b.bottom), (rx, m2.cy), (m2.right, m2.cy)], end="open")
    d2 = s.diamond(cx, 355, 150, 44, "More feeds?"); arrow(m2.bottom, d2.top)
    s.path([(d2.left, d2.cy), (60, d2.cy), (60, m1.cy), (m1.left, m1.cy)], end="open")
    s.text(d2.left - 8, d2.cy - 6, "[yes]", 11, anchor="end")
    e = s.action(cx, 410, "Remove repeats within the batch (title, URL)", W); arrow(d2.bottom, e.top)
    s.text(cx + 8, d2.bottom + 12, "[no]", 11, anchor="start")
    m3 = s.diamond(cx, 480, 26, 26); arrow(e.bottom, m3.top)
    d3 = s.diamond(cx, 535, 170, 44, "Already in database?"); arrow(m3.bottom, d3.top)
    sk = s.action(rx, d3.cy - 17, "Skip (duplicate)", 220)
    s.line(d3.right, d3.cy, sk.left, d3.cy, end="open"); s.text(d3.right + 8, d3.cy - 6, "[yes]", 11, anchor="start")
    f = s.action(cx, 590, "Score 8 dimensions (rules); run models if available", W + 50); arrow(d3.bottom, f.top)
    s.text(cx + 8, d3.bottom + 12, "[no]", 11, anchor="start")
    d4 = s.diamond(cx, 668, 210, 54, "Scored dimensions carry\n≥ 65 % of risk weight?"); arrow(f.bottom, d4.top)
    g1 = s.action(200, 718, "Compute risk; Low / Moderate / High", 250)
    g2 = s.action(rx - 30, 718, "No score; label = not assessed", 230)
    s.path([(d4.left, d4.cy), (200, d4.cy), (200, g1.top)], end="open"); s.text(d4.left - 8, d4.cy - 6, "[yes]", 11, anchor="end")
    s.path([(d4.right, d4.cy), (rx - 30, d4.cy), (rx - 30, g2.top)], end="open"); s.text(d4.right + 8, d4.cy - 6, "[no]", 11, anchor="start")
    m4 = s.diamond(cx, 795, 26, 26)
    s.path([(200, g1.bottom), (200, m4.cy), (m4.left, m4.cy)], end="open")
    s.path([(rx - 30, g2.bottom), (rx - 30, m4.cy), (m4.right, m4.cy)], end="open")
    h = s.action(cx, 830, "Set Needs Verification if any rule applies *", W + 20); arrow(m4.bottom, h.top)
    i = s.action(cx, 890, "Insert article into Supabase", W); arrow(h.bottom, i.top)
    m5 = s.diamond(cx, 950, 26, 26); arrow(i.bottom, m5.top)
    # routed outside the "not assessed" branch so that no line crosses an action box
    s.path([(sk.right, sk.cy), (770, sk.cy), (770, m5.cy), (m5.right, m5.cy)], end="open")
    d5 = s.diamond(cx, 1000, 150, 44, "More articles?"); arrow(m5.bottom, d5.top)
    s.path([(d5.left, d5.cy), (30, d5.cy), (30, m3.cy), (m3.left, m3.cy)], end="open")
    s.text(d5.left - 8, d5.cy - 6, "[yes]", 11, anchor="end")
    j = s.action(rx, 983, "Re-group recent articles (TF-IDF)", 230)
    s.line(d5.right, d5.cy, j.left, d5.cy, end="open"); s.text(d5.right + 6, d5.cy - 6, "[no]", 11, anchor="start")
    s.line(j.cx, j.bottom, j.cx, 1036, end="open")
    s.add(f"<circle cx='{j.cx}' cy='1048' r='12' fill='white' stroke='{INK}' stroke-width='1.5'/>"
          f"<circle cx='{j.cx}' cy='1048' r='7' fill='{INK}'/>")
    s.text(20, 1080, "* no score, score 0.40–0.60, excerpt < 150 characters, classifier confidence < 0.60, or classifier and rules differ by ≥ 0.50",
           10.5, anchor="start", style="italic")
    s.save("activity")



if __name__ == "__main__":
    for fn in (modules, architecture, dfd0, dfd1, workflow, class_diagram, erd, use_case, sequence,
               activity, component_diagram, deployment):
        fn()
    print("written:", sorted(p.name for p in OUT.glob("*.svg")))
