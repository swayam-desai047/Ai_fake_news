"""
Cross-source event grouping (mirror of ``frontend/src/lib/clustering.ts``).

Headline (counted twice) + lead sentence of the excerpt are turned into TF-IDF vectors and
compared by cosine similarity. Grouping is seed-based: every candidate is compared with the
group's seed only, so unrelated stories cannot be chained together through a shared middle
article. A candidate must also be published within ``MAX_GAP_HOURS`` of the seed. Only one report
per publisher is kept and a group needs at least two distinct publishers.

Text similarity says that reports are about the same event. It does not verify any claim, and
agreement between sources is not treated as evidence that a report is true.
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

STOPWORDS = set((
    "a an the and or but of to in on at for with by from as is are was were be been being it its this that these those after before "
    "over under into about than then will would could should may might has have had not no new says say said what how why who whom when "
    "where which while amid against more most first last over out up down off just also us uk his her their our your they them he she we "
    "you i live latest news video watch report reports year years day days week weeks says one two three can get gets make makes"
).split(" "))

SIMILARITY_THRESHOLD = 0.32
WINDOW_HOURS = 48
MAX_GAP_HOURS = 36
MIN_PUBLISHERS = 2


def tokens(text: str) -> List[str]:
    text = re.sub(r"[’']s\b", "", (text or "").lower())
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    out = []
    for t in re.split(r"\s+", text):
        t = re.sub(r"^-+|-+$", "", t)
        if len(t) > 2 and t not in STOPWORDS and not re.fullmatch(r"\d+", t):
            out.append(t)
    return out


def lead_sentence(text: str) -> str:
    m = re.match(r"^[\s\S]{0,240}?[.!?](\s|$)", text or "")
    return m.group(0) if m else (text or "")[:240]


def vectorise(docs: List[List[str]]) -> List[Dict[str, float]]:
    """TF-IDF with the same smoothing as clustering.ts: w = tf * ln((1+n)/(1+df) + 1), L2-normalised."""
    df: Dict[str, int] = {}
    for doc in docs:
        for t in set(doc):
            df[t] = df.get(t, 0) + 1
    n = len(docs)
    vecs = []
    for doc in docs:
        tf: Dict[str, int] = {}
        for t in doc:
            tf[t] = tf.get(t, 0) + 1
        v = {t: f * math.log((1 + n) / (1 + df[t]) + 1) for t, f in tf.items()}
        norm = math.sqrt(sum(w * w for w in v.values())) or 1.0
        vecs.append({t: w / norm for t, w in v.items()})
    return vecs


def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    small, large = (a, b) if len(a) < len(b) else (b, a)
    return sum(w * large.get(t, 0.0) for t, w in small.items())


def _time(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def cluster_articles(articles: List[Dict[str, Any]], now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Group article rows (keys: id, title, content_summary, source_domain, published_at).

    Returns ``[{group_id, event_title, article_ids, publishers, similarity}]`` sorted by publisher count.
    """
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=WINDOW_HOURS)
    pool = [a for a in articles if (_time(a.get("published_at")) or now) >= cutoff]
    if len(pool) < 2:
        return []

    times = [_time(a.get("published_at")) for a in pool]
    vecs = vectorise([tokens(f"{a['title']} {a['title']} {lead_sentence(a.get('content_summary') or '')}") for a in pool])
    assigned: set = set()
    groups = []
    for i in range(len(pool)):
        if i in assigned:
            continue
        members = [(i, 1.0)]
        for j in range(i + 1, len(pool)):
            if j in assigned:
                continue
            if times[i] and times[j] and abs((times[i] - times[j]).total_seconds()) > MAX_GAP_HOURS * 3600:
                continue
            sim = cosine(vecs[i], vecs[j])
            if sim >= SIMILARITY_THRESHOLD:
                members.append((j, sim))
        by_publisher: Dict[str, tuple] = {}
        for idx, sim in members:
            pub = (pool[idx].get("source_domain") or "").strip() or "Unknown publisher"
            by_publisher.setdefault(pub, (idx, sim))
        if len(by_publisher) < MIN_PUBLISHERS:
            continue
        kept = list(by_publisher.values())
        assigned.update(idx for idx, _ in kept)
        ids = [str(pool[idx]["id"]) for idx, _ in kept]
        sims = [sim for idx, sim in kept if idx != i]
        groups.append({
            "group_id": f"ev-{sorted(ids)[0]}",
            "event_title": pool[i]["title"],
            "article_ids": ids,
            "publishers": list(by_publisher.keys()),
            "similarity": round(min(sims), 3) if sims else None,
        })
    return sorted(groups, key=lambda g: -len(g["publishers"]))


def assignments(articles: List[Dict[str, Any]], now: Optional[datetime] = None) -> Dict[str, Dict[str, Optional[str]]]:
    """Map every article id in the window to its new ``{group_id, event_title}`` (None when ungrouped)."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=WINDOW_HOURS)
    out: Dict[str, Dict[str, Optional[str]]] = {
        str(a["id"]): {"group_id": None, "event_title": None}
        for a in articles if (_time(a.get("published_at")) or now) >= cutoff
    }
    for g in cluster_articles(articles, now):
        for aid in g["article_ids"]:
            out[aid] = {"group_id": g["group_id"], "event_title": g["event_title"]}
    return out
