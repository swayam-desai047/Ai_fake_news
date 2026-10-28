from collections import Counter
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from services.ai_service import analyze_article_text
from services.db_service import get_article_by_id, get_grouped_articles
from db.supabase import get_supabase_client

api_router = APIRouter()

DIMENSION_KEYS = [
    "sentiment", "bias", "objectivity", "readability",
    "propaganda", "headline_accuracy", "source_credibility", "content_quality",
]
RISK_LABELS = ["Low Risk", "Moderate Risk", "High Risk"]

class ArticleAnalyzeRequest(BaseModel):
    text: str

class ArticleAnalyzeResponse(BaseModel):
    sentiment: str
    is_fake: bool
    credibility_score: float

@api_router.get("/health")
def health():
    return {"status": "healthy"}

@api_router.post("/analyze", response_model=ArticleAnalyzeResponse)
def analyze_endpoint(request: ArticleAnalyzeRequest):
    """Analyze a single block of text for fake news and sentiment."""
    try:
        result = analyze_article_text(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/articles")
def get_articles(
    limit: int = 50,
    offset: int = 0,
    category: Optional[str] = None,
    risk: Optional[str] = None,
    q: Optional[str] = None,
    needs_verification: Optional[bool] = None,
):
    """Fetch recent articles from Supabase, optionally filtered by category, risk label and search term."""
    if risk and risk not in RISK_LABELS:
        raise HTTPException(status_code=422, detail=f"risk must be one of {RISK_LABELS}")
    try:
        client = get_supabase_client()
        query = client.table("articles").select("*")
        if category and category.lower() != "all":
            query = query.eq("category", category.lower())
        if risk:
            query = query.eq("credibility_label", risk)
        if needs_verification is not None:
            query = query.eq("needs_verification", needs_verification)
        if q:
            # Characters with meaning in PostgREST filter syntax are dropped from the search term.
            term = "".join(ch for ch in q if ch not in ",()*%")[:120].strip()
            if term:
                query = query.or_(f"title.ilike.%{term}%,content_summary.ilike.%{term}%")
        response = query.order("published_at", desc=True).range(offset, offset + max(1, min(limit, 200)) - 1).execute()
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@api_router.get("/article/{article_id}")
def get_article(article_id: str):
    """Return one article with its full 8-dimension analysis and summary."""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@api_router.get("/groups")
def get_groups():
    """Return cross-source event clusters (articles sharing a group_id) with at least two publishers."""
    groups = get_grouped_articles()
    return [g for g in groups if g.get("publisher_count", 0) >= 2]

@api_router.get("/analytics")
def get_analytics(limit: int = 500):
    """Category, sentiment, risk and dimension statistics over the most recent articles."""
    try:
        client = get_supabase_client()
        rows = client.table("articles").select(
            "category, sentiment, credibility_label, needs_verification, dimensions, group_id, source_domain"
        ).order("published_at", desc=True).limit(max(1, min(limit, 2000))).execute().data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    scored = [r["dimensions"] for r in rows if isinstance(r.get("dimensions"), dict) and all(
        isinstance(r["dimensions"].get(k), (int, float)) for k in DIMENSION_KEYS)]
    group_sizes = Counter(r["group_id"] for r in rows if r.get("group_id"))
    return {
        "total": len(rows),
        "categories": dict(Counter((r.get("category") or "general") for r in rows)),
        "sentiment": dict(Counter((r.get("sentiment") or "unscored") for r in rows)),
        "risk": {label: sum(1 for r in rows if r.get("credibility_label") == label) for label in RISK_LABELS},
        "needs_verification": sum(1 for r in rows if r.get("needs_verification")),
        "dimension_averages": {
            k: round(sum(d[k] for d in scored) / len(scored), 1) if scored else None for k in DIMENSION_KEYS
        },
        "scored_articles": len(scored),
        "publishers": dict(Counter((r.get("source_domain") or "unknown") for r in rows)),
        "groups": len([g for g, n in group_sizes.items() if n >= 2]),
    }

@api_router.get("/report/{article_id}")
def get_report(article_id: str):
    """Generate and stream an A4 executive PDF report for one article."""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Imported lazily so the API starts even where ReportLab is not installed yet.
    from services.report_service import build_article_report
    pdf = build_article_report(article)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="article-report-{article_id}.pdf"'},
    )
