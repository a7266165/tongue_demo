"""WebSocket endpoint for real-time pipeline progress updates."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..pipeline.base import PipelineContext
from ..storage.file_store import image_to_base64

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected (%d total)", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected (%d total)", len(self.active_connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a message to all connected clients."""
        text = json.dumps(message, default=str)
        for conn in self.active_connections:
            try:
                await conn.send_text(text)
            except Exception:
                logger.warning("Failed to send to a WebSocket client")


manager = ConnectionManager()


async def notify_step_complete(step_name: str, ctx: PipelineContext) -> None:
    """Callback for pipeline runner to notify clients of step completion."""
    import numpy as np

    message: dict[str, Any] = {
        "type": "step_complete",
        "step": step_name,
        "results": ctx.results.get(step_name, {}),
    }

    # Include latest intermediate image if available
    for key, img in ctx.intermediate_images.items():
        if key.startswith(step_name) or step_name in key:
            if isinstance(img, np.ndarray):
                message["image"] = image_to_base64(img)
                break

    await manager.broadcast(message)


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            logger.debug("Received from client: %s", data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
