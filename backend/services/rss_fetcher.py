"""
RSS collection: fetch the configured publisher feeds and normalise each entry.

Each feed is downloaded with a timeout (httpx) and parsed with feedparser. A feed that fails is
recorded in ``failed_sources`` and the rest of the run continues. Entries are cleaned (HTML
removed, whitespace collapsed), given an ISO-8601 UTC publication time when the feed provides one,
and de-duplicated within the batch by normalised URL and normalised title.
"""
from __future__ import annotations

import calendar
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

import feedparser
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Grouped by category (unchanged source list; https where the publisher supports it).
RSS_SOURCES: Dict[str, Dict[str, str]] = {
    "sports": {
        "BBC Sport": "https://feeds.bbci.co.uk/sport/rss.xml",
        "Yahoo Sports": "https://sports.yahoo.com/rss/",
    },
    "politics": {
        "CNN Politics": "http://rss.cnn.com/rss/cnn_allpolitics.rss",
        "BBC Politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
    },
    "business": {
        "Yahoo Finance": "https://finance.yahoo.com/news/rss",
        "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    },
    "technology": {
        "CNN Tech": "http://rss.cnn.com/rss/cnn_tech.rss",
        "BBC Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    },
    "general": {
        "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
        "CNN": "http://rss.cnn.com/rss/edition_world.rss",
        "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    },
}

ENTRIES_PER_SOURCE = 8
TIMEOUT_SECONDS = 15
USER_AGENT = "AI-News-Aggregator/2.0 (academic project; RSS reader)"


def clean_html(raw_html: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    if not raw_html:
        return ""
    text = BeautifulSoup(raw_html, "html.parser").get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def normalise_url(url: str) -> str:
    """Lower-case host, drop query string/fragment and trailing slash (used for duplicate checks)."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower() or "https", parts.netloc.lower(), path, "", ""))


def normalise_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def entry_published_at(entry) -> Optional[str]:
    """ISO-8601 UTC timestamp from the entry's parsed date, or None if the feed gives none."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    try:
        return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc).isoformat()
    except (OverflowError, ValueError, TypeError):
        return None


def parse_feed(content: bytes, source_domain: str, category: str, limit: int = ENTRIES_PER_SOURCE) -> List[Dict]:
    """Parse one feed document into normalised article dicts."""
    feed = feedparser.parse(content)
    out = []
    for entry in feed.entries[:limit]:
        title = clean_html(entry.get("title", ""))
        url = (entry.get("link") or "").strip()
        if not title or not url:
            continue
        excerpt = clean_html(entry.get("summary", "") or entry.get("description", ""))
        out.append({
            "title": title,
            "source_domain": source_domain,
            "source_url": url,
            # The excerpt is stored as supplied; an empty excerpt stays empty (no title fallback),
            # so later analysis can tell "headline only" apart from real body text.
            "content_summary": excerpt if excerpt != title else "",
            "category": category,
            "published_at": entry_published_at(entry),
        })
    return out


def fetch_feed(client: httpx.Client, url: str) -> bytes:
    response = client.get(url)
    response.raise_for_status()
    return response.content


def dedupe(articles: List[Dict]) -> List[Dict]:
    """Drop repeats within one batch (same normalised URL or same normalised title)."""
    seen_urls, seen_titles, out = set(), set(), []
    for a in articles:
        u, t = normalise_url(a["source_url"]), normalise_title(a["title"])
        if u in seen_urls or t in seen_titles:
            continue
        seen_urls.add(u)
        seen_titles.add(t)
        out.append(a)
    return out


def fetch_articles(sources: Optional[Dict[str, Dict[str, str]]] = None,
                   client: Optional[httpx.Client] = None) -> Tuple[List[Dict], List[str]]:
    """Fetch every configured feed. Returns ``(articles, failed_sources)``."""
    sources = sources or RSS_SOURCES
    own_client = client is None
    client = client or httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=True,
                                    headers={"User-Agent": USER_AGENT})
    articles: List[Dict] = []
    failed: List[str] = []
    try:
        for category, feeds in sources.items():
            for source_domain, feed_url in feeds.items():
                try:
                    items = parse_feed(fetch_feed(client, feed_url), source_domain, category)
                    if not items:
                        logger.warning("Feed %s returned no usable entries", source_domain)
                    articles.extend(items)
                except Exception as exc:
                    logger.warning("Feed %s failed: %s", source_domain, exc)
                    failed.append(source_domain)
    finally:
        if own_client:
            client.close()
    return dedupe(articles), failed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data, failed_sources = fetch_articles()
    print(f"Fetched {len(data)} articles; failed feeds: {failed_sources or 'none'}")
    if data:
        print(data[0])
