"""Opt-in tests that need the real models or network access. Skipped by default."""
import os

import pytest

RUN_MODELS = os.getenv("RUN_MODEL_TESTS") == "1"
RUN_LIVE = os.getenv("RUN_LIVE_TESTS") == "1"


@pytest.mark.model
@pytest.mark.skipif(not RUN_MODELS, reason="set RUN_MODEL_TESTS=1 (downloads transformer weights)")
def test_real_models_load_and_return_scores():
    from services import ai_service
    ai_service.reset_for_tests()
    fake = ai_service.classify_fake_news("WASHINGTON (Reuters) - The Senate passed the bill on Tuesday, aides said.")
    senti = ai_service.classify_sentiment("The rescue team saved everyone and the town celebrated.")
    assert fake["status"] == "ok" and 0 <= fake["fake_probability"] <= 1
    assert senti["status"] == "ok" and senti["positive_probability"] > 0.5


@pytest.mark.live
@pytest.mark.skipif(not RUN_LIVE, reason="set RUN_LIVE_TESTS=1 (fetches real RSS feeds)")
def test_real_rss_feeds():
    from services.rss_fetcher import fetch_articles
    articles, failed = fetch_articles()
    assert articles, f"no articles; failed feeds: {failed}"


@pytest.mark.live
@pytest.mark.skipif(not RUN_LIVE, reason="set RUN_LIVE_TESTS=1 (needs Supabase credentials)")
def test_supabase_connectivity():
    from db.supabase import get_supabase_client
    assert get_supabase_client().table("articles").select("id").limit(1).execute() is not None
