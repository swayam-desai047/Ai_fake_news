import json
from pathlib import Path

import pytest

from services.dimension_service import (
    DIMENSION_KEYS, analyse_text, risk_label_for, rule_risk, sentiment_from_score,
)

VECTORS = json.loads((Path(__file__).resolve().parents[2] / "shared" / "scoring_vectors.json").read_text())


def _camel_to_backend(expected):
    """scoring.ts uses needsVerification; the Python port uses needs_verification."""
    cred = dict(expected["credibility"])
    cred["needs_verification"] = cred.pop("needsVerification")
    return {"sentiment": expected["sentiment"], "dimensions": expected["dimensions"], "credibility": cred}


@pytest.mark.parametrize("vector", VECTORS, ids=[v["title"][:30] for v in VECTORS])
def test_matches_typescript_implementation(vector):
    got = analyse_text(vector["title"], vector["excerpt"], vector["publisher"])
    got.pop("evidence_chars")
    assert got == _camel_to_backend(vector["expected"])


def test_all_eight_dimensions_and_explanations_present():
    r = analyse_text("Flood warning issued", "Officials warned residents near the river to prepare for evacuation, the agency said.", "BBC")
    assert set(DIMENSION_KEYS) <= set(r["dimensions"])
    assert set(r["dimensions"]["explanations"]) == set(DIMENSION_KEYS)
    for k in DIMENSION_KEYS:
        v = r["dimensions"][k]
        assert v is None or 0 <= v <= 100


def test_headline_only_article_is_not_given_artificial_scores():
    r = analyse_text("Markets fall sharply", "", "Some Unknown Blog")
    d = r["dimensions"]
    assert d["headline_accuracy"] is None
    assert d["content_quality"] is None
    assert d["readability"] is None
    assert d["source_credibility"] is None
    assert r["credibility"]["score"] is None
    assert r["credibility"]["label"] == "Unavailable"
    assert r["credibility"]["needs_verification"] is True
    assert d["explanations"]["headline_accuracy"].startswith("Not scored")


def test_unknown_publisher_has_no_source_score():
    r = analyse_text("Council approves new park", "The city council voted to approve a new park, a spokesperson said on Monday evening after a long meeting with residents.", "Local Gazette")
    assert r["dimensions"]["source_credibility"] is None
    assert r["credibility"]["score"] is not None  # remaining weight 0.65 is enough


def test_risk_thresholds():
    assert risk_label_for(0.35) == "Low Risk"
    assert risk_label_for(0.36) == "Moderate Risk"
    assert risk_label_for(0.65) == "Moderate Risk"
    assert risk_label_for(0.66) == "High Risk"


def test_rule_risk_requires_enough_weight():
    assert rule_risk({"propaganda": 90, "objectivity": 90, "bias": 90})[0] is None
    score, weight = rule_risk({"propaganda": 100, "objectivity": 100, "bias": 100, "source_credibility": 100, "headline_accuracy": 100})
    assert score == 0.0 and weight == 1.0


def test_sentiment_thresholds():
    assert sentiment_from_score(60) == "positive"
    assert sentiment_from_score(59) == "neutral"
    assert sentiment_from_score(40) == "negative"


def test_backend_feed_name_aljazeera_is_in_reference_table():
    from services.dimension_service import publisher_reputation
    assert publisher_reputation("AlJazeera") == publisher_reputation("Al Jazeera") == 86
