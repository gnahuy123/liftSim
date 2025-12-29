from fastapi import WebSocket, WebSocketDisconnect
from app.core.sessions import session_manager
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_json(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    # Extract session_id from the websocket path params (used by add_websocket_route)
    session_id = websocket.path_params.get('session_id')

    # Validate session
    controller = session_manager.get_controller(session_id)
    if not controller:
        await websocket.close(code=1008, reason="Session invalid")
        return

    await manager.connect(websocket, session_id)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "state_update",
            "data": controller.get_state()
        })
        
        while True:
            data = await websocket.receive_text()
            if data == "move":
                state = controller.move()
                # Broadcast to all connections in session
                await manager.broadcast(session_id, {
                    "type": "state_update",
                    "data": state
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)