"""Generates the UML / design diagrams of the project report as SVG files (docs/report/diagrams/).

Conventions (UML 2): classes/objects in compartments, object names underlined, composition = filled
diamond at the whole, dependency = dashed line with open arrow, synchronous message = solid line with
filled arrowhead, return = dashed line with open arrowhead, activation bars on lifelines, activity
decisions/merges as diamonds, loops drawn back into a merge node.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "diagrams"
OUT.mkdir(exist_ok=True)
FONT = "font-family='Liberation Serif, Times New Roman, serif'"
INK = "#111"
FILL = "#f2f2f2"
LH = 15


class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2
    @property
    def top(self): return self.y
    @property
    def bottom(self): return self.y + self.h
    @property
    def left(self): return self.x
    @property
    def right(self): return self.x + self.w


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def add(self, s): self.items.append(s)

    def text(self, x, y, s, size=12, anchor="middle", weight="normal", style="normal", under=False, bg=False):
        if bg:
            tw = len(s) * size * 0.47
            x0 = x - tw / 2 if anchor == "middle" else (x if anchor == "start" else x - tw)
            self.add(f"<rect x='{x0 - 3}' y='{y - size + 1}' width='{tw + 6}' height='{size + 3}' fill='white'/>")
        deco = " text-decoration='underline'" if under else ""
        self.add(f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' "
                 f"font-style='{style}'{deco} {FONT} fill='{INK}'>{escape(s)}</text>")

    def rect(self, x, y, w, h, r=0, fill=FILL, dash=False, sw=1.2):
        d = " stroke-dasharray='5 3'" if dash else ""
        self.add(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{r}' fill='{fill}' stroke='{INK}' stroke-width='{sw}'{d}/>")
        return Box(x, y, w, h)

    def path(self, pts, dash=False, end=None, start=None, sw=1.2):
        d = " stroke-dasharray='6 4'" if dash else ""
        m = (f" marker-end='url(#{end})'" if end else "") + (f" marker-start='url(#{start})'" if start else "")
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f"<polyline points='{p}' fill='none' stroke='{INK}' stroke-width='{sw}'{d}{m}/>")

    def line(self, x1, y1, x2, y2, **kw): self.path([(x1, y1), (x2, y2)], **kw)

    def ellipse(self, cx, cy, rx, ry, label, size=11.5):
        self.add(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{FILL}' stroke='{INK}' stroke-width='1.2'/>")
        lines = label.split("\n")
        for i, l in enumerate(lines):
            self.text(cx, cy + 4 + (i - (len(lines) - 1) / 2) * 13, l, size)

    def actor(self, x, y, name):
        self.add(f"<circle cx='{x}' cy='{y}' r='11' fill='white' stroke='{INK}' stroke-width='1.3'/>")
        self.line(x, y + 11, x, y + 42, sw=1.3)
        self.line(x - 18, y + 22, x + 18, y + 22, sw=1.3)
        self.line(x, y + 42, x - 15, y + 64, sw=1.3)
        self.line(x, y + 42, x + 15, y + 64, sw=1.3)
        for i, part in enumerate([p for p in name.split("\n") if p]):
            self.text(x, y + 82 + i * 14, part, 12, weight="bold")
        return x, y + 22

    def diamond(self, cx, cy, w, h, label="", size=11):
        pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
        self.add(f"<polygon points='{pts}' fill='{FILL}' stroke='{INK}' stroke-width='1.2'/>")
        lines = [l for l in label.split("\n") if l]
        for i, l in enumerate(lines):
            self.text(cx, cy + 4 + (i - (len(lines) - 1) / 2) * 13, l, size)
        return Box(cx - w / 2, cy - h / 2, w, h)

    def uml(self, x, y, w, title, attrs, ops=None, obj=False, size=11):
        h1, h2 = 24, max(1, len(attrs)) * LH + 8
        h3 = 0 if obj else (len(ops or []) * LH + 8 if ops else 10)
        self.rect(x, y, w, h1 + h2 + h3, fill="white", sw=1.3)
        self.rect(x, y, w, h1, fill=FILL, sw=1.3)
        self.text(x + w / 2, y + 16, title, 12.5, weight="bold", under=obj)
        for i, a in enumerate(attrs):
            self.text(x + 7, y + h1 + 15 + i * LH, a, size, anchor="start")
        if not obj:
            self.line(x, y + h1 + h2, x + w, y + h1 + h2)
            for i, o in enumerate(ops or []):
                self.text(x + 7, y + h1 + h2 + 15 + i * LH, o, size, anchor="start")
        return Box(x, y, w, h1 + h2 + h3)

    def action(self, cx, y, label, w=300, h=34):
        b = self.rect(cx - w / 2, y, w, h, r=15)
        self.text(cx, y + h / 2 + 4, label, 12)
        return b

    def save(self, name):
        defs = (
            "<defs>"
            f"<marker id='open' viewBox='0 0 10 10' refX='10' refY='5' markerWidth='9' markerHeight='9' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10' fill='none' stroke='{INK}' stroke-width='1.3'/></marker>"
            f"<marker id='solid' viewBox='0 0 10 10' refX='10' refY='5' markerWidth='8' markerHeight='8' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{INK}'/></marker>"
            f"<marker id='diamond' viewBox='0 0 16 10' refX='16' refY='5' markerWidth='16' markerHeight='10' markerUnits='userSpaceOnUse' orient='auto-start-reverse'>"
            f"<path d='M0,5 L8,0 L16,5 L8,10 z' fill='{INK}'/></marker>"
            "</defs>")
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {self.w} {self.h}' width='{self.w}' height='{self.h}'>"
               f"{defs}<rect width='100%' height='100%' fill='white'/>{''.join(self.items)}</svg>")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def architecture():
    s = SVG(760, 430)
    layers = [
        ("Data source", "Public RSS feeds (BBC, CNN, Al Jazeera, Yahoo)"),
        ("Collection", "rss_fetcher.py · scheduler.py (APScheduler, every 30 min)"),
        ("Analysis", "analysis_pipeline.py → dimension_service · ai_service · summary"),
        ("Storage", "Supabase / PostgreSQL — articles, named_visitors (RLS)"),
        ("API", "FastAPI router.py (/api/...) · report_service.py (PDF)"),
        ("Presentation", "Next.js + React + Tailwind + Recharts (read-only Supabase key)"),
    ]
    for i, (name, desc) in enumerate(layers):
        y = 20 + i * 68
        s.rect(20, y, 150, 46, r=6)
        s.text(95, y + 28, name, 14, weight="bold")
        s.rect(200, y, 540, 46, r=6, fill="white")
        s.text(470, y + 28, desc, 13)
        if i < len(layers) - 1:
            s.line(95, y + 46, 95, y + 68, end="solid")
    s.save("architecture")


def object_diagram():
    s = SVG(820, 480)
    src = s.uml(20, 30, 220, "bbc : Source", ['name = "BBC"', 'category = "general"', "reputation = 93"], obj=True)
    art = s.uml(300, 30, 230, "a1 : Article", ['title = "Huawei found guilty of', '   stealing trade secrets..."',
                                              "publishedAt = 2026-11-25 02:59 UTC", "excerptLength = 52 chars",
                                              'groupId = "ev-d73d8a5a…"'], obj=True)
    a2 = s.uml(590, 30, 210, "a2 : Article", ['title = "China’s Huawei found', '   guilty of trade secrets..."',
                                             'publisher = "AlJazeera"', 'groupId = "ev-d73d8a5a…"'], obj=True)
    grp = s.uml(590, 210, 210, "g1 : ArticleGroup", ['groupId = "ev-d73d8a5a…"', "publishers = [BBC, AlJazeera]"], obj=True)
    cred = s.uml(20, 290, 230, "c1 : CredibilityResult", ["riskScore = 0.15", 'label = "Low Risk"',
                                                         "classifierFakeScore = null", "needsVerification = true",
                                                         'status = "partial"'], obj=True)
    dim = s.uml(300, 290, 230, "d1 : DimensionAnalysis", ["sentiment = 50, bias = 84", "objectivity = 92, readability = 66",
                                                         "propaganda = 95, headline = 45", "sourceCredibility = 93",
                                                         "contentQuality = 44"], obj=True)
    sen = s.uml(590, 350, 210, "s1 : SentimentResult", ['label = "neutral"', "score = 50 (rules)"], obj=True)
    s.line(src.right, src.y + 45, art.left, src.y + 45)
    s.line(art.right, art.y + 45, a2.left, art.y + 45)
    s.line(a2.cx, a2.bottom, grp.cx, grp.top)
    s.path([(art.right, art.y + 95), (565, art.y + 95), (565, grp.cy), (grp.left, grp.cy)])
    bus = art.bottom + 45
    s.path([(art.x + 40, art.bottom), (art.x + 40, bus), (cred.cx, bus), (cred.cx, cred.top)])
    s.line(art.x + 115, art.bottom, art.x + 115, dim.top)
    s.path([(art.x + 200, art.bottom), (art.x + 200, art.bottom + 30), (550, art.bottom + 30), (550, sen.cy), (sen.left, sen.cy)])
    s.text(410, 468, "Snapshot of one article processed by the implemented pipeline (models not installed: status partial).", 11, style="italic")
    s.save("object")


def class_diagram():
    s = SVG(900, 610)
    src = s.uml(20, 20, 210, "Source", ["- name : String", "- feedUrl : String", "- category : String"],
                ["+ fetch_articles() : List<Article>"])
    art = s.uml(330, 20, 240, "Article", ["- id : UUID", "- title : String {unique}", "- sourceUrl : String",
                                          "- excerpt : String", "- category : String", "- publishedAt : DateTime"],
                ["+ analyze_article() : void"])
    grp = s.uml(670, 20, 210, "ArticleGroup", ["- groupId : String", "- eventTitle : String", "- publishers : List<String>"],
                ["+ cluster_articles() : List"])
    y2 = 330
    cred = s.uml(15, y2, 225, "CredibilityResult", ["- riskScore : float [0..1]", "- label : RiskLabel [0..1]",
                                                    "- classifierFakeScore : float [0..1]", "- classifierConfidence : float [0..1]",
                                                    "- needsVerification : bool", "- status : String"])
    dim = s.uml(255, y2, 220, "DimensionAnalysis", ["- sentiment : int [0..1]", "- bias : int [0..1]",
                                                     "- objectivity : int [0..1]", "- readability : int [0..1]",
                                                     "- propaganda : int [0..1]", "- headlineAccuracy : int [0..1]",
                                                     "- sourceCredibility : int [0..1]", "- contentQuality : int [0..1]",
                                                     "- explanations : Map"], ["+ rule_risk() : float [0..1]"])
    sen = s.uml(490, y2, 175, "SentimentResult", ["- label : Sentiment", "- score : int"])
    summ = s.uml(680, y2, 200, "Summary", ["- text : String", "- method : String"])
    rep = s.uml(680, 470, 200, "Report", ["- articleId : UUID", "- format : A4 PDF"], ["+ build_article_report() : bytes"])
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
    s.save("class")


def use_case():
    s = SVG(780, 660)
    s.rect(210, 20, 360, 620, fill="white", sw=1.4)
    s.text(390, 44, "AI-Powered News Aggregator", 14, weight="bold")
    sched = ["Collect RSS feeds", "Remove duplicates", "Analyse articles\n(risk, sentiment, 8 dimensions)",
             "Group cross-source events"]
    user = ["Register display name", "View news dashboard", "Search & filter articles", "View article analysis",
            "Compare coverage", "View analytics", "Download PDF report", "Analyse custom text (API)"]
    ax, ay = s.actor(690, 120, "Scheduler\n(APScheduler)")
    for i, u in enumerate(sched):
        y = 85 + i * 55
        s.ellipse(390, y, 150, 22, u)
        s.line(ax - 18, ay, 540, y)
    rx, ry = s.actor(95, 400, "Reader")
    for i, u in enumerate(user):
        y = 320 + i * 40
        s.ellipse(390, y, 140, 17, u)
        s.line(rx + 18, ry, 250, y)
    s.save("usecase")


def sequence():
    s = SVG(840, 600)
    X = {"reader": 70, "next": 270, "api": 490, "db": 710}
    s.actor(X["reader"], 14, "")
    s.text(X["reader"], 100, "Reader", 12, weight="bold")
    for key, name in (("next", "Next.js server"), ("api", "FastAPI backend"), ("db", "Supabase (PostgreSQL)")):
        s.rect(X[key] - 82, 62, 164, 36, r=4)
        s.text(X[key], 85, name, 12.5, weight="bold")
    for x in X.values():
        s.line(x, 106, x, 585, dash=True, sw=0.9)

    def act(x, y1, y2):
        s.rect(x - 6, y1, 12, y2 - y1, fill="white", sw=1.1)

    def msg(x1, x2, y, label, ret=False):
        off = 6 if x2 > x1 else -6
        s.line(x1 + off, y, x2 - off, y, dash=ret, end="open" if ret else "solid")
        s.text((x1 + x2) / 2, y - 6, label, 11, style="italic", bg=True)

    act(X["reader"], 120, 570)
    act(X["next"], 140, 255)
    act(X["db"], 175, 215)
    act(X["api"], 315, 545)
    act(X["db"], 350, 390)
    msg(X["reader"], X["next"], 140, "1: GET /article/{id}")
    msg(X["next"], X["db"], 175, "2: select * from articles where id = {id}")
    msg(X["db"], X["next"], 215, "3: article row", ret=True)
    msg(X["next"], X["reader"], 250, "4: rendered article page", ret=True)
    msg(X["reader"], X["api"], 315, "5: GET /api/report/{id}  (Download PDF)")
    msg(X["api"], X["db"], 350, "6: get_article_by_id(id)")
    msg(X["db"], X["api"], 390, "7: article row", ret=True)
    act(X["api"] + 8, 440, 490)
    s.path([(X["api"] + 6, 425), (X["api"] + 50, 425), (X["api"] + 50, 455), (X["api"] + 14, 455)], end="solid")
    s.text(X["api"] + 58, 444, "8: build_article_report()", 11, anchor="start", style="italic")
    msg(X["api"], X["reader"], 540, "9: application/pdf (attachment)", ret=True)
    s.save("sequence")


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
    s.path([(rx, sk.bottom), (rx, m5.cy), (m5.right, m5.cy)], end="open")
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


def modules():
    s = SVG(800, 400)
    root = s.rect(290, 15, 220, 40, r=6); s.text(400, 40, "AI News Aggregator", 14, weight="bold")
    groups = [
        ("Collection", ["rss_fetcher.py", "scheduler.py"]),
        ("Analysis", ["dimension_service.py", "ai_service.py", "analysis_pipeline.py"]),
        ("Grouping", ["clustering_service.py", "clustering.ts"]),
        ("Storage", ["db_service.py", "db/supabase.py", "SQL migrations"]),
        ("API & Reports", ["api/router.py", "main.py", "report_service.py"]),
        ("Frontend", ["repository.ts", "scoring.ts", "pages / components", "pdfReportGenerator.ts"]),
    ]
    w = 122
    s.line(400, root.bottom, 400, 78)
    s.line(12 + w / 2, 78, 12 + 5 * (w + 9) + w / 2, 78)
    for i, (g, items) in enumerate(groups):
        x = 12 + i * (w + 9)
        s.line(x + w / 2, 78, x + w / 2, 100)
        s.rect(x, 100, w, 34, r=5); s.text(x + w / 2, 122, g, 13, weight="bold")
        s.line(x + 10, 134, x + 10, 160 + (len(items) - 1) * 52 + 17)
        for j, it in enumerate(items):
            yy = 160 + j * 52
            s.line(x + 10, yy + 17, x + 18, yy + 17)
            s.rect(x + 18, yy, w - 20, 34, r=4, fill="white"); s.text(x + 18 + (w - 20) / 2, yy + 22, it, 10)
    s.save("modules")


if __name__ == "__main__":
    for fn in (architecture, object_diagram, class_diagram, use_case, sequence, activity, modules):
        fn()
    print("written:", sorted(p.name for p in OUT.glob("*.svg")))
