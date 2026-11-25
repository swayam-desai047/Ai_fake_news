"""Quick connectivity check: prints the five most recently ingested articles."""
from db.supabase import get_supabase_client

client = get_supabase_client()
response = (client.table("articles")
            .select("title, credibility_label, risk_score, analysis_status, published_at, created_at")
            .order("created_at", desc=True).limit(5).execute())
print("Five most recently ingested articles:")
for r in response.data:
    print(r)
