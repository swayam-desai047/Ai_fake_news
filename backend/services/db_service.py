"""
Supabase persistence for articles: duplicate checks, analysed inserts, cross-source group updates
and read helpers used by the API.

Writes need the service-role key (``SUPABASE_SERVICE_ROLE_KEY``); with migration
``02_integrity_and_security.sql`` applied, the public (anon/publishable) key can only read.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from db.supabase import get_supabase_client
from services.analysis_pipeline import analyze_article
from services.clustering_service import WINDOW_HOURS, assignments
from services.rss_fetcher import normalise_title, normalise_url

logger = logging.getLogger(__name__)

# Columns written by the pipeline. Columns added by migration 02 are listed separately so the
# service still works (with a warning) against a database where it has not been applied yet.
BASE_COLUMNS = [
    "title", "source_domain", "source_url", "content_summary", "category", "published_at",
    "sentiment", "is_fake", "credibility_score", "ai_reasoning", "risk_score", "confidence_level",
    "credibility_label", "needs_verification", "ai_summary", "dimensions", "group_id", "event_title",
]
V2_COLUMNS = ["analysis_status", "analysis_method", "model_version", "analyzed_at", "summary_method",
              "model_fake_probability"]


def get_article_by_id(article_id: str) -> Optional[Dict[str, Any]]:
    """Fetch one article by UUID; None when absent. Raises on database errors."""
    client = get_supabase_client()
    response = client.table("articles").select("*").eq("id", article_id).limit(1).execute()
    return response.data[0] if response.data else None


def get_grouped_articles(limit: int = 300) -> List[Dict[str, Any]]:
    """Articles sharing a group_id, assembled into groups with publisher-wise coverage."""
    client = get_supabase_client()
    response = (client.table("articles").select("*").not_.is_("group_id", "null")
                .order("published_at", desc=True).limit(limit).execute())
    groups: Dict[str, Dict[str, Any]] = {}
    for article in response.data or []:
        gid = article.get("group_id")
        g = groups.setdefault(gid, {"group_id": gid, "event_title": article.get("event_title") or article.get("title"),
                                    "articles": [], "publishers": []})
        g["articles"].append(article)
        pub = article.get("source_domain") or "Unknown publisher"
        if pub not in g["publishers"]:
            g["publishers"].append(pub)
    result = []
    for g in groups.values():
        g["publisher_count"] = len(g["publishers"])
        g["coverage"] = [
            {"publisher": p, "articles": [
                {"id": a["id"], "title": a["title"], "published_at": a.get("published_at"),
                 "credibility_label": a.get("credibility_label"), "sentiment": a.get("sentiment")}
                for a in g["articles"] if (a.get("source_domain") or "Unknown publisher") == p]}
            for p in g["publishers"]
        ]
        result.append(g)
    return sorted(result, key=lambda g: -g["publisher_count"])


def existing_keys(client, articles: List[Dict]) -> Tuple[Set[str], Set[str]]:
    """Normalised titles and URLs of the batch that are already stored."""
    titles = list({a["title"] for a in articles})
    # Raw and normalised forms, so a stored URL also matches an incoming copy with tracking parameters.
    urls = list({u for a in articles if a.get("source_url") for u in (a["source_url"], normalise_url(a["source_url"]))})
    seen_titles: Set[str] = set()
    seen_urls: Set[str] = set()
    for i in range(0, len(titles), 50):
        rows = client.table("articles").select("title").in_("title", titles[i:i + 50]).execute().data or []
        seen_titles.update(normalise_title(r["title"]) for r in rows)
    for i in range(0, len(urls), 50):
        rows = client.table("articles").select("source_url").in_("source_url", urls[i:i + 50]).execute().data or []
        seen_urls.update(normalise_url(r["source_url"]) for r in rows if r.get("source_url"))
    return seen_titles, seen_urls


def build_record(article: Dict[str, Any], analysis: Dict[str, Any], include_v2: bool = True) -> Dict[str, Any]:
    """Merge a collected article with its analysis into a row; never fills in missing analysis."""
    merged = {**article, **{k: v for k, v in analysis.items() if not k.startswith("_")}}
    columns = BASE_COLUMNS + (V2_COLUMNS if include_v2 else [])
    record = {c: merged.get(c) for c in columns if c in merged}
    record.setdefault("category", "general")
    if not record.get("published_at"):
        record.pop("published_at", None)  # let the column default (ingestion time) apply
    return record


def _insert(client, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Insert, ignoring a title already present (UNIQUE constraint); falls back to pre-v2 columns."""
    try:
        res = client.table("articles").upsert(record, on_conflict="title", ignore_duplicates=True).execute()
    except Exception as exc:
        missing_v2 = any(c in str(exc) for c in V2_COLUMNS)
        if not missing_v2:
            raise
        logger.warning("Migration 02 not applied; storing without analysis_status/model_version columns.")
        legacy = {k: v for k, v in record.items() if k not in V2_COLUMNS}
        res = client.table("articles").upsert(legacy, on_conflict="title", ignore_duplicates=True).execute()
    return res.data[0] if res.data else None


def store_articles_in_db(articles: List[Dict], analyse: Callable[..., Dict[str, Any]] = analyze_article,
                         client=None) -> Dict[str, int]:
    """Analyse and store new articles. Already-stored articles are skipped before analysis.

    Returns counts: received, duplicates, inserted, failed, needs_verification, unavailable.
    """
    client = client or get_supabase_client()
    stats = {"received": len(articles), "duplicates": 0, "inserted": 0, "failed": 0,
             "needs_verification": 0, "unavailable": 0}
    if not articles:
        return stats
    seen_titles, seen_urls = existing_keys(client, articles)
    for article in articles:
        if normalise_title(article["title"]) in seen_titles or normalise_url(article.get("source_url", "")) in seen_urls:
            stats["duplicates"] += 1
            continue
        try:
            analysis = analyse(article["title"], article.get("content_summary", ""), article.get("source_domain", ""))
            saved = _insert(client, build_record(article, analysis))
            if saved:
                stats["inserted"] += 1
                stats["needs_verification"] += int(bool(analysis.get("needs_verification")))
                stats["unavailable"] += int(analysis.get("analysis_status") == "unavailable")
            else:
                stats["duplicates"] += 1
            seen_titles.add(normalise_title(article["title"]))
            seen_urls.add(normalise_url(article.get("source_url", "")))
        except Exception as exc:
            stats["failed"] += 1
            logger.error("Could not store article %r: %s", article.get("title"), exc)
    logger.info("Ingestion: %s", stats)
    return stats


def update_groups(client=None, now: Optional[datetime] = None) -> Dict[str, int]:
    """Re-cluster recent articles and write changed group_id / event_title values."""
    client = client or get_supabase_client()
    now = now or datetime.now(timezone.utc)
    since = (now - timedelta(hours=WINDOW_HOURS)).isoformat()
    rows = (client.table("articles").select("id, title, content_summary, source_domain, published_at, group_id, event_title")
            .gte("published_at", since).limit(1000).execute().data or [])
    new = assignments(rows, now)
    changed = 0
    for row in rows:
        target = new.get(str(row["id"]))
        if target is None:
            continue
        if row.get("group_id") != target["group_id"] or row.get("event_title") != target["event_title"]:
            client.table("articles").update(target).eq("id", row["id"]).execute()
            changed += 1
    groups = len({v["group_id"] for v in new.values() if v["group_id"]})
    logger.info("Grouping: %d articles in window, %d groups, %d rows updated", len(rows), groups, changed)
    return {"articles": len(rows), "groups": groups, "updated": changed}


def reanalyze(ids: Iterable[str], client=None, analyse: Callable[..., Dict[str, Any]] = analyze_article) -> int:
    """Re-run the analysis on stored articles (e.g. legacy rows) and update them in place."""
    client = client or get_supabase_client()
    done = 0
    for aid in ids:
        rows = client.table("articles").select("*").eq("id", aid).limit(1).execute().data or []
        if not rows:
            continue
        row = rows[0]
        analysis = analyse(row["title"], row.get("content_summary") or "", row.get("source_domain") or "")
        update = {k: v for k, v in build_record({}, analysis).items() if k not in ("category",)}
        client.table("articles").update(update).eq("id", aid).execute()
        done += 1
    return done
