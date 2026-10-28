from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router

app = FastAPI(title="AI News Aggregator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
# Handover paths (GET /api/articles, /api/article/{id}, /api/groups, /api/report/{id}, /api/analytics).
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI News Aggregator API is running"}

@app.on_event("startup")
def on_startup():
    try:
        from services.scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        print(f"Scheduler startup skipped: {e}")
