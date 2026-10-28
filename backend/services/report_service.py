"""
Executive PDF report generation (handover §6 step 4).

Builds an A4 report for one article using ReportLab: header with platform metadata and
timestamp, headline and provenance, AI summary, credibility label and confidence, the eight
dimension scores with explanations, and the academic disclaimer. Values that were never
recorded are printed as "Not recorded" rather than filled in.
"""
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

INK = colors.HexColor("#171717")
GREY = colors.HexColor("#626262")
RULE = colors.HexColor("#D8D6D0")
PAPER = colors.HexColor("#F0EEE8")

DISCLAIMER = (
    "This report provides AI-generated indicators for critical evaluation and does not "
    "constitute absolute proof of factual truth."
)

DIMENSIONS = [
    ("sentiment", "Sentiment", "0 negative tone - 100 positive tone"),
    ("bias", "Bias", "0 loaded - 100 balanced"),
    ("objectivity", "Objectivity", "0 opinionated - 100 factual"),
    ("readability", "Readability", "0 dense - 100 plain"),
    ("propaganda", "Propaganda / Manipulation", "0 many markers - 100 none detected"),
    ("headline_accuracy", "Headline Accuracy", "0 unsupported - 100 supported"),
    ("source_credibility", "Source Credibility", "0 unrated - 100 established"),
    ("content_quality", "Content Quality", "0 thin - 100 complete"),
]


def _text(value: Any, fallback: str = "Not recorded") -> str:
    if value is None or value == "":
        return fallback
    return escape(str(value))


def build_article_report(article: Dict[str, Any]) -> bytes:
    """Return the PDF bytes for one article row from the `articles` table."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
        title=f"Report: {article.get('title', 'Article')}", author="The Daily Signal",
    )
    base = getSampleStyleSheet()
    nameplate = ParagraphStyle("nameplate", parent=base["Title"], fontName="Times-Bold", fontSize=24, leading=28, alignment=TA_CENTER, textColor=INK)
    sub = ParagraphStyle("sub", parent=base["Normal"], fontName="Times-Italic", fontSize=9.5, alignment=TA_CENTER, textColor=GREY)
    label = ParagraphStyle("label", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=GREY, spaceAfter=3)
    headline = ParagraphStyle("headline", parent=base["Normal"], fontName="Times-Bold", fontSize=17, leading=20, textColor=INK, spaceAfter=4)
    body = ParagraphStyle("body", parent=base["Normal"], fontName="Times-Roman", fontSize=10.5, leading=14, textColor=INK)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11)
    meta = ParagraphStyle("meta", parent=base["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=GREY)

    generated = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    story = [
        Paragraph("The Daily Signal", nameplate),
        Paragraph("Article Intelligence Report", sub),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1.2, color=INK, spaceAfter=1),
        HRFlowable(width="100%", thickness=0.4, color=INK, spaceAfter=3 * mm),
        Paragraph(f"Generated {generated} · AI News Aggregator, MIT-WPU M.Sc Computer Science, Group 17", meta),
        Spacer(1, 4 * mm),
        Paragraph(f"{_text(article.get('category'), 'General').upper()} · {_text(article.get('source_domain'), 'Unknown publisher').upper()}", label),
        Paragraph(_text(article.get("title"), "Untitled"), headline),
        Paragraph(f"Published: {_text(article.get('published_at'))}", meta),
    ]
    if article.get("source_url"):
        url = escape(article["source_url"])
        story.append(Paragraph(f'Source: <link href="{url}" color="#171717">{url}</link>', meta))
    story.append(Spacer(1, 4 * mm))

    summary = article.get("ai_summary") or article.get("content_summary")
    if summary:
        box = Table(
            [[Paragraph("AI SUMMARY" if article.get("ai_summary") else "STORED EXCERPT", label)], [Paragraph(escape(summary), body)]],
            colWidths=[doc.width],
        )
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PAPER),
            ("LINEABOVE", (0, 0), (-1, 0), 1, INK),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ]))
        story += [box, Spacer(1, 5 * mm)]

    confidence = article.get("confidence_level")
    risk_score = article.get("risk_score")
    cred_rows = [
        [Paragraph(h, label) for h in ("RISK LABEL", "RISK SCORE (0-1)", "CONFIDENCE", "VERIFICATION")],
        [
            Paragraph(_text(article.get("credibility_label")), body),
            Paragraph(f"{risk_score:.2f}" if isinstance(risk_score, (int, float)) else "Not recorded", body),
            Paragraph(f"{round(confidence * 100)}%" if isinstance(confidence, (int, float)) else "Not reported", body),
            Paragraph("Needs verification" if article.get("needs_verification") else "Not flagged", body),
        ],
    ]
    cred = Table(cred_rows, colWidths=[doc.width / 4] * 4)
    cred.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story += [Paragraph("CREDIBILITY INDICATORS", label), cred]
    if article.get("ai_reasoning"):
        story += [Spacer(1, 2 * mm), Paragraph(f"<i>{escape(article['ai_reasoning'])}</i>", small)]
    story.append(Spacer(1, 6 * mm))

    dims = article.get("dimensions") or {}
    explanations = dims.get("explanations") or {}
    story.append(Paragraph("EIGHT-DIMENSION CONTENT ANALYSIS", label))
    if not any(isinstance(dims.get(k), (int, float)) for k, _, _ in DIMENSIONS):
        story.append(Paragraph("<i>No dimension scores are recorded for this article.</i>", body))
    else:
        rows = [[Paragraph(h, label) for h in ("DIMENSION", "SCORE", "EXPLANATION")]]
        for key, name, scale in DIMENSIONS:
            score = dims.get(key)
            rows.append([
                Paragraph(f"<b>{name}</b><br/><font size=6.5 color='#626262'>{scale}</font>", small),
                Paragraph(f"<b>{round(score)}</b>" if isinstance(score, (int, float)) else "—", body),
                Paragraph(_text(explanations.get(key), "No explanation recorded."), small),
            ])
        table = Table(rows, colWidths=[doc.width * 0.32, doc.width * 0.1, doc.width * 0.58], repeatRows=1)
        table.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 1, INK),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, INK),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)

    story += [
        Spacer(1, 8 * mm),
        HRFlowable(width="100%", thickness=0.8, color=INK, spaceAfter=3 * mm),
        Paragraph(f"<i>{DISCLAIMER}</i>", small),
    ]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(GREY)
        canvas.drawString(16 * mm, 9 * mm, "The Daily Signal · MIT World Peace University (MIT-WPU), Pune · Group 17")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
