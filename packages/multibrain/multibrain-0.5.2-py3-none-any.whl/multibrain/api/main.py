# src/multibrain/api/main.py

import os
import logging
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from multibrain.api.routes.router import router as api_router
from multibrain.api.routes.streaming import router as streaming_router

# Configure logging
log_level = os.getenv("MULTIBRAIN_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("MultiBrain API starting up...")
    logger.info(f"Environment: {os.getenv('MULTIBRAIN_ENV', 'development')}")

    # Get CORS origins for logging
    cors_origins = os.getenv("MULTIBRAIN_CORS_ORIGINS", "*")
    if cors_origins == "*":
        origins = ["*"]
    else:
        origins = [origin.strip() for origin in cors_origins.split(",")]
        origins.extend(
            ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
        )
    logger.info(f"CORS origins: {origins}")

    # Check if serving static files
    serve_static = os.getenv("MULTIBRAIN_SERVE_STATIC", "false").lower() == "true"
    static_path = Path(os.getenv("MULTIBRAIN_STATIC_PATH", "frontend/dist"))
    if serve_static:
        logger.info(f"Serving static files: {static_path}")

    yield

    # Shutdown
    logger.info("MultiBrain API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MultiBrain API",
    version="2.0.0",
    description="Query multiple AI models simultaneously with real-time streaming",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.getenv("MULTIBRAIN_CORS_ORIGINS", "*")
if cors_origins == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in cors_origins.split(",")]
    # Always include localhost for development
    origins.extend(
        ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)
app.include_router(streaming_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": os.getenv("MULTIBRAIN_ENV", "development"),
    }


# API root endpoint
@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {"message": "MultiBrain API v2.0", "docs": "/docs", "health": "/health"}


# API health check endpoint (for frontend compatibility)
@app.get("/api/health")
@app.head("/api/health")
async def api_health_check():
    """API health check endpoint for frontend"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": os.getenv("MULTIBRAIN_ENV", "development"),
    }


# Serve static files if configured
serve_static = os.getenv("MULTIBRAIN_SERVE_STATIC", "false").lower() == "true"
static_path = Path(os.getenv("MULTIBRAIN_STATIC_PATH", "frontend/dist"))

if serve_static and static_path.exists():
    # Mount static files
    if (static_path / "assets").exists():
        app.mount(
            "/assets", StaticFiles(directory=static_path / "assets"), name="assets"
        )

    # Serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Don't serve index.html for API routes
        if full_path.startswith("api/") or full_path in [
            "health",
            "docs",
            "redoc",
            "openapi.json",
        ]:
            return {"detail": "Not found"}

        # Check if it's a static file request
        file_path = static_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Serve index.html for all other routes (SPA routing)
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"detail": "Frontend not found"}

    logger.info(f"Serving static files from {static_path}")
