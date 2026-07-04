import json

from fastapi import APIRouter, Depends, WebSocket
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from src.modules.rides.ride_controller import RideController
from src.modules.ws.ws_manager import manager
from src.shared.db.db_manager import get_db
from src.shared.db.redis_manager import get_redis
from src.shared.utils.enums import RideStatus

router = APIRouter(prefix="/driver", tags=["driver"])


@router.websocket("/ws/{driver_id}")
async def driver_ws(
    websocket: WebSocket,
    driver_id: int,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    await manager.connect(driver_id, websocket)
    controller = RideController(session, redis)
    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)

            event = message.get("event")
            data = message.get("data")

            if event == RideStatus.DRIVER_ASSIGNED:
                await controller.accept_ride(data["ride_id"], driver_id)

    except WebSocketDisconnect:
        manager.disconnect(driver_id)
