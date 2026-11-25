from datetime import datetime, timedelta, timezone

from services.clustering_service import assignments, cluster_articles

NOW = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)


def row(i, pub, title, hours_ago=1, excerpt=""):
    return {"id": i, "source_domain": pub, "title": title, "content_summary": excerpt,
            "published_at": (NOW - timedelta(hours=hours_ago)).isoformat()}


def test_groups_same_event_across_publishers():
    groups = cluster_articles([
        row("1", "BBC", "Netherlands pulls out of Eurovision over Israel participation"),
        row("2", "AlJazeera", "The Netherlands pulls out of Eurovision 2027 due to Israel sensitivities"),
        row("3", "CNN", "Monsoon rains flood Chennai streets"),
    ], NOW)
    assert len(groups) == 1
    assert sorted(groups[0]["publishers"]) == ["AlJazeera", "BBC"]
    assert groups[0]["group_id"] == "ev-1"


def test_same_publisher_only_is_not_a_group():
    assert cluster_articles([
        row("1", "BBC", "Netherlands pulls out of Eurovision over Israel"),
        row("2", "BBC", "Netherlands pulls out of Eurovision over Israel row"),
    ], NOW) == []


def test_reports_far_apart_in_time_are_not_grouped():
    assert cluster_articles([
        row("1", "BBC", "Netherlands pulls out of Eurovision over Israel", hours_ago=1),
        row("2", "CNN", "Netherlands pulls out of Eurovision over Israel row", hours_ago=40),
    ], NOW) == []


def test_old_articles_outside_window_ignored_and_ungrouped_cleared():
    rows = [
        row("1", "BBC", "Netherlands pulls out of Eurovision over Israel"),
        row("2", "CNN", "Netherlands pulls out of Eurovision over Israel row"),
        row("3", "CNN", "Completely different story about cricket"),
        row("4", "BBC", "Ancient story", hours_ago=100),
    ]
    a = assignments(rows, NOW)
    assert a["1"]["group_id"] == a["2"]["group_id"] == "ev-1"
    assert a["3"] == {"group_id": None, "event_title": None}
    assert "4" not in a


def test_insufficient_articles():
    assert cluster_articles([row("1", "BBC", "Lonely story")], NOW) == []
