import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")

def is_configured() -> bool:
    return bool(
        SUPABASE_URL
        and SUPABASE_KEY
        and (SUPABASE_URL.startswith("http://") or SUPABASE_URL.startswith("https://"))
        and "YOUR_SUPABASE" not in SUPABASE_URL
    )

if not is_configured():
    print("Warning: Valid SUPABASE_URL or SUPABASE_KEY is missing in .env")

def get_supabase_client() -> Client:
    if not is_configured():
        raise ValueError("Supabase credentials not configured or invalid URL.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
