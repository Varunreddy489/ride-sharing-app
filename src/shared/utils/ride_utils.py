from src.shared.utils.config import get_settings


class RideUtils:
    def __init__(self):
        self.settings = get_settings()

    def calculate_ride_fare(self, distance: float) -> float:
        """
        Calculate ride fare based on distance.
        """

        base_fare = self.settings.base_fare

        if distance <= 1:
            return base_fare

        elif distance <= 3:
            return base_fare + (distance * 15)

        elif distance <= 10:
            return base_fare + (distance * 10)

        else:
            return base_fare + (10 * 10) + ((distance - 10) * 8)
