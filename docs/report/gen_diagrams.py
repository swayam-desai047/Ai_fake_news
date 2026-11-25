"""Generates the UML / design diagrams of the project report as SVG files (docs/report/diagrams/)."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "diagrams"
OUT.mkdir(exist_ok=True)
FONT = "font-family='Times New Roman, serif'"
INK = "#111"
FILL = "#f4f4f4"


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def add(self, s):
        self.items.append(s)

    def text(self, x, y, s, size=12, anchor="middle", weight="normal", style="normal", under=False):
        deco = " text-decoration='underline'" if under else ""
        self.add(f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' "
                 f"font-style='{style}'{deco} {FONT} fill='{INK}'>{escape(s)}</text>")

    def rect(self, x, y, w, h, r=0, fill=FILL, dash=False, sw=1.2):
        d = " stroke-dasharray='5 3'" if dash else ""
        self.add(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{r}' fill='{fill}' stroke='{INK}' stroke-width='{sw}'{d}/>")

    def line(self, x1, y1, x2, y2, dash=False, arrow=True, sw=1.2, head="open"):
        d = " stroke-dasharray='5 3'" if dash else ""
        m = f" marker-end='url(#{head})'" if arrow else ""
        self.add(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{INK}' stroke-width='{sw}'{d}{m}/>")

    def poly(self, pts, arrow=True, dash=False):
        d = " stroke-dasharray='5 3'" if dash else ""
        m = " marker-end='url(#open)'" if arrow else ""
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f"<polyline points='{p}' fill='none' stroke='{INK}' stroke-width='1.2'{d}{m}/>")

    def ellipse(self, cx, cy, rx, ry, label, size=11):
        self.add(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{FILL}' stroke='{INK}' stroke-width='1.2'/>")
        lines = label.split("\n")
        for i, l in enumerate(lines):
            self.text(cx, cy + 4 + (i - (len(lines) - 1) / 2) * 13, l, size)

    def actor(self, x, y, name):
        self.add(f"<circle cx='{x}' cy='{y}' r='11' fill='white' stroke='{INK}' stroke-width='1.3'/>")
        self.line(x, y + 11, x, y + 42, arrow=False, sw=1.3)
        self.line(x - 18, y + 22, x + 18, y + 22, arrow=False, sw=1.3)
        self.line(x, y + 42, x - 15, y + 64, arrow=False, sw=1.3)
        self.line(x, y + 42, x + 15, y + 64, arrow=False, sw=1.3)
        for i, part in enumerate(name.split("\n")):
            self.text(x, y + 82 + i * 14, part, 12, weight="bold")

    def diamond(self, cx, cy, w, h, label, size=11):
        pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
        self.add(f"<polygon points='{pts}' fill='{FILL}' stroke='{INK}' stroke-width='1.2'/>")
        lines = label.split("\n")
        for i, l in enumerate(lines):
            self.text(cx, cy + 4 + (i - (len(lines) - 1) / 2) * 13, l, size)

    def uml_box(self, x, y, w, title, attrs, ops=(), obj=False, title_size=13, size=11):
        lh = 15
        h1 = 24
        h2 = max(1, len(attrs)) * lh + 8
        h3 = (len(ops) * lh + 8) if ops else (0 if obj else 10)
        self.rect(x, y, w, h1 + h2 + h3, fill="white", sw=1.3)
        self.rect(x, y, w, h1, fill=FILL, sw=1.3)
        self.text(x + w / 2, y + 16, title, title_size, weight="bold", under=obj)
        self.line(x, y + h1 + h2, x + w, y + h1 + h2, arrow=False) if (ops or not obj) else None
        for i, a in enumerate(attrs):
            self.text(x + 8, y + h1 + 15 + i * lh, a, size, anchor="start")
        for i, o in enumerate(ops):
            self.text(x + 8, y + h1 + h2 + 15 + i * lh, o, size, anchor="start")
        return h1 + h2 + h3

    def save(self, name):
        defs = (f"<defs><marker id='open' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='8' markerHeight='8' orient='auto-start-reverse'>"
                f"<path d='M0,0 L10,5 L0,10' fill='none' stroke='{INK}' stroke-width='1.4'/></marker>"
                f"<marker id='solid' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='8' markerHeight='8' orient='auto-start-reverse'>"
                f"<path d='M0,0 L10,5 L0,10 z' fill='{INK}'/></marker>"
                f"<marker id='tri' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='11' markerHeight='11' orient='auto-start-reverse'>"
                f"<path d='M0,0 L10,5 L0,10 z' fill='white' stroke='{INK}'/></marker></defs>")
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {self.w} {self.h}' width='{self.w}' height='{self.h}'>"
               f"{defs}<rect width='100%' height='100%' fill='white'/>{''.join(self.items)}</svg>")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


# ── System architecture ─────────────────────────────────────────────────────────────────────
def architecture():
    s = SVG(760, 430)
    layers = [
        ("Data source", "Public RSS feeds (BBC, CNN, Al Jazeera, Yahoo)"),
        ("Collection", "rss_fetcher.py · scheduler.py (APScheduler, every 30 min)"),
        ("Analysis", "analysis_pipeline.py → dimension_service · ai_service · summary · clustering"),
        ("Storage", "Supabase / PostgreSQL — articles, named_visitors (RLS)"),
        ("API", "FastAPI router.py (/api/...) · report_service.py (PDF)"),
        ("Presentation", "Next.js + React + Tailwind + Recharts (pages, search, analytics, PDF)"),
    ]
    for i, (name, desc) in enumerate(layers):
        y = 20 + i * 68
        s.rect(20, y, 150, 46, r=6)
        s.text(95, y + 28, name, 14, weight="bold")
        s.rect(200, y, 540, 46, r=6, fill="white")
        s.text(470, y + 28, desc, 13)
        if i < len(layers) - 1:
            s.line(95, y + 46, 95, y + 68)
    s.save("architecture")


# ── 3.1 Object diagram ───────────────────────────────────────────────────────────────────────
def object_diagram():
    s = SVG(780, 470)
    s.uml_box(20, 20, 230, "bbc : Source", ["name = \"BBC\"", "category = \"general\"",
                                            "reputation = 93 (reference table)"], obj=True)
    s.uml_box(275, 20, 250, "a1 : Article", ["title = \"Huawei found guilty of", "   stealing trade secrets...\"",
                                             "publishedAt = 2026-11-25 02:59 UTC", "excerpt = 52 characters",
                                             "groupId = ev-d73d…"], obj=True)
    s.uml_box(550, 20, 210, "c1 : CredibilityResult", ["riskScore = 0.15", "label = \"Low Risk\"",
                                                       "classifierFakeScore = null", "needsVerification = true",
                                                       "status = \"partial\""], obj=True)
    s.uml_box(20, 215, 230, "g1 : ArticleGroup", ["groupId = \"ev-d73d…\"", "publishers = [BBC, AlJazeera]",
                                                  "size = 2"], obj=True)
    s.uml_box(275, 245, 250, "d1 : DimensionAnalysis", ["sentiment = 50   bias = 84", "objectivity = 92   readability = 66",
                                                        "propaganda = 95   headline = 45", "sourceCredibility = 93",
                                                        "contentQuality = 44"], obj=True)
    s.uml_box(550, 215, 210, "s1 : SentimentResult", ["label = \"neutral\"", "score = 50 (rules)"], obj=True)
    s.uml_box(550, 330, 210, "r1 : Report", ["format = A4 PDF", "source = GET /api/report/{id}"], obj=True)
    s.line(250, 60, 275, 60, arrow=False)
    s.line(525, 70, 550, 70, arrow=False)
    s.line(140, 215, 300, 135, arrow=False)
    s.line(400, 140, 400, 245, arrow=False)
    s.line(525, 140, 600, 215, arrow=False)
    s.line(500, 140, 600, 330, arrow=False)
    s.text(390, 455, "Values are taken from an article processed by the implemented pipeline (models not loaded: status partial).", 11, style="italic")
    s.save("object")


# ── 3.2 Class diagram ────────────────────────────────────────────────────────────────────────
def class_diagram():
    s = SVG(800, 600)
    s.uml_box(20, 20, 220, "Source", ["- name : String", "- feedUrl : String", "- category : String"],
              ["+ fetchArticles() : List<Article>"])
    s.uml_box(290, 20, 230, "Article", ["- id : UUID", "- title : String (unique)", "- sourceUrl : String",
                                        "- excerpt : String", "- category : String", "- publishedAt : DateTime"],
              ["+ analyse() : AnalysisResult", "+ toReport() : Report"])
    s.uml_box(570, 20, 210, "CredibilityResult", ["- riskScore : float | null", "- label : RiskLabel | null",
                                                  "- classifierFakeScore : float | null",
                                                  "- classifierConfidence : float | null",
                                                  "- needsVerification : bool", "- status : String"])
    s.uml_box(570, 215, 210, "SentimentResult", ["- label : pos | neu | neg", "- score : int (0-100)"])
    s.uml_box(570, 320, 210, "Summary", ["- text : String", "- method : \"extractive\""])
    s.uml_box(250, 300, 290, "DimensionAnalysis", ["- sentiment : int | null", "- bias : int | null",
                                                   "- objectivity : int | null", "- readability : int | null",
                                                   "- propaganda : int | null", "- headlineAccuracy : int | null",
                                                   "- sourceCredibility : int | null", "- contentQuality : int | null",
                                                   "- explanations : Map<String,String>"],
              ["+ ruleRisk() : float | null"])
    s.uml_box(20, 230, 200, "ArticleGroup", ["- groupId : String", "- eventTitle : String", "- publishers : List"],
              ["+ addArticle(a : Article)"])
    s.uml_box(20, 420, 200, "Report", ["- articleId : UUID", "- generatedAt : DateTime"], ["+ generatePDF() : bytes"])
    # associations
    s.line(240, 60, 290, 60, arrow=False); s.text(250, 54, "1", 11); s.text(280, 54, "*", 11)
    s.line(520, 60, 570, 60, arrow=False); s.text(530, 54, "1", 11); s.text(560, 54, "1", 11)
    s.line(520, 140, 570, 240, arrow=False); s.text(560, 232, "1", 11)
    s.line(500, 170, 600, 320, arrow=False); s.text(590, 312, "0..1", 11)
    s.line(400, 170, 400, 300, arrow=False); s.text(410, 292, "1", 11)
    s.line(290, 150, 220, 250, arrow=False); s.text(282, 165, "*", 11); s.text(228, 245, "0..1", 11)
    s.line(300, 170, 200, 420, arrow=False, dash=True)
    s.text(230, 380, "«uses»", 11, style="italic")
    s.save("class")


# ── 3.3 Use case diagram ─────────────────────────────────────────────────────────────────────
def use_case():
    s = SVG(760, 640)
    s.rect(200, 20, 360, 600, fill="white", sw=1.4)
    s.text(380, 42, "AI-Powered News Aggregator", 14, weight="bold")
    sched = ["Collect RSS feeds", "Remove duplicates", "Analyse articles\n(risk, sentiment, 8 dimensions)",
             "Group cross-source events"]
    user = ["Register display name", "View news dashboard", "Search & filter articles", "View article analysis",
            "Compare coverage", "View analytics", "Download PDF report", "Analyse custom text (API)"]
    ys = []
    for i, u in enumerate(sched):
        y = 80 + i * 52
        s.ellipse(380, y, 150, 21, u)
        s.line(650, 150, 532, y, arrow=False)
    for i, u in enumerate(user):
        y = 300 + i * 40
        s.ellipse(380, y, 140, 17, u)
        s.line(100, 450, 238, y, arrow=False)
        ys.append(y)
    s.actor(100, 380, "Reader")
    s.actor(650, 90, "Scheduler\n(APScheduler)")
    s.save("usecase")


# ── 3.4 Sequence diagram ─────────────────────────────────────────────────────────────────────
def sequence():
    s = SVG(800, 560)
    parts = [("Reader", 70), ("Next.js frontend", 250), ("FastAPI backend", 450), ("Supabase DB", 650)]
    for name, x in parts:
        s.rect(x - 70, 15, 140, 36, r=6)
        s.text(x, 38, name, 13, weight="bold")
        s.line(x, 51, x, 540, dash=True, arrow=False, sw=1)
    msgs = [
        (70, 250, "1: open /article/{id}", False),
        (250, 650, "2: select * from articles where id = {id}", False),
        (650, 250, "3: article row (scores, risk, dimensions)", True),
        (250, 70, "4: render article + analysis supplement", True),
        (70, 450, "5: click Download PDF → GET /api/report/{id}", False),
        (450, 650, "6: get_article_by_id(id)", False),
        (650, 450, "7: article row", True),
        (450, 450, "8: build_article_report() (ReportLab)", False),
        (450, 70, "9: application/pdf file", True),
    ]
    y = 90
    for x1, x2, label, ret in msgs:
        if x1 == x2:
            s.poly([(x1, y - 6), (x1 + 50, y - 6), (x1 + 50, y + 12), (x1 + 4, y + 12)])
            s.text(x1 + 58, y + 6, label, 11, anchor="start", style="italic")
        else:
            s.line(x1, y, x2 - (6 if x2 > x1 else -6), y, dash=ret, head="solid" if not ret else "open")
            s.text((x1 + x2) / 2, y - 6, label, 11, style="italic")
        y += 50
    s.save("sequence")


# ── 3.5 Activity diagram ─────────────────────────────────────────────────────────────────────
def activity():
    s = SVG(760, 860)
    cx = 300
    s.add(f"<circle cx='{cx}' cy='25' r='11' fill='{INK}'/>")
    s.text(cx + 20, 29, "every 30 minutes (APScheduler)", 11, anchor="start", style="italic")
    steps = ["Fetch RSS feeds (timeout 15 s)", "Clean HTML, parse date, drop repeats in batch"]
    y = 55
    s.line(cx, 36, cx, y)
    for st in steps:
        s.rect(cx - 150, y, 300, 36, r=14); s.text(cx, y + 23, st, 12); s.line(cx, y + 36, cx, y + 60); y += 60
    s.diamond(cx, y + 30, 210, 60, "Feed failed?"); s.line(cx + 105, y + 30, 520, y + 30)
    s.rect(520, y + 12, 200, 36, r=14); s.text(620, y + 35, "Log + add to failed list", 12)
    s.text(cx + 120, y + 24, "[yes]", 11, anchor="start")
    s.line(cx, y + 60, cx, y + 85); y += 85
    s.diamond(cx, y + 30, 210, 60, "Already stored?\n(title / URL)"); s.line(cx + 105, y + 30, 520, y + 30)
    s.rect(520, y + 12, 200, 36, r=14); s.text(620, y + 35, "Skip (duplicate)", 12)
    s.text(cx + 120, y + 24, "[yes]", 11, anchor="start"); s.text(cx + 8, y + 76, "[no]", 11, anchor="start")
    s.line(cx, y + 60, cx, y + 85); y += 85
    for st in ["Score 8 dimensions (rules)", "Run classifier + sentiment model (if available)", "Combine risk score, label, summary"]:
        s.rect(cx - 150, y, 300, 36, r=14); s.text(cx, y + 23, st, 12); s.line(cx, y + 36, cx, y + 60); y += 60
    s.diamond(cx, y + 30, 230, 64, "Enough evidence?\n(≥ 65 % risk weight)"); s.line(cx + 115, y + 30, 520, y + 30)
    s.rect(520, y + 12, 220, 36, r=14); s.text(630, y + 35, "Label = not assessed", 12)
    s.text(cx + 125, y + 24, "[no]", 11, anchor="start"); s.line(cx, y + 62, cx, y + 85)
    s.poly([(630, y + 48), (630, y + 74), (cx + 6, y + 74)]); y += 85
    s.diamond(cx, y + 30, 250, 64, "Ambiguous score, short text,\nlow confidence or disagreement?"); s.line(cx + 125, y + 30, 520, y + 30)
    s.rect(520, y + 12, 220, 36, r=14); s.text(630, y + 35, "Flag Needs Verification", 12)
    s.text(cx + 135, y + 24, "[yes]", 11, anchor="start")
    s.line(cx, y + 62, cx, y + 85)
    s.poly([(630, y + 48), (630, y + 74), (cx + 6, y + 74)]); y += 85
    for st in ["Store article in Supabase", "Re-group recent articles (TF-IDF)"]:
        s.rect(cx - 150, y, 300, 36, r=14); s.text(cx, y + 23, st, 12); s.line(cx, y + 36, cx, y + 58); y += 58
    s.add(f"<circle cx='{cx}' cy='{y + 10}' r='12' fill='white' stroke='{INK}' stroke-width='1.5'/><circle cx='{cx}' cy='{y + 10}' r='7' fill='{INK}'/>")
    s.save("activity")


# ── 3.6 Module hierarchy ─────────────────────────────────────────────────────────────────────
def modules():
    s = SVG(800, 420)
    s.rect(290, 15, 220, 40, r=6); s.text(400, 40, "AI News Aggregator", 14, weight="bold")
    groups = [
        ("Collection", ["rss_fetcher.py", "scheduler.py"]),
        ("Analysis", ["dimension_service.py", "ai_service.py", "analysis_pipeline.py"]),
        ("Grouping", ["clustering_service.py", "clustering.ts"]),
        ("Storage", ["db_service.py", "db/supabase.py", "SQL migrations"]),
        ("API & Reports", ["api/router.py", "main.py", "report_service.py"]),
        ("Frontend", ["repository.ts", "scoring.ts", "pages / components", "pdfReportGenerator.ts"]),
    ]
    w = 122
    for i, (g, items) in enumerate(groups):
        x = 12 + i * (w + 9)
        s.line(400, 55, x + w / 2, 100)
        s.rect(x, 100, w, 34, r=5); s.text(x + w / 2, 122, g, 13, weight="bold")
        for j, it in enumerate(items):
            yy = 160 + j * 52
            s.rect(x + 6, yy, w - 12, 34, r=4, fill="white"); s.text(x + w / 2, yy + 22, it, 10.5)
            s.line(x + w / 2, (134 if j == 0 else yy - 18), x + w / 2, yy, arrow=False)
    s.save("modules")


if __name__ == "__main__":
    for f in (architecture, object_diagram, class_diagram, use_case, sequence, activity, modules):
        f()
    print("written:", sorted(p.name for p in OUT.glob("*.svg")))
