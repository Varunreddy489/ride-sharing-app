from src.shared.constants import VALID_RIDE_TRANSITIONS
from src.shared.utils.enums import RideStatus
from src.shared.utils.exceptions import InvalidStateTransitionError


def validate_transition(curr_status: RideStatus, next_status: RideStatus):
    if next_status not in VALID_RIDE_TRANSITIONS.get(curr_status, set()):
        raise InvalidStateTransitionError(
            f"Cannot transition from {curr_status} to {next_status}"
        )
