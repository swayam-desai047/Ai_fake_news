"""
Transformer model inference: fake-news classification and sentiment.

Models (unchanged from the original project):
  * ``mrm8488/bert-tiny-finetuned-fake-news-detection`` - binary text classifier.
  * ``distilbert-base-uncased-finetuned-sst-2-english`` - binary (POSITIVE/NEGATIVE) sentiment.

Label mapping of the fake-news model
------------------------------------
The model's ``config.json`` has no ``id2label`` entry, so the pipeline reports the generic labels
``LABEL_0`` and ``LABEL_1`` and the model card does not document which one is "fake". The original
code treated ``LABEL_1`` as fake; published third-party usage of this model uses the same mapping
(LABEL_0 = real, LABEL_1 = fake). It is kept as the default but is configurable through
``FAKE_NEWS_FAKE_LABEL`` and can be checked on known examples with ``scripts/validate_models.py``.

Design rules
------------
* Models are loaded lazily on first use, not at import time, so the API and the tests start
  without downloading weights.
* If a model cannot be loaded or fails at inference, its outputs are ``None`` and the returned
  ``status`` says so. No placeholder score (such as 0.5) is ever returned in its place.
* Softmax scores are reported as raw, uncalibrated model outputs, never as probabilities of truth.
* Sentiment is kept separate from fake-news classification.
"""
from __future__ import annotations

import logging
import os
import threading
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

FAKE_NEWS_MODEL = os.getenv("FAKE_NEWS_MODEL", "mrm8488/bert-tiny-finetuned-fake-news-detection")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
FAKE_LABEL = os.getenv("FAKE_NEWS_FAKE_LABEL", "LABEL_1").upper()
REAL_LABEL = os.getenv("FAKE_NEWS_REAL_LABEL", "LABEL_0").upper()
MODELS_ENABLED = os.getenv("ENABLE_MODELS", "1") not in ("0", "false", "False")
MAX_TOKENS = 512
MAX_INPUT_CHARS = 20_000

_lock = threading.Lock()
_pipelines: Dict[str, Any] = {}
_load_errors: Dict[str, str] = {}


def _load(kind: str):
    """Load (once) and return the pipeline for ``kind`` ('fake_news' or 'sentiment'), or None."""
    if kind in _pipelines:
        return _pipelines[kind]
    if kind in _load_errors:
        return None
    with _lock:
        if kind in _pipelines:
            return _pipelines[kind]
        if not MODELS_ENABLED:
            _load_errors[kind] = "Model inference is disabled (ENABLE_MODELS=0)."
            return None
        try:
            from transformers import pipeline  # imported lazily: heavy dependency

            model = FAKE_NEWS_MODEL if kind == "fake_news" else SENTIMENT_MODEL
            logger.info("Loading %s model %s", kind, model)
            _pipelines[kind] = pipeline("text-classification", model=model, top_k=None)
            return _pipelines[kind]
        except Exception as exc:  # missing package, no network, corrupt cache...
            logger.error("Failed to load %s model: %s", kind, exc)
            _load_errors[kind] = f"{type(exc).__name__}: could not load model."
            return None


def model_status() -> Dict[str, Any]:
    """Load state of both models, without forcing a load."""
    def one(kind: str, name: str) -> Dict[str, Any]:
        state = "loaded" if kind in _pipelines else "failed" if kind in _load_errors else "not_loaded"
        return {"model": name, "state": state, "error": _load_errors.get(kind)}
    return {
        "fake_news": {**one("fake_news", FAKE_NEWS_MODEL), "fake_label": FAKE_LABEL},
        "sentiment": one("sentiment", SENTIMENT_MODEL),
        "enabled": MODELS_ENABLED,
    }


def _scores(raw: Any) -> Dict[str, float]:
    """Normalise pipeline output (list of dicts, possibly nested once) into {LABEL: score}."""
    if isinstance(raw, list) and raw and isinstance(raw[0], list):
        raw = raw[0]
    if not isinstance(raw, list):
        raise ValueError("unexpected pipeline output")
    out: Dict[str, float] = {}
    for item in raw:
        label = str(item["label"]).upper()
        out[label] = float(item["score"])
    return out


def _run(pipe, text: str) -> Dict[str, float]:
    return _scores(pipe(text, truncation=True, max_length=MAX_TOKENS))


def prepare_text(title: str, body: str) -> str:
    text = ". ".join(p.strip() for p in (title or "", body or "") if p and p.strip())
    return " ".join(text.split())[:MAX_INPUT_CHARS]


def classify_fake_news(text: str) -> Dict[str, Any]:
    """Run the fake-news classifier. ``fake_probability`` is the raw softmax score of the fake label."""
    result: Dict[str, Any] = {"status": "unavailable", "fake_probability": None, "confidence": None,
                              "predicted_label": None, "error": None}
    if not text or not text.strip():
        result["error"] = "No text to classify."
        return result
    pipe = _load("fake_news")
    if pipe is None:
        result["error"] = _load_errors.get("fake_news", "Model unavailable.")
        return result
    try:
        scores = _run(pipe, text)
    except Exception as exc:
        logger.error("Fake-news inference failed: %s", exc)
        result["error"] = "Inference failed."
        return result

    fake = scores.get(FAKE_LABEL, scores.get("FAKE"))
    real = scores.get(REAL_LABEL, scores.get("REAL", scores.get("TRUE")))
    if fake is None and real is not None:
        fake = 1.0 - real
    if fake is None:
        logger.error("Unexpected fake-news labels %s (expected %s/%s)", list(scores), FAKE_LABEL, REAL_LABEL)
        result["error"] = f"Unexpected model labels: {sorted(scores)}."
        return result
    fake = max(0.0, min(1.0, fake))
    result.update({
        "status": "ok",
        "fake_probability": round(fake, 4),
        "confidence": round(max(fake, 1.0 - fake), 4),
        "predicted_label": "fake" if fake >= 0.5 else "real",
    })
    return result


def classify_sentiment(text: str) -> Dict[str, Any]:
    """Run SST-2 sentiment. Returns the raw POSITIVE softmax score; the label is derived elsewhere."""
    result: Dict[str, Any] = {"status": "unavailable", "positive_probability": None, "error": None}
    if not text or not text.strip():
        result["error"] = "No text to classify."
        return result
    pipe = _load("sentiment")
    if pipe is None:
        result["error"] = _load_errors.get("sentiment", "Model unavailable.")
        return result
    try:
        scores = _run(pipe, text)
    except Exception as exc:
        logger.error("Sentiment inference failed: %s", exc)
        result["error"] = "Inference failed."
        return result
    pos = scores.get("POSITIVE")
    if pos is None and "NEGATIVE" in scores:
        pos = 1.0 - scores["NEGATIVE"]
    if pos is None:
        result["error"] = f"Unexpected model labels: {sorted(scores)}."
        return result
    result.update({"status": "ok", "positive_probability": round(max(0.0, min(1.0, pos)), 4)})
    return result


def analyze_article_text(text: str) -> Dict[str, Any]:
    """Both models on one text (used by the /analyze endpoint and the ingestion pipeline)."""
    return {"fake_news": classify_fake_news(text), "sentiment": classify_sentiment(text),
            "models": {"fake_news": FAKE_NEWS_MODEL, "sentiment": SENTIMENT_MODEL}}


def reset_for_tests(pipelines: Optional[Dict[str, Any]] = None, errors: Optional[Dict[str, str]] = None) -> None:
    """Replace the loaded pipelines (tests inject fakes so no weights are downloaded)."""
    _pipelines.clear()
    _load_errors.clear()
    _pipelines.update(pipelines or {})
    _load_errors.update(errors or {})


if __name__ == "__main__":
    import json
    sample = "Shocking news! The earth is actually flat and scientists have been lying to us."
    print(json.dumps(analyze_article_text(sample), indent=2))
