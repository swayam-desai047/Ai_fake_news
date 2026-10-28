from typing import List, Dict, Optional, Any
from db.supabase import get_supabase_client
from services.ai_service import analyze_article_text
import logging

logger = logging.getLogger(__name__)

def get_article_by_id(article_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single article by UUID from Supabase."""
    client = get_supabase_client()
    try:
        response = client.table("articles").select("*").eq("id", article_id).limit(1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching article by id '{article_id}': {e}")
        return None

def get_grouped_articles() -> List[Dict[str, Any]]:
    """
    Fetches articles grouped by their group_id for cross-source comparison.
    Returns a list of cluster dictionaries containing group_id, event_title, and associated articles.
    """
    client = get_supabase_client()
    try:
        response = client.table("articles").select("*").not_.is_("group_id", "null").order("published_at", desc=True).limit(200).execute()
        articles = response.data or []
        
        groups_dict: Dict[str, Dict[str, Any]] = {}
        for article in articles:
            gid = article.get("group_id")
            if not gid:
                continue
            if gid not in groups_dict:
                groups_dict[gid] = {
                    "group_id": gid,
                    "event_title": article.get("event_title") or article.get("title"),
                    "articles": [],
                    "publishers": set()
                }
            groups_dict[gid]["articles"].append(article)
            domain = article.get("source_domain")
            if domain:
                groups_dict[gid]["publishers"].add(domain)

        result = []
        for gid, grp in groups_dict.items():
            grp["publishers"] = list(grp["publishers"])
            grp["publisher_count"] = len(grp["publishers"])
            result.append(grp)

        return result
    except Exception as e:
        logger.error(f"Error fetching grouped articles: {e}")
        return []

def save_article_with_dimensions(article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Saves an article with full 8-dimension scores, AI summary, calibrated risk, and clustering metadata.
    Handles duplicate checking by title.
    """
    client = get_supabase_client()
    title = article_data.get("title")
    if not title:
        logger.warning("Attempted to save article without title")
        return None

    try:
        check = client.table("articles").select("id").eq("title", title).limit(1).execute()
        if check.data and len(check.data) > 0:
            logger.info(f"Article already exists, skipping: {title}")
            return check.data[0]

        record = {
            "title": title,
            "source_domain": article_data.get("source_domain", ""),
            "source_url": article_data.get("source_url", ""),
            "content_summary": article_data.get("content_summary", ""),
            "category": article_data.get("category", "general"),
            "sentiment": article_data.get("sentiment", "neutral"),
            "is_fake": article_data.get("is_fake", False),
            "credibility_score": article_data.get("credibility_score", 0.5),
            "ai_reasoning": article_data.get("ai_reasoning", ""),
            "risk_score": article_data.get("risk_score"),
            "confidence_level": article_data.get("confidence_level"),
            "credibility_label": article_data.get("credibility_label", "Low Risk"),
            "needs_verification": article_data.get("needs_verification", False),
            "ai_summary": article_data.get("ai_summary", ""),
            "dimensions": article_data.get("dimensions", {}),
            "group_id": article_data.get("group_id"),
            "event_title": article_data.get("event_title")
        }
        
        res = client.table("articles").insert(record).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        logger.error(f"Error saving article with dimensions '{title}': {e}")
        return None

def store_articles_in_db(articles: List[Dict]):
    """Stores fetched articles in the Supabase 'articles' table (backwards compatible)."""
    inserted_count = 0
    for article in articles:
        try:
            if "dimensions" in article or "credibility_label" in article:
                saved = save_article_with_dimensions(article)
                if saved:
                    inserted_count += 1
            else:
                ai_data = analyze_article_text(article["content_summary"])
                merged = {**article, **ai_data}
                saved = save_article_with_dimensions(merged)
                if saved:
                    inserted_count += 1
        except Exception as e:
            logger.error(f"Error inserting article '{article.get('title')}': {e}")
            
    logger.info(f"Successfully processed {inserted_count} out of {len(articles)} articles.")
    return inserted_count
