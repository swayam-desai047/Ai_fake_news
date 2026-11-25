from datetime import datetime, timedelta, timezone

from services import db_service
from tests.fake_supabase import FakeSupabase


def fake_analyse(title, excerpt, publisher):
    return {"sentiment": "neutral", "dimensions": {"sentiment": 50}, "risk_score": None, "credibility_label": None,
            "needs_verification": True, "analysis_status": "unavailable", "analysis_method": "rules",
            "_model_errors": {"x": "y"}}


def art(title, url, excerpt="Body", published="2026-11-24T10:00:00+00:00"):
    return {"title": title, "source_domain": "BBC", "source_url": url, "content_summary": excerpt,
            "category": "world", "published_at": published}


def test_stores_new_articles_and_skips_duplicates():
    db = FakeSupabase([{"id": "x", "title": "Existing story", "source_url": "https://e.com/1"}])
    stats = db_service.store_articles_in_db(
        [art("Existing story", "https://e.com/other"), art("Fresh", "https://e.com/1?utm=2"), art("New one", "https://n.com/2")],
        analyse=fake_analyse, client=db)
    assert stats["inserted"] == 1 and stats["duplicates"] == 2
    stored = [r for r in db.tables["articles"] if r["title"] == "New one"][0]
    assert stored["published_at"] == "2026-11-24T10:00:00+00:00"
    assert stored["credibility_label"] is None  # never defaulted to "Low Risk"
    assert stored["analysis_status"] == "unavailable"
    assert "_model_errors" not in stored


def test_missing_published_at_uses_column_default():
    rec = db_service.build_record(art("T", "u", published=None), fake_analyse("", "", ""))
    assert "published_at" not in rec


def test_running_twice_creates_no_duplicates():
    db = FakeSupabase()
    batch = [art("Story A", "https://a.com/1"), art("Story B", "https://b.com/1")]
    db_service.store_articles_in_db(batch, analyse=fake_analyse, client=db)
    second = db_service.store_articles_in_db(batch, analyse=fake_analyse, client=db)
    assert second["inserted"] == 0 and len(db.tables["articles"]) == 2


def test_analysis_failure_is_counted_not_raised():
    def boom(*_):
        raise RuntimeError("model crashed")
    stats = db_service.store_articles_in_db([art("A", "https://a.com")], analyse=boom, client=FakeSupabase())
    assert stats["failed"] == 1 and stats["inserted"] == 0


def test_update_groups_writes_group_ids():
    now = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)
    t = (now - timedelta(hours=2)).isoformat()
    db = FakeSupabase([
        {"id": "1", "title": "Netherlands pulls out of Eurovision over Israel", "source_domain": "BBC", "published_at": t, "content_summary": ""},
        {"id": "2", "title": "Netherlands pulls out of Eurovision over Israel row", "source_domain": "CNN", "published_at": t, "content_summary": ""},
        {"id": "3", "title": "Cricket final tonight", "source_domain": "CNN", "published_at": t, "content_summary": "", "group_id": "ev-old"},
    ])
    res = db_service.update_groups(client=db, now=now)
    rows = {r["id"]: r for r in db.tables["articles"]}
    assert rows["1"]["group_id"] == rows["2"]["group_id"] == "ev-1"
    assert rows["3"]["group_id"] is None
    assert res["groups"] == 1 and res["updated"] == 3


def test_grouped_articles_have_publisher_coverage(monkeypatch):
    db = FakeSupabase([
        {"id": "1", "title": "A", "source_domain": "BBC", "group_id": "g", "published_at": "2"},
        {"id": "2", "title": "B", "source_domain": "CNN", "group_id": "g", "published_at": "1"},
    ])
    monkeypatch.setattr(db_service, "get_supabase_client", lambda: db)
    g = db_service.get_grouped_articles()[0]
    assert g["publisher_count"] == 2
    assert [c["publisher"] for c in g["coverage"]] == ["BBC", "CNN"]


def test_insert_drops_columns_of_unapplied_migrations():
    calls = []

    class Table:
        def upsert(self, record, **_):
            calls.append(record)
            self.record = record
            return self

        def execute(self):
            for col in ("analysis_status", "image_url"):
                if col in self.record:
                    raise RuntimeError(f"Could not find the '{col}' column of 'articles'")
            from types import SimpleNamespace
            return SimpleNamespace(data=[self.record])

    class Client:
        def table(self, _):
            return Table()

    record = {"title": "T", "analysis_status": "ok", "image_url": "https://ex.com/a.jpg"}
    saved = db_service._insert(Client(), record)
    assert saved == {"title": "T"}
    assert len(calls) == 3
