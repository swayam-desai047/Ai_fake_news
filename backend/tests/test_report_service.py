from io import BytesIO

import pytest

from services.report_service import build_article_report

pypdf = pytest.importorskip("pypdf")


def _text(pdf: bytes) -> str:
    return " ".join(page.extract_text() for page in pypdf.PdfReader(BytesIO(pdf)).pages)


def test_report_contains_required_fields():
    pdf = build_article_report({
        "title": "Flood warning issued", "source_domain": "BBC", "published_at": "2026-11-24",
        "source_url": "https://bbc.co.uk/x", "content_summary": "Officials warned residents.",
        "credibility_label": "Moderate Risk", "risk_score": 0.42, "confidence_level": 0.81,
        "model_fake_probability": 0.3, "needs_verification": True, "ai_reasoning": "Reason text.",
        "dimensions": {"sentiment": 30, "bias": 90, "objectivity": None, "readability": 60, "propaganda": 95,
                       "headline_accuracy": 70, "source_credibility": 93, "content_quality": 40,
                       "explanations": {"objectivity": "Not scored: test."}},
        "analysis_status": "complete", "analysis_method": "model+rules", "model_version": "pipeline 2.0",
    })
    assert pdf.startswith(b"%PDF")
    text = _text(pdf)
    for needle in ("Flood warning issued", "BBC", "Moderate Risk", "0.42", "81%", "0.30", "Needs verification",
                   "Officials warned residents.", "ANALYSIS METHOD", "pipeline 2.0", "n/a"):
        assert needle in text, needle


def test_report_does_not_invent_missing_values():
    text = _text(build_article_report({"title": "Bare article"}))
    assert "Unavailable" in text
    assert "Not computed" in text and "Not reported" in text
    assert "No dimension scores are recorded" in text
    assert "Low Risk" not in text
