"""
Article analysis pipeline: one function that turns a collected article into the analysis fields
stored in the Supabase ``articles`` table.

Steps
  1. Eight-dimension analysis + rule-based risk (``dimension_service``, mirror of scoring.ts).
  2. Fake-news classifier (BERT-tiny) and sentiment model (DistilBERT SST-2), if available.
  3. Risk combination, risk label, verification flag and analysis status.
  4. Extractive summary when the excerpt is long enough to condense.

Risk methodology (documented in docs/PROJECT_REPORT.md):
  * rule_risk  = 1 - weighted composite of source credibility, propaganda, objectivity, bias and
                 headline accuracy (only dimensions that could be scored; none if < 65% of weight).
  * model_risk = raw softmax score of the classifier's "fake" class (uncalibrated).
  * risk_score = mean of the two when both exist; rule_risk alone when the model is unavailable;
                 none when rule_risk is none (a headline alone is not enough evidence).
  * label      = Low (<= 0.35) / Moderate (<= 0.65) / High; no label when there is no score.
  * needs_verification when: no score, score in 0.40-0.60, excerpt < 150 chars, classifier
    confidence < 0.60, or classifier and rules disagree by >= 0.50.
These are heuristic indicators, not calibrated probabilities.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services import ai_service
from services.dimension_service import (
    MIN_EVIDENCE_CHARS,
    UNCERTAINTY_BAND,
    analyse_text,
    clamp,
    js_round,
    risk_label_for,
    round2,
    rule_risk,
    sentiment_from_score,
    split_sentences,
)

PIPELINE_VERSION = "2.0"
LOW_MODEL_CONFIDENCE = 0.60
DISAGREEMENT = 0.50
SUMMARY_STOPWORDS = set(
    "a an the and or but of to in on at for with by from as is are was were be been it its this that these those "
    "has have had will would could should may might not no he she they we you i his her their our said says".split()
)


def extractive_summary(text: str, max_sentences: int = 2) -> Optional[str]:
    """Frequency-based extractive summary; None unless there are at least three usable sentences.

    Sentences are scored by the average document frequency of their content words and the best
    ones are returned in their original order. Nothing is generated or paraphrased.
    """
    sentences = [s for s in split_sentences(text or "") if len(s) > 30]
    if len(sentences) < 3:
        return None
    tokens = lambda s: [w for w in re.findall(r"[a-z0-9']+", s.lower()) if w not in SUMMARY_STOPWORDS and len(w) > 2]
    freq = Counter(w for s in sentences for w in tokens(s))
    if not freq:
        return None
    top = max(freq.values())

    def score(idx_s):
        idx, s = idx_s
        ws = tokens(s)
        base = sum(freq[w] / top for w in ws) / (len(ws) or 1)
        return base + (0.15 if idx == 0 else 0)  # small lead bias: news puts the key fact first

    best = sorted(sorted(enumerate(sentences), key=score, reverse=True)[:max_sentences])
    return " ".join(s for _, s in best)


def _sentiment_dimension(dims: Dict[str, Any], sentiment_result: Dict[str, Any]) -> str:
    """Replace the lexical sentiment score by the model's when the model ran; return the label."""
    pos = sentiment_result.get("positive_probability")
    if sentiment_result.get("status") == "ok" and isinstance(pos, (int, float)):
        score = clamp(pos * 100, 5, 95)
        dims["sentiment"] = score
        dims["explanations"]["sentiment"] = (
            f"DistilBERT SST-2 rates the headline and excerpt {js_round(pos * 100)}% positive "
            f"(raw model score, uncalibrated); scores between 41 and 59 are read as neutral."
        )
    return sentiment_from_score(dims["sentiment"])


def analyze_article(title: str, excerpt: str, publisher: str, use_models: bool = True) -> Dict[str, Any]:
    """Return the analysis columns for one article (keys match the ``articles`` table)."""
    rules = analyse_text(title, excerpt, publisher)
    dims = rules["dimensions"]
    evidence_chars = rules["evidence_chars"]

    model_text = ai_service.prepare_text(title, excerpt if excerpt != title else "")
    if use_models:
        fake = ai_service.classify_fake_news(model_text)
        senti = ai_service.classify_sentiment(model_text)
    else:
        fake = {"status": "unavailable", "fake_probability": None, "confidence": None, "error": "Models not used."}
        senti = {"status": "unavailable", "positive_probability": None, "error": "Models not used."}

    sentiment = _sentiment_dimension(dims, senti)
    rule_score, _ = rule_risk(dims)
    p_fake = fake.get("fake_probability") if fake.get("status") == "ok" else None
    model_conf = fake.get("confidence") if fake.get("status") == "ok" else None

    reasons = []
    if rule_score is None:
        risk_score = None
        reasons.append(rules["credibility"]["reasoning"])
    elif p_fake is not None:
        risk_score = round2((rule_score + p_fake) / 2)
        reasons.append(
            f"Risk score {risk_score:.2f} = mean of the rule-based risk {rule_score:.2f} and the classifier's "
            f"fake-class score {p_fake:.2f} (raw softmax output, not a calibrated probability)."
        )
    else:
        risk_score = rule_score
        reasons.append(f"Rule-based risk score {rule_score:.2f}; the fake-news classifier was unavailable.")

    label = risk_label_for(risk_score) if risk_score is not None else None
    flags = []
    if risk_score is None:
        flags.append("no risk score could be computed")
    elif UNCERTAINTY_BAND[0] <= risk_score <= UNCERTAINTY_BAND[1]:
        flags.append("the score is inside the 0.40-0.60 uncertainty band")
    if evidence_chars < MIN_EVIDENCE_CHARS:
        flags.append(f"only {evidence_chars} characters of publisher text were available (minimum {MIN_EVIDENCE_CHARS})")
    if model_conf is not None and model_conf < LOW_MODEL_CONFIDENCE:
        flags.append(f"classifier confidence {model_conf:.2f} is below {LOW_MODEL_CONFIDENCE:.2f}")
    if p_fake is not None and rule_score is not None and abs(p_fake - rule_score) >= DISAGREEMENT:
        flags.append("the classifier and the rule-based indicators disagree strongly")
    needs_verification = bool(flags)
    if flags:
        reasons.append("Needs verification: " + "; ".join(flags) + ".")

    if risk_score is None:
        status = "unavailable"
    elif fake.get("status") == "ok" and senti.get("status") == "ok":
        status = "complete"
    else:
        status = "partial"

    models_used = []
    if fake.get("status") == "ok":
        models_used.append(ai_service.FAKE_NEWS_MODEL)
    if senti.get("status") == "ok":
        models_used.append(ai_service.SENTIMENT_MODEL)
    method = "model+rules" if models_used else "rules"

    summary = extractive_summary(excerpt)
    return {
        "sentiment": sentiment,
        "dimensions": dims,
        "risk_score": risk_score,
        "credibility_label": label,
        "needs_verification": needs_verification,
        "confidence_level": model_conf,
        "model_fake_probability": p_fake,
        "is_fake": (p_fake >= 0.5) if p_fake is not None else None,
        # Legacy column: complement of the classifier's fake score (kept for older dashboards).
        "credibility_score": round(1 - p_fake, 4) if p_fake is not None else None,
        "ai_reasoning": " ".join(reasons),
        "ai_summary": summary,
        "summary_method": "extractive" if summary else None,
        "analysis_status": status,
        "analysis_method": method,
        "model_version": f"pipeline {PIPELINE_VERSION}; " + (", ".join(models_used) if models_used else "rules only"),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "_model_errors": {k: v.get("error") for k, v in (("fake_news", fake), ("sentiment", senti)) if v.get("error")},
    }
