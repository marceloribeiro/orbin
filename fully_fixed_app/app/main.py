"""
Main FastAPI application for fully_fixed_app.
"""

from datetime import datetime
from fastapi import FastAPI
from config.settings import settings
from app.routes import router

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered chat application built with Orbin",
    version="1.0.0",
    debug=settings.DEBUG
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "app_name": settings.APP_NAME
    }