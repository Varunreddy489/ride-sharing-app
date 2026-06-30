from pydantic import BaseModel

from src.modules.ws.ws_events import WsRideEvents


class WebRideSchema(BaseModel):
    event: WsRideEvents
    data: any
