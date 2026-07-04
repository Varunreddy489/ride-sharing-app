from http import HTTPStatus

from src.shared.utils.enums import RideStatus

VALID_RIDE_TRANSITIONS: dict[RideStatus, set[RideStatus]] = {
    RideStatus.PENDING: {
        RideStatus.DRIVER_ASSIGNED,
        RideStatus.REJECTED,
        RideStatus.CANCELED,
    },
    RideStatus.DRIVER_ASSIGNED: {
        RideStatus.DRIVER_ARRIVING,
        RideStatus.REJECTED,
        RideStatus.CANCELED,
    },
    RideStatus.DRIVER_ARRIVING: {RideStatus.REJECTED, RideStatus.CANCELED},
    RideStatus.DRIVER_ARRIVED: {RideStatus.RIDE_STARTED, RideStatus.CANCELED},
    RideStatus.RIDE_STARTED: {RideStatus.IN_PROGRESS},
    RideStatus.IN_PROGRESS: {RideStatus.COMPLETED},
    RideStatus.CANCELED: set(),
    RideStatus.TIMED_OUT: set(),
    RideStatus.REJECTED: set(),
}

RETRYABLE_HTTP_ERROR_CODES = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]
