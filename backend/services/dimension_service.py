"""
Eight-dimension content analysis and rule-based credibility risk.

This module is a line-by-line port of ``frontend/src/lib/scoring.ts`` so that articles scored by
the backend ingestion pipeline and articles scored in the browser (live RSS feeds, external search)
use one scoring system, not two. ``shared/scoring_vectors.json`` holds reference inputs and the
outputs of the TypeScript implementation; ``tests/test_dimension_service.py`` and
``frontend/src/lib/scoringParity.test.ts`` both check against it.

Score direction (0-100) per dimension:
  sentiment           0 = strongly negative tone, 50 = neutral, 100 = strongly positive
  bias                100 = no loaded or one-sided language detected
  objectivity         100 = no evaluative / subjective wording detected
  readability         Flesch Reading Ease (higher = easier to read, not "better")
  propaganda          100 = no manipulation or sensationalism markers detected
  headline_accuracy   share of headline terms supported by the excerpt
  source_credibility  publisher reputation from a hand-curated reference table
  content_quality     completeness of the supplied excerpt (not the full article)

A dimension that cannot be measured from the available text is ``None`` together with an
explanation; no placeholder number is ever substituted. Nothing here is a calibrated probability.
"""
from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple

DIMENSION_KEYS = [
    "sentiment", "bias", "objectivity", "readability",
    "propaganda", "headline_accuracy", "source_credibility", "content_quality",
]
RISK_LABELS = ["Low Risk", "Moderate Risk", "High Risk"]

# Hand-curated publisher reference table (same as scoring.ts).
PUBLISHER_REPUTATION: List[Tuple[str, int]] = [
    ("reuters", 95), ("associated press", 95), ("bbc", 93), ("guardian", 90), ("the hindu", 90),
    ("financial times", 93), ("bloomberg", 92), ("indian express", 88), ("al jazeera", 86), ("aljazeera", 86),
    ("ndtv", 84), ("mint", 86), ("techcrunch", 84), ("cnn", 86), ("yahoo", 78),
]

POSITIVE = ["surge", "gain", "gains", "milestone", "breakthrough", "success", "record", "win", "wins", "won", "growth", "rise", "rises", "improve", "improves", "celebrate", "recovery", "hope", "boost", "praise", "award", "agreement", "deal"]
NEGATIVE = ["crash", "collapse", "death", "dead", "dies", "died", "killed", "kill", "fraud", "theft", "warning", "ban", "threat", "scandal", "loss", "arrest", "arrested", "panic", "terror", "attack", "war", "crisis", "fall", "falls", "cut", "cuts", "fear", "fears", "violence", "shooting", "injured", "sanction", "sanctions", "protest", "accused", "condemns"]
SUBJECTIVE = ["obviously", "clearly", "terrible", "wonderful", "disastrous", "miracle", "heroic", "shameful", "absurd", "brilliant", "outrageous", "pathetic", "incredible", "unbelievable", "amazing", "horrific", "disgraceful"]
LOADED = ["regime", "radical", "extremist", "thugs", "elites", "puppet", "traitor", "propaganda", "so-called", "mob", "witch hunt", "invasion"]
ATTRIBUTION = ["said", "says", "according to", "told", "stated", "reported", "announced", "confirmed", "spokesperson", "officials"]
MANIPULATION = [
    re.compile(r"\bshocking\b", re.I | re.A), re.compile(r"\byou won'?t believe\b", re.I | re.A), re.compile(r"\bsecret\b", re.I | re.A),
    re.compile(r"\burgent\b", re.I | re.A), re.compile(r"\bexposed\b", re.I | re.A), re.compile(r"\boutrage\b", re.I | re.A),
    re.compile(r"!{2,}"), re.compile(r"\bmust see\b", re.I | re.A), re.compile(r"\bgoes viral\b", re.I | re.A),
    re.compile(r"\bdestroys\b", re.I | re.A), re.compile(r"\bslams\b", re.I | re.A),
]
STOPWORDS = set(
    "a an the and or but of to in on at for with by from as is are was were be been it its this that these those "
    "after before over under into about than then will would could should may might has have had not no yes up out "
    "new says say said what how why who when where which".split(" ")
)

MIN_EVIDENCE_CHARS = 150
RISK_WEIGHTS = {
    "source_credibility": 0.35,
    "propaganda": 0.2,
    "objectivity": 0.15,
    "bias": 0.15,
    "headline_accuracy": 0.15,
}
MIN_RISK_WEIGHT = 0.65
UNCERTAINTY_BAND = (0.4, 0.6)

_TERM_PATTERNS: Dict[str, re.Pattern] = {}


def js_round(x: float) -> int:
    """JavaScript ``Math.round`` (halves round towards +infinity), for parity with scoring.ts."""
    return int(math.floor(x + 0.5))


def round2(x: float) -> float:
    return js_round(x * 100) / 100


def clamp(n: float, lo: float = 0, hi: float = 100) -> int:
    return max(int(lo), min(int(hi), js_round(n)))


def _words(text: str) -> List[str]:
    return [w for w in re.split(r"\s+", re.sub(r"[^a-z0-9\s'-]", " ", text.lower())) if w]


def _term_pattern(term: str) -> re.Pattern:
    if term not in _TERM_PATTERNS:
        _TERM_PATTERNS[term] = re.compile(term if " " in term else rf"\b{term}\b", re.I | re.A)
    return _TERM_PATTERNS[term]


def _count_hits(text: str, terms: List[str]) -> int:
    return sum(1 for t in terms if _term_pattern(t).search(text))


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w, count=1)
    w = re.sub(r"^y", "", w, count=1)
    m = re.findall(r"[aeiouy]{1,2}", w)
    return max(1, len(m) if m else 1)


def flesch_reading_ease(text: str) -> float:
    ws = [w for w in re.split(r"\s+", text.strip()) if w]
    if not ws:
        return 50.0
    sentences = max(1, len([s for s in re.split(r"[.!?]+", text) if s.strip()]))
    syl = sum(_syllables(w) for w in ws)
    return 206.835 - 1.015 * (len(ws) / sentences) - 84.6 * (syl / len(ws))


def publisher_reputation(publisher: str) -> Optional[int]:
    p = (publisher or "").lower()
    for key, score in PUBLISHER_REPUTATION:
        if key in p:
            return score
    return None


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'‘])", text or "")
    return [s.strip() for s in parts if s.strip()]


def risk_label_for(score: float) -> str:
    if score <= 0.35:
        return "Low Risk"
    if score <= 0.65:
        return "Moderate Risk"
    return "High Risk"


def sentiment_from_score(score: float) -> str:
    return "positive" if score >= 60 else "negative" if score <= 40 else "neutral"


def rule_risk(dims: Dict[str, Any]) -> Tuple[Optional[float], float]:
    """Inverse of the weighted composite of the scoreable credibility dimensions.

    Returns ``(score, available_weight)``; ``score`` is None when too little weight is scoreable.
    """
    weight = 0.0
    total = 0.0
    for key, w in RISK_WEIGHTS.items():
        v = dims.get(key)
        if isinstance(v, (int, float)):
            weight += w
            total += v * w
    weight = round2(weight)
    if weight < MIN_RISK_WEIGHT:
        return None, weight
    composite = total / weight / 100
    return round2(1 - composite), weight


def analyse_text(title: str, excerpt: str, publisher: str) -> Dict[str, Any]:
    """Score the eight dimensions and the rule-based risk for one article (mirror of ``analyseText``)."""
    title = title or ""
    excerpt = excerpt or ""
    body = excerpt if excerpt and excerpt != title else ""
    combined = f"{title}. {body}"
    evidence_chars = len(body)

    # 1. Sentiment
    pos = _count_hits(combined, POSITIVE)
    neg = _count_hits(combined, NEGATIVE)
    sentiment_score = clamp(50 + (pos - neg) * 9, 5, 95)
    sentiment = sentiment_from_score(sentiment_score)
    sentiment_expl = (
        f"Balanced or descriptive tone ({pos} positive, {neg} negative cue words)."
        if sentiment == "neutral"
        else f"Predominantly {sentiment} framing: {pos} positive and {neg} negative cue words."
    )

    # 2. Objectivity
    subj = _count_hits(combined, SUBJECTIVE)
    objectivity = clamp(92 - subj * 14, 20)
    objectivity_expl = (
        f"{subj} evaluative adjective{'s' if subj > 1 else ''} found; wording leans on judgement rather than fact."
        if subj > 0 else "No evaluative adjectives from the reference lexicon were found."
    )

    # 3. Bias
    loaded = _count_hits(combined, LOADED)
    attributed = _count_hits(combined, ATTRIBUTION) > 0
    bias = clamp(90 - loaded * 15 - (0 if (attributed or not body) else 6), 20)
    if loaded > 0:
        bias_expl = f"{loaded} loaded or partisan term{'s' if loaded > 1 else ''} detected."
    elif attributed:
        bias_expl = "No loaded terms; claims carry explicit attribution."
    else:
        bias_expl = "No loaded terms detected; the excerpt does not attribute its claims."

    # 4. Readability
    flesch = flesch_reading_ease(combined)
    readability = clamp(flesch) if body else None
    if readability is None:
        readability_expl = "Not scored: a headline alone is too short for a reading-ease formula."
    else:
        tier = ("plain, accessible prose" if readability >= 60
                else "moderately demanding prose" if readability >= 40 else "dense, technical prose")
        readability_expl = f"Flesch Reading Ease {js_round(flesch)} — {tier}."

    # 5. Propaganda / manipulation
    manip = sum(1 for p in MANIPULATION if p.search(combined))
    shouting = len(re.findall(r"\b[A-Z]{5,}\b", title, re.A))
    propaganda = clamp(95 - manip * 22 - shouting * 10, 5)
    markers = manip + shouting
    propaganda_expl = (
        f"{markers} sensationalism marker{'s' if markers > 1 else ''} (clickbait phrasing, shouting capitals or stacked exclamation)."
        if markers > 0 else "No clickbait phrasing, shouting capitals or stacked exclamation detected."
    )

    # 6. Headline accuracy
    head_terms = [w for w in _words(title) if len(w) > 3 and w not in STOPWORDS]
    body_terms = set(_words(body))
    matched = sum(1 for t in head_terms if t in body_terms or re.sub(r"s$", "", t, count=1) in body_terms)
    ratio = matched / len(head_terms) if head_terms else 0
    headline_accuracy = clamp(45 + ratio * 50) if (body and head_terms) else None
    if not body:
        headline_expl = "Not scored: no excerpt was supplied, so the headline could not be checked against body text."
    elif head_terms:
        headline_expl = f"{matched} of {len(head_terms)} key headline terms appear in the excerpt."
    else:
        headline_expl = "Not scored: the headline has no key terms to check."

    # 7. Source credibility
    rep = publisher_reputation(publisher)
    source_expl = (
        f"{publisher} is listed in the publication's reference table of established newsrooms."
        if rep is not None else f"Not scored: {publisher or 'this publisher'} is not in the reference table."
    )

    # 8. Content quality
    sentences = len(split_sentences(body))
    content_quality = clamp(35 + min(evidence_chars, 600) / 12 + min(sentences, 4) * 5) if body else None
    if not body:
        content_expl = "Not scored: the feed supplied a headline only."
    elif evidence_chars < MIN_EVIDENCE_CHARS:
        content_expl = f"Feed supplied only {evidence_chars} characters; quality of the full article cannot be judged."
    else:
        content_expl = f"Feed excerpt of {evidence_chars} characters across {sentences} sentence{'' if sentences == 1 else 's'}."

    dimensions: Dict[str, Any] = {
        "sentiment": sentiment_score,
        "bias": bias,
        "objectivity": objectivity,
        "readability": readability,
        "propaganda": propaganda,
        "headline_accuracy": headline_accuracy,
        "source_credibility": rep,
        "content_quality": content_quality,
        "explanations": {
            "sentiment": sentiment_expl,
            "bias": bias_expl,
            "objectivity": objectivity_expl,
            "readability": readability_expl,
            "propaganda": propaganda_expl,
            "headline_accuracy": headline_expl,
            "source_credibility": source_expl,
            "content_quality": content_expl,
        },
    }

    score, available_weight = rule_risk(dimensions)
    label = "Unavailable" if score is None else risk_label_for(score)
    ambiguous = score is not None and UNCERTAINTY_BAND[0] <= score <= UNCERTAINTY_BAND[1]
    thin = evidence_chars < MIN_EVIDENCE_CHARS
    needs_verification = score is None or ambiguous or thin

    reasons = [
        f"No risk score: the scoreable dimensions carry only {js_round(available_weight * 100)}% of the risk weight "
        f"(minimum {js_round(MIN_RISK_WEIGHT * 100)}%)."
        if score is None else f"Rule-based risk score {score:.2f} ({label})."
    ]
    if thin:
        reasons.append(f"Only {evidence_chars} characters of publisher text were available, below the {MIN_EVIDENCE_CHARS}-character evidence threshold.")
    if ambiguous:
        reasons.append("The score falls inside the 0.40–0.60 uncertainty band.")
    if markers > 0:
        reasons.append("Sensational framing markers were found.")
    if rep is None:
        reasons.append("The publisher is not in the reference reputation table.")

    return {
        "sentiment": sentiment,
        "dimensions": dimensions,
        "credibility": {
            "label": label,
            "score": score,
            "confidence": None,
            "needs_verification": needs_verification,
            "reasoning": " ".join(reasons),
        },
        "evidence_chars": evidence_chars,
    }
