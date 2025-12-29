"""
FastAPI application entry point.
"""
import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import endpoints, websocket
from app.core.config import CORS_ORIGINS
from app.core.sessions import session_manager

app = FastAPI(
    title="Lift Simulation API",
    description="Lift simulation system for comparing elevator algorithms",
    version="1.0.0",
)

# CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api")
app.add_websocket_route("/ws/{session_id}", websocket.websocket_endpoint)

# Serve React frontend (built)
frontend_path = "frontend-react/dist"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.on_event("startup")
async def startup_event() -> None:
    """Start background tasks."""
    asyncio.create_task(session_cleanup_task())


async def session_cleanup_task() -> None:
    """Periodically clean up expired sessions."""
    while True:
        await asyncio.sleep(60 * 5)
        session_manager.cleanup_sessions()


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "lift-simulation"}
