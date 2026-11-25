"""
Builds docs/Project_Report.pdf from content.html.

  python docs/report/gen_diagrams.py   # SVG diagrams
  python docs/report/build.py          # needs Node + Playwright (Chromium) and pypdf

Code excerpts are copied from the real source files at build time; the /api/analyze example is read
from analyze_example.json (output captured from the running API).
"""
import json
import re
import subprocess
import sys
from html import escape
from pathlib import Path

from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT_PDF = ROOT / "docs" / "Project_Report.pdf"


def excerpt(path, start, end, include_end=True):
    text = (ROOT / path).read_text(encoding="utf-8")
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i: j + (len(end) if include_end else 0)].rstrip()


CODE = {
    "dimension_rule_risk": excerpt("backend/services/dimension_service.py", "def rule_risk(", "return round2(1 - composite), weight"),
    "pipeline_risk": excerpt("backend/services/analysis_pipeline.py", "    rule_score, _ = rule_risk(dims)", "    needs_verification = bool(flags)"),
    "ai_classify": excerpt("backend/services/ai_service.py", "    fake = scores.get(FAKE_LABEL", "    return result", include_end=True),
    "cluster_loop": excerpt("backend/services/clustering_service.py", "    for i in range(len(pool)):", "        assigned.update(idx for idx, _ in kept)"),
    "router_article": excerpt("backend/api/router.py", '@api_router.get("/article/{article_id}")', "    return article"),
}


def analyze_example():
    data = json.loads((HERE / "analyze_example.json").read_text())
    full = data["response"]
    keep = ("risk_score", "credibility_label", "needs_verification", "sentiment", "analysis_status", "analysis_method")
    res = {k: full[k] for k in keep}
    res["dimensions"] = {k: v for k, v in full["dimensions"].items() if k != "explanations"}
    res["ai_reasoning"] = full["ai_reasoning"]
    return "Request:\n" + json.dumps(data["request"], indent=1, ensure_ascii=False) + "\n\nResponse (shortened):\n" + json.dumps(res, indent=1, ensure_ascii=False)


CSS = """
@page { size: A4; margin: 25mm 20mm 22mm 30mm; }
html { font-family: 'Times New Roman', 'Liberation Serif', serif; font-size: 12pt; line-height: 1.5; color: #000; }
body { margin: 0; }
h1 { font-size: 16pt; text-transform: uppercase; text-align: center; margin: 0 0 14pt; break-after: avoid; }
h2 { font-size: 14pt; margin: 14pt 0 6pt; break-after: avoid; }
h3 { font-size: 12pt; margin: 10pt 0 4pt; break-after: avoid; }
p { text-align: justify; margin: 0 0 8pt; }
ul, ol { margin: 0 0 8pt; padding-left: 22pt; }
li { margin-bottom: 2pt; text-align: justify; }
.chapter { break-before: page; }
.chapter:first-child, .chapter.cont { break-before: auto; }
.chapter.cont h1 { margin-top: 20pt; }
table { border-collapse: collapse; width: 100%; table-layout: auto; margin: 4pt 0 12pt; font-size: 11pt; line-height: 1.3; break-inside: auto; }
table.small { font-size: 10pt; }
caption { font-weight: bold; margin-bottom: 4pt; caption-side: top; text-align: center; }
th, td { border: 1px solid #000; padding: 2pt 4pt; overflow-wrap: break-word; vertical-align: top; text-align: left; }
th { background: #eee; }
tr { break-inside: avoid; }
figure { margin: 8pt 0 12pt; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 205mm; }
figure img.bordered, figure img[src^="img/"] { border: 1px solid #999; }
figcaption { font-weight: bold; font-size: 11pt; margin-top: 4pt; }
pre.code { font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace; font-size: 8.3pt; line-height: 1.3;
  background: #f6f6f6; border: 1px solid #bbb; padding: 6pt 8pt; white-space: pre-wrap; break-inside: auto; }
.refs li { margin-bottom: 4pt; text-align: left; }
"""

FRONT_CSS = CSS + """
.cover { text-align: center; height: 245mm; display: flex; flex-direction: column; justify-content: space-between; }
.cover img { width: 75%; }
.cover .uni { font-size: 22pt; margin-top: 10mm; }
.cover .dept { font-size: 15pt; }
.cover .title { font-size: 22pt; font-weight: bold; line-height: 1.3; margin: 0 8mm; }
.cover .label { font-size: 14pt; }
.page { break-before: page; }
.team td, .team th { text-align: center; font-size: 12pt; padding: 3pt; }
.page p { margin-bottom: 5pt; }
.idx td { border: 1px solid #000; }
.idx td:first-child { width: 12%; text-align: center; }
.idx td:last-child { width: 14%; text-align: center; }
.idx tr.ch td { font-weight: bold; }
"""

INDEX = [
    ("1", "Introduction", "1. Introduction", True),
    ("1.1", "Existing System, Proposed System And Need And Objective Of System", "1.1 Existing System", False),
    ("1.2", "Scope Of Work", "1.2 Scope of Work", False),
    ("1.3", "Operating Environment – Hardware And Software", "1.3 Operating Environment", False),
    ("1.4", "Description Of Technology Used", "1.4 Description of Technology", False),
    ("2", "Proposed System", "2. Proposed System", True),
    ("2.1", "Feasibility Study", "2.1 Feasibility Study", False),
    ("2.2", "User Requirements", "2.2 User Requirements", False),
    ("3", "Analysis And Design", "3. Analysis and Design", True),
    ("3.1", "Object Diagram", "3.1 Object Diagram", False),
    ("3.2", "Class Diagram", "3.2 Class Diagram", False),
    ("3.3", "Use Case Diagram", "3.3 Use Case Diagram", False),
    ("3.4", "Sequence Diagram", "3.4 Sequence Diagram", False),
    ("3.5", "Activity Diagram", "3.5 Activity Diagram", False),
    ("3.6", "Module Hierarchy Diagram", "3.6 Module Hierarchy Diagram", False),
    ("3.7", "User Interface Design (Screens)", "3.7 User Interface Design", False),
    ("3.8", "Table Specifications", "3.8 Table Specifications", False),
    ("4", "Input And Output Screens", "4. Input and Output Screens", True),
    ("5", "Test Procedures And Implementation", "5. Test Procedures and Implementation", True),
    ("6", "Sample Code", "6. Sample Code", True),
    ("7", "Limitations", "7. Limitations", True),
    ("8", "Future Scope", "8. Future Scope", True),
    ("9", "Conclusion", "9. Conclusion", True),
    ("10", "References", "10. References", True),
]

TEAM = [("1", "Swayam Desai", "1272260064"), ("2", "Vinit Mistry", "1272260066"),
        ("3", "Hetvi Patel", "1272260131"), ("4", "Tapaswini Nayak", "1272262064")]

ABSTRACT = """
<p>Online news is published continuously by many sources, and the same event appears under different headlines,
wording and levels of detail. Readers find it hard to compare coverage and to judge which reports use emotional,
one-sided or sensational language. This project presents an AI-Powered News Aggregator that collects articles
from selected RSS feeds every 30 minutes, removes duplicates and analyses each article.</p>
<p>Each article receives a credibility-risk indicator (Low, Moderate or High, or "not assessed" when the text is
insufficient), a sentiment label and eight content-analysis scores — sentiment, bias, objectivity, readability,
propaganda/manipulation, headline accuracy, source credibility and content quality — each with a plain-language
explanation. A BERT-tiny fake-news classifier and a DistilBERT sentiment model are combined with transparent
rules, and articles that need human checking are flagged. Reports of the same event from different publishers
are grouped with TF-IDF similarity. The system is built with Python, FastAPI, Hugging Face Transformers,
Supabase/PostgreSQL, Next.js, React, Tailwind CSS and Recharts, and provides search, analytics and PDF
reports.</p>
<p>The outputs are machine-generated indicators for critical reading, not proof that a report is true or false.
The system was tested with 62 backend and 32 frontend automated tests and an end-to-end run on real BBC and
Al Jazeera feed items.</p>
<p><b>Keywords:</b> fake news detection, news aggregation, NLP, BERT, sentiment analysis, credibility, TF-IDF.</p>
"""


def front_html(pages):
    rows = []
    for num, title, _key, chapter in INDEX:
        pg = pages.get(num, "")
        rows.append(f"<tr class='{'ch' if chapter else ''}'><td>{num}</td><td>{escape(title)}</td><td>{pg}</td></tr>")
    team = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in TEAM)
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>{FRONT_CSS}</style></head><body>
<div class='cover'>
  <div><img src='img/mitwpu_logo.jpg'>
  <div class='uni'>School of Computer Science &amp; Engineering</div>
  <div class='dept'>Department of Computer Science and Applications</div>
  <div class='dept' style='margin-top:6mm'>2026-2027</div></div>
  <div><div class='label'>Mini Project Report on</div><br>
  <div class='title'>“AI-Powered News Aggregator with Advanced Credibility and Content Analysis”</div></div>
  <div class='label'>Course Code: MSC40040 &nbsp;·&nbsp; First Year M.Sc. Computer Science<br>Group Id: 17</div>
</div>
<div class='page'>
  <h1>Project Details</h1>
  <p><b>Project Title:</b> AI-Powered News Aggregator with Advanced Credibility and Content Analysis</p>
  <p><b>Course Code:</b> MSC40040 &nbsp; <b>Year:</b> 2026-2027 &nbsp; <b>Group Id:</b> 17</p>
  <p><b>Team Leader:</b> Swayam Desai</p>
  <table class='team'><tr><th>S.No.</th><th>Team Member</th><th>PRN</th></tr>{team}</table>
  <p><b>Name of the Mentor:</b> Prof. Pradeep Tiwari</p>
  <h1 style='margin-top:8mm'>Abstract</h1>{ABSTRACT}
</div>
<div class='page'><h1>Index</h1><table class='idx'><tr><th>No.</th><th>Contents</th><th>Page</th></tr>{''.join(rows)}</table></div>
</body></html>"""


def body_html():
    html = (HERE / "content.html").read_text(encoding="utf-8")
    for key, code in CODE.items():
        html = html.replace("{{CODE:%s}}" % key, escape(code))
    html = html.replace("{{ANALYZE_EXAMPLE}}", escape(analyze_example()))
    assert "{{" not in html, re.findall(r"\{\{[^}]+\}\}", html)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>"


RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out, numbered] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'networkidle' });
  const footer = numbered === '1'
    ? "<div style='width:100%;font-size:9pt;font-family:Liberation Serif,serif;text-align:center;'>Page <span class='pageNumber'></span></div>"
    : "<div></div>";
  await p.pdf({ path: out, format: 'A4', preferCSSPageSize: true, displayHeaderFooter: true,
                headerTemplate: '<div></div>', footerTemplate: footer, printBackground: true });
  await b.close();
})();
"""


def render(html, name, numbered):
    src = HERE / f"_{name}.html"
    src.write_text(html, encoding="utf-8")
    js = HERE / "_render.js"
    js.write_text(RENDER_JS)
    out = HERE / f"_{name}.pdf"
    subprocess.run(["node", str(js), str(src), str(out), "1" if numbered else "0"], check=True,
                   cwd=ROOT / "frontend")  # resolves the playwright package
    return out


def heading_pages(pdf):
    """Page number (1-based) where each index heading first appears."""
    texts = [re.sub(r"\s+", " ", page.extract_text() or "") for page in PdfReader(str(pdf)).pages]
    found = {}
    for num, _title, key, _ in INDEX:
        for i, t in enumerate(texts):
            if key in t or key.upper() in t:
                found[num] = i + 1
                break
    return found, len(texts)


def main():
    body = render(body_html(), "body", True)
    pages, n_body = heading_pages(body)
    missing = [n for n, *_ in INDEX if n not in pages]
    if missing:
        print("warning: headings not located:", missing, file=sys.stderr)
    front = render(front_html(pages), "front", False)
    writer = PdfWriter()
    for part in (front, body):
        for page in PdfReader(str(part)).pages:
            writer.add_page(page)
    writer.add_metadata({"/Title": "AI-Powered News Aggregator with Advanced Credibility and Content Analysis — Project Report",
                         "/Author": "MIT-WPU M.Sc. Computer Science, Group 17"})
    with open(OUT_PDF, "wb") as fh:
        writer.write(fh)
    n_front = len(PdfReader(str(front)).pages)
    for f in HERE.glob("_*"):
        f.unlink()
    print(f"{OUT_PDF}: {n_front} front pages + {n_body} numbered pages; index pages: {pages}")


if __name__ == "__main__":
    main()
