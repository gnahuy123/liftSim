from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints, websocket
from app.core.sessions import session_manager
import asyncio
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(endpoints.router, prefix="/api")
app.add_websocket_route("/ws/{session_id}", websocket.websocket_endpoint)

# Serve React frontend (built) or fallback message
frontend_path = "frontend-react/dist"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(session_cleanup_task())

async def session_cleanup_task():
    while True:
        await asyncio.sleep(60 * 5)  # Run every 5 minutes
        session_manager.cleanup_sessions()

@app.get("/")
def health_check():
    return {"status": "Lift system operational"}