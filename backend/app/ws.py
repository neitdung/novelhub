from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, novel_id: int) -> None:
        await websocket.accept()
        if novel_id not in self.active_connections:
            self.active_connections[novel_id] = []
        self.active_connections[novel_id].append(websocket)

    def disconnect(self, websocket: WebSocket, novel_id: int) -> None:
        if novel_id in self.active_connections:
            self.active_connections[novel_id].remove(websocket)
            if not self.active_connections[novel_id]:
                del self.active_connections[novel_id]

    async def send_progress(
        self, novel_id: int, data: dict[str, Any]
    ) -> None:
        if novel_id in self.active_connections:
            message = json.dumps(data)
            disconnected = []
            for connection in self.active_connections[novel_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.append(connection)
            for conn in disconnected:
                self.disconnect(conn, novel_id)


manager = ConnectionManager()


@router.websocket("/ws/analysis/{novel_id}")
async def analysis_websocket(websocket: WebSocket, novel_id: int) -> None:
    await manager.connect(websocket, novel_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, novel_id)


async def broadcast_progress(novel_id: int, data: dict[str, Any]) -> None:
    await manager.send_progress(novel_id, data)
