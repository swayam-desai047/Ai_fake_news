"""REST endpoints. Mounted at both /api/v1 and /api (see main.py)."""
import hmac
import logging
import os
from collections import Counter
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Response
from pydantic import BaseModel, Field

from db.supabase import get_supabase_client, is_configured
from services import ai_service
from services.analysis_pipeline import analyze_article
from services.db_service import get_article_by_id, get_grouped_articles
from services.dimension_service import DIMENSION_KEYS, RISK_LABELS

logger = logging.getLogger(__name__)
api_router = APIRouter()

RiskFilter = Literal["Low Risk", "Moderate Risk", "High Risk", "Unavailable"]


def _db_error(exc: Exception) -> HTTPException:
    logger.error("Database error: %s", exc)
    return HTTPException(status_code=503, detail="The database is temporarily unavailable.")


class ArticleAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=ai_service.MAX_INPUT_CHARS, description="Article text or excerpt.")
    title: str = Field("", max_length=500)
    publisher: str = Field("", max_length=120)


class ArticleAnalyzeResponse(BaseModel):
    sentiment: Optional[str]
    is_fake: Optional[bool]
    credibility_score: Optional[float]
    risk_score: Optional[float]
    credibility_label: Optional[str]
    needs_verification: bool
    confidence_level: Optional[float]
    model_fake_probability: Optional[float]
    dimensions: dict
    ai_reasoning: str
    ai_summary: Optional[str]
    analysis_status: str
    analysis_method: str
    model_version: str
    model_errors: dict


@api_router.get("/health")
def health():
    from services.scheduler import last_run
    return {
        "status": "healthy",
        "database_configured": is_configured(),
        "models": ai_service.model_status(),
        "last_ingestion": last_run or None,
    }


@api_router.post("/analyze", response_model=ArticleAnalyzeResponse)
def analyze_endpoint(request: ArticleAnalyzeRequest):
    """Analyse a block of text: classifier, sentiment, eight dimensions and risk. Nothing is stored."""
    title = request.title.strip()
    text = request.text.strip()
    if not title:
        # Without a separate headline, the first sentence stands in for it.
        first, _, rest = text.partition(". ")
        title, text = (first, rest) if rest else (text[:120], text)
    result = analyze_article(title, text, request.publisher.strip())
    result["model_errors"] = result.pop("_model_errors", {})
    return result


@api_router.get("/articles")
def get_articles(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0, le=10_000),
    category: Optional[str] = Query(None, max_length=40),
    risk: Optional[RiskFilter] = None,
    q: Optional[str] = Query(None, max_length=120),
    needs_verification: Optional[bool] = None,
):
    """Recent articles, optionally filtered by category, risk label, verification flag and search term."""
    try:
        query = get_supabase_client().table("articles").select("*")
        if category and category.lower() != "all":
            query = query.eq("category", category.lower())
        if risk == "Unavailable":
            query = query.is_("credibility_label", "null")
        elif risk:
            query = query.eq("credibility_label", risk)
        if needs_verification is not None:
            query = query.eq("needs_verification", needs_verification)
        if q:
            # Characters with meaning in PostgREST filter syntax are dropped from the search term.
            term = "".join(ch for ch in q if ch.isalnum() or ch in " -'").strip()
            if term:
                query = query.or_(f"title.ilike.%{term}%,content_summary.ilike.%{term}%")
        return query.order("published_at", desc=True).range(offset, offset + limit - 1).execute().data
    except Exception as exc:
        raise _db_error(exc)


@api_router.get("/article/{article_id}")
def get_article(article_id: UUID):
    """One article with its eight-dimension analysis, risk fields and summary."""
    try:
        article = get_article_by_id(str(article_id))
    except Exception as exc:
        raise _db_error(exc)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@api_router.get("/groups")
def get_groups():
    """Cross-source event groups (articles sharing a group_id) covered by at least two publishers."""
    try:
        groups = get_grouped_articles()
    except Exception as exc:
        raise _db_error(exc)
    return [g for g in groups if g.get("publisher_count", 0) >= 2]


@api_router.get("/analytics")
def get_analytics(limit: int = Query(500, ge=1, le=2000)):
    """Category, sentiment, risk, analysis-status and dimension statistics over recent articles."""
    try:
        rows = get_supabase_client().table("articles").select("*").order("published_at", desc=True).limit(limit).execute().data or []
    except Exception as exc:
        raise _db_error(exc)

    def dim_values(key):
        return [r["dimensions"][key] for r in rows
                if isinstance(r.get("dimensions"), dict) and isinstance(r["dimensions"].get(key), (int, float))]

    group_sizes = Counter(r["group_id"] for r in rows if r.get("group_id"))
    risk = {label: sum(1 for r in rows if r.get("credibility_label") == label) for label in RISK_LABELS}
    risk["Unavailable"] = sum(1 for r in rows if r.get("credibility_label") not in RISK_LABELS)
    return {
        "total": len(rows),
        "categories": dict(Counter((r.get("category") or "general") for r in rows)),
        "sentiment": dict(Counter((r.get("sentiment") or "unscored") for r in rows)),
        "risk": risk,
        "needs_verification": sum(1 for r in rows if r.get("needs_verification")),
        "analysis_status": dict(Counter((r.get("analysis_status") or "legacy") for r in rows)),
        "dimension_averages": {
            k: (round(sum(v) / len(v), 1) if v else None) for k, v in ((k, dim_values(k)) for k in DIMENSION_KEYS)
        },
        "dimension_counts": {k: len(dim_values(k)) for k in DIMENSION_KEYS},
        "publishers": dict(Counter((r.get("source_domain") or "unknown") for r in rows)),
        "groups": len([g for g, n in group_sizes.items() if n >= 2]),
    }


@api_router.get("/report/{article_id}")
def get_report(article_id: UUID):
    """Generate and stream an A4 PDF report for one article."""
    try:
        article = get_article_by_id(str(article_id))
    except Exception as exc:
        raise _db_error(exc)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    from services.report_service import build_article_report  # lazy: ReportLab only needed here
    return Response(
        content=build_article_report(article),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="article-report-{article_id}.pdf"'},
    )


@api_router.post("/ingest")
def trigger_ingest(x_ingest_token: Optional[str] = Header(None)):
    """Run one ingestion cycle on demand. Disabled unless INGEST_TOKEN is set; the header must match."""
    token = os.getenv("INGEST_TOKEN")
    if not token:
        raise HTTPException(status_code=404, detail="Not found")
    if not x_ingest_token or not hmac.compare_digest(x_ingest_token, token):
        raise HTTPException(status_code=403, detail="Invalid ingest token")
    from services.scheduler import fetch_and_store_job
    return fetch_and_store_job()
