"""
WebSocket endpoints for real-time lift state updates.
"""
from fastapi import WebSocket, WebSocketDisconnect

from app.core.sessions import session_manager


class ConnectionManager:
    """Manages WebSocket connections per session."""

    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict) -> None:
        """Broadcast a message to all connections in a session."""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_json(message)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle WebSocket connections for lift state updates."""
    session_id: str | None = websocket.path_params.get("session_id")

    if not session_id:
        await websocket.close(code=1008, reason="Session ID required")
        return

    controller = session_manager.get_controller(session_id)
    if not controller:
        await websocket.close(code=1008, reason="Session invalid")
        return

    await manager.connect(websocket, session_id)

    try:
        await websocket.send_json({
            "type": "state_update",
            "data": controller.get_state(),
        })

        while True:
            data = await websocket.receive_text()
            if data == "move":
                state = controller.move()
                await manager.broadcast(session_id, {
                    "type": "state_update",
                    "data": state,
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
