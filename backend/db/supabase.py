"""
Supabase client for the backend.

The backend writes articles, so it should use the service-role key (``SUPABASE_SERVICE_ROLE_KEY``,
or the newer ``SUPABASE_SECRET_KEY``). This key bypasses Row Level Security and must never be
exposed to the browser: it belongs only in ``backend/.env`` or the server's secret store.
``SUPABASE_KEY`` is still accepted for backwards compatibility.
"""
import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_SECRET_KEY")
    or os.getenv("SUPABASE_KEY")
)


def is_configured() -> bool:
    return bool(
        SUPABASE_URL
        and SUPABASE_KEY
        and SUPABASE_URL.startswith(("http://", "https://"))
        and "YOUR_SUPABASE" not in SUPABASE_URL.upper()
    )


if not is_configured():
    logger.warning("Supabase is not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing).")


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    if not is_configured():
        raise RuntimeError("Supabase credentials are not configured.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
