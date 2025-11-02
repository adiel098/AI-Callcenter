"""
Main FastAPI application
"""
import sys
import os

# Ensure parent directory is in Python path for imports to work
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sentry_sdk

from backend.config import get_settings
from backend.database import init_db
from backend.api.routes import leads, calls, meetings, campaigns, analytics, webhooks, partners
from backend.api.routes import settings as settings_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize Sentry if DSN provided
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
    )

# Create FastAPI app
app = FastAPI(
    title="AI Outbound Meeting Scheduler",
    description="AI-powered system for scheduling meetings via phone calls",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(calls.router, prefix="/api/calls", tags=["calls"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(settings_routes.router, prefix="/api", tags=["settings"])
app.include_router(partners.router, prefix="/api/partners", tags=["partners"])


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("Starting AI Outbound Meeting Scheduler API")
    # Initialize database
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Outbound Meeting Scheduler API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy"}


@app.get("/readiness")
async def readiness_check():
    """Readiness check endpoint"""
    # Check database connection
    try:
        from backend.database import get_db_context
        with get_db_context() as db:
            # Simple query to check connection
            db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not_ready", "database": "disconnected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
