from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from src.modules.ws.ws_manager import manager

router = APIRouter(prefix="/driver", tags=["driver"])


@router.websocket("/drivers}")
async def driver_ws(
    websocket: WebSocket,
    driver_id: int,
):
    await manager.connect(driver_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(driver_id)
