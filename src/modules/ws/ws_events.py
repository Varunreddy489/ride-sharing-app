from enum import StrEnum


class WsRideEvents(StrEnum):
    RIDE_REQUEST = "ride.request"
    RIDE_ACCEPTED = "ride.accepted"
    RIDE_REJECTED = "ride.rejected"

    DRIVER_LOCATION = "driver.location"

    RIDE_STARTED = "ride.started"
    RIDE_COMPLETED = "ride.completed"

    HEARTBEAT = "heartbeat"
