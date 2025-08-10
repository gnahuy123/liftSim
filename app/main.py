from fastapi import FastAPI
from app.api import endpoints, websocket
from app.core.sessions import session_manager
import asyncio

app = FastAPI()

app.include_router(endpoints.router, prefix="/api")
app.add_websocket_route("/ws/{session_id}", websocket.websocket_endpoint)

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