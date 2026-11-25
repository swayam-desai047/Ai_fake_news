"""FastAPI application: CORS, rate limiting, error handling, routers and the ingestion scheduler."""
import logging
import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import api_router

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Comma-separated list of frontend origins allowed to call the API from a browser.
ALLOWED_ORIGINS = [o.strip() for o in os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]

# Simple in-memory rate limit for the expensive endpoints (model inference, PDF rendering).
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
RATE_LIMITED_PATHS = ("/analyze", "/report/")
_hits: dict = defaultdict(deque)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    scheduler = None
    if os.getenv("ENABLE_SCHEDULER", "1") not in ("0", "false", "False"):
        try:
            from services.scheduler import start_scheduler
            scheduler = start_scheduler(run_now=os.getenv("INGEST_ON_STARTUP", "0") in ("1", "true", "True"))
        except Exception as exc:
            logger.warning("Scheduler not started: %s", exc)
    yield
    if scheduler:
        scheduler.shutdown(wait=False)


app = FastAPI(title="AI News Aggregator API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if RATE_LIMIT_PER_MINUTE > 0 and any(p in request.url.path for p in RATE_LIMITED_PATHS):
        key = (request.client.host if request.client else "unknown", "analyze" if "/analyze" in request.url.path else "report")
        now = time.monotonic()
        window = _hits[key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= RATE_LIMIT_PER_MINUTE:
            return JSONResponse({"detail": "Too many requests. Please wait a minute."}, status_code=429,
                                headers={"Retry-After": "60"})
        window.append(now)
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled(_request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse({"detail": "Internal server error."}, status_code=500)


app.include_router(api_router, prefix="/api/v1")
# Same routes without the version prefix (paths used in the synopsis: /api/article/{id}, /api/report/{id}...).
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI News Aggregator API is running", "docs": "/docs"}
