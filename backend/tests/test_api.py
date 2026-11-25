import uuid

import pytest

from tests.fake_supabase import FakeSupabase

ARTICLE_ID = str(uuid.uuid4())


@pytest.fixture
def db(monkeypatch):
    fake = FakeSupabase([{
        "id": ARTICLE_ID, "title": "Flood warning issued as river rises", "source_domain": "BBC",
        "source_url": "https://bbc.co.uk/x", "content_summary": "Officials warned residents.", "category": "general",
        "published_at": "2026-11-24T10:00:00+00:00", "credibility_label": "Moderate Risk", "risk_score": 0.4,
        "needs_verification": True, "sentiment": "negative", "group_id": None,
        "dimensions": {"sentiment": 30, "bias": 90, "objectivity": 92, "readability": None, "propaganda": 95,
                       "headline_accuracy": 70, "source_credibility": 93, "content_quality": 40, "explanations": {}},
        "analysis_status": "partial",
    }, {"id": str(uuid.uuid4()), "title": "Old row", "credibility_label": None, "dimensions": {}, "published_at": "2026-01-01"}])
    import api.router as router
    import services.db_service as dbs
    monkeypatch.setattr(router, "get_supabase_client", lambda: fake)
    monkeypatch.setattr(dbs, "get_supabase_client", lambda: fake)
    return fake


def test_health_check(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert "models" in body and "database_configured" in body


def test_analyze_endpoint_with_models(client, fake_models):
    r = client.post("/api/v1/analyze", json={"title": "Markets fall", "text": "Stocks fell sharply on Monday, analysts said, after weak factory data from several large economies raised fears of a slowdown.", "publisher": "Reuters"})
    assert r.status_code == 200
    data = r.json()
    for key in ("sentiment", "is_fake", "credibility_score", "risk_score", "credibility_label", "dimensions", "analysis_status"):
        assert key in data
    assert data["sentiment"] in ("positive", "neutral", "negative")
    assert data["analysis_status"] == "complete"
    assert set(data["dimensions"]["explanations"]) == {
        "sentiment", "bias", "objectivity", "readability", "propaganda", "headline_accuracy", "source_credibility", "content_quality"}


def test_analyze_without_models_reports_status(client, no_models):
    r = client.post("/api/v1/analyze", json={"text": "Stocks fell sharply on Monday. Analysts blamed weak data."})
    assert r.status_code == 200
    data = r.json()
    assert data["analysis_method"] == "rules"
    assert data["is_fake"] is None and data["confidence_level"] is None
    assert data["model_errors"]


def test_analyze_validation(client):
    assert client.post("/api/v1/analyze", json={"text": ""}).status_code == 422
    assert client.post("/api/v1/analyze", json={"text": "x" * 20_001}).status_code == 422
    assert client.post("/api/v1/analyze", json={}).status_code == 422


def test_article_by_id(client, db):
    r = client.get(f"/api/article/{ARTICLE_ID}")
    assert r.status_code == 200 and r.json()["title"].startswith("Flood")
    assert client.get(f"/api/article/{uuid.uuid4()}").status_code == 404
    assert client.get("/api/article/not-a-uuid").status_code == 422


def test_articles_filters_and_validation(client, db):
    assert client.get("/api/articles?limit=0").status_code == 422
    assert client.get("/api/articles?risk=Safe").status_code == 422
    r = client.get("/api/articles?risk=Unavailable")
    assert r.status_code == 200 and [a["title"] for a in r.json()] == ["Old row"]
    assert len(client.get("/api/articles?risk=Moderate%20Risk").json()) == 1


def test_analytics_counts_unavailable_and_ignores_missing_scores(client, db):
    a = client.get("/api/analytics").json()
    assert a["risk"]["Unavailable"] == 1 and a["risk"]["Moderate Risk"] == 1
    assert a["dimension_averages"]["readability"] is None
    assert a["dimension_averages"]["bias"] == 90
    assert a["dimension_counts"]["bias"] == 1


def test_database_errors_are_not_leaked(client, db):
    db.fail = True
    r = client.get("/api/articles")
    assert r.status_code == 503
    assert "db down" not in r.text


def test_report_pdf(client, db):
    r = client.get(f"/api/report/{ARTICLE_ID}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    assert client.get(f"/api/report/{uuid.uuid4()}").status_code == 404


def test_cors_allows_only_configured_origins(client):
    ok = client.options("/api/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"
    bad = client.options("/api/health", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


def test_ingest_disabled_without_token(client, monkeypatch):
    monkeypatch.delenv("INGEST_TOKEN", raising=False)
    assert client.post("/api/ingest").status_code == 404
    monkeypatch.setenv("INGEST_TOKEN", "secret")
    assert client.post("/api/ingest", headers={"X-Ingest-Token": "wrong"}).status_code == 403


def test_rate_limit(client, no_models, monkeypatch):
    import main
    monkeypatch.setattr(main, "RATE_LIMIT_PER_MINUTE", 2)
    main._hits.clear()
    codes = [client.post("/api/analyze", json={"text": "Some text here. More text."}).status_code for _ in range(3)]
    main._hits.clear()
    assert codes == [200, 200, 429]
