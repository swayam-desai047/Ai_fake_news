"""
Re-score stored articles with the current analysis pipeline.

Usage (from the backend directory):
    python -m scripts.reanalyze            # rows marked legacy or without dimensions (max 500)
    python -m scripts.reanalyze --all      # every row (max 500 per run)
    python -m scripts.reanalyze --regroup  # only re-run cross-source grouping

Needs SUPABASE_SERVICE_ROLE_KEY. Model weights are downloaded on first use if they are not cached.
"""
import argparse
import logging

from db.supabase import get_supabase_client
from services.db_service import reanalyze, update_groups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--regroup", action="store_true")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    client = get_supabase_client()
    if not args.regroup:
        query = client.table("articles").select("id, analysis_status, dimensions")
        rows = query.order("published_at", desc=True).limit(args.limit).execute().data or []
        if not args.all:
            rows = [r for r in rows if (r.get("analysis_status") in (None, "legacy")) or not r.get("dimensions")]
        print(f"Re-analysing {len(rows)} articles...")
        print(f"Updated {reanalyze([r['id'] for r in rows], client=client)} articles.")
    print("Grouping:", update_groups(client=client))


if __name__ == "__main__":
    main()
