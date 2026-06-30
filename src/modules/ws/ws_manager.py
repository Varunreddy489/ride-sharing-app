from fastapi import WebSocket

from src.modules.ws.ws_schema import WebRideSchema


class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, driver_id: int, ws: WebSocket):
        await ws.accept()
        self.active_connections[driver_id] = ws

    async def send_event(self, driver_id: int, event: str, data: dict):
        ws = self.active_connections.get(driver_id)
        if ws is None:
            return False
        try:
            message = WebRideSchema(event=event, data=data)
            await ws.send_json(message.model_dump())
            return True
        except Exception:
            self.disconnect(driver_id)
            return False

    def disconnect(self, driver_id: int):
        self.active_connections.pop(driver_id, None)


manager = WebSocketManager()
