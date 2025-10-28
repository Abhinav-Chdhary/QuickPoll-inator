# routers/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/ws", tags=["websockets"])


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        """Broadcast a JSON message to all active connections."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                # Handle cases where client disconnected unexpectedly
                self.disconnect(connection)


# Create a single instance of the manager
manager = ConnectionManager()


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """
    The main WebSocket endpoint.
    It accepts a connection and keeps it open.
    """
    await manager.connect(websocket)
    try:
        while True:
            # We just keep the connection alive.
            # We don't need to receive messages from the client
            # in this pattern, but we need to wait.
            # A 'ping' message every 30s from the client
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
