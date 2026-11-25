"""
Scheduled ingestion: every 30 minutes fetch the RSS feeds, analyse and store new articles, then
re-run cross-source grouping over the recent window.

A lock keeps runs from overlapping; APScheduler is configured with ``max_instances=1`` and
``coalesce=True`` so a slow run never produces a second concurrent job. Every step is wrapped so a
failing feed, model or database call is logged instead of stopping the scheduler.
"""
import logging
import os
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from services.rss_fetcher import fetch_articles
from services.db_service import store_articles_in_db, update_groups

logger = logging.getLogger(__name__)

INTERVAL_MINUTES = int(os.getenv("INGEST_INTERVAL_MINUTES", "30"))
_run_lock = threading.Lock()
last_run: dict = {}


def fetch_and_store_job() -> dict:
    """One ingestion run. Returns a summary (also kept in ``last_run`` for /api/health)."""
    if not _run_lock.acquire(blocking=False):
        logger.info("Previous ingestion still running; skipping this trigger.")
        return {"skipped": True}
    summary: dict = {"started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        articles, failed = fetch_articles()
        summary.update({"fetched": len(articles), "failed_sources": failed})
        summary["storage"] = store_articles_in_db(articles) if articles else {}
        summary["grouping"] = update_groups()
    except Exception as exc:
        logger.exception("Ingestion run failed")
        summary["error"] = type(exc).__name__
    finally:
        summary["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        last_run.clear()
        last_run.update(summary)
        _run_lock.release()
    logger.info("Ingestion summary: %s", summary)
    return summary


def start_scheduler(run_now: bool = False) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetch_and_store_job,
        trigger=IntervalTrigger(minutes=INTERVAL_MINUTES),
        id="fetch_rss_job",
        name=f"Fetch RSS feeds every {INTERVAL_MINUTES} min",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    if run_now:
        scheduler.add_job(fetch_and_store_job, id="fetch_rss_initial", replace_existing=True, max_instances=1)
    scheduler.start()
    logger.info("Scheduler started (every %d minutes).", INTERVAL_MINUTES)
    return scheduler


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sched = start_scheduler()
    fetch_and_store_job()  # run once immediately when started by hand
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
