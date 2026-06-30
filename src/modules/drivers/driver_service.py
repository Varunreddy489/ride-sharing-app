from geojson_pydantic import Point

from src.modules.drivers.driver_schema import (
    DriverLocationRequestSchema,
    DriverLocationResponseSchema,
    DriverRequestSchema,
    DriverResponseSchema,
    DriversInRangeResponseSchema,
    DriverStatusUpdateRequestSchema,
)
from src.shared.utils.exceptions import (
    DuplicateResourceException,
    ResourceNotFoundException,
)


class DriverService:
    def __init__(self, driver_repo):
        self.driver_repo = driver_repo

    async def register_driver(self, payload: DriverRequestSchema):

        # Todo: add a valid user check
        # is_valid_driver = await self.driver_repo.check_valid_user(payload.user_id)
        # if not is_valid_driver:
        #     raise ValidationException("Invalid user ID for driver registration.")
        is_existing_driver = await self.driver_repo.check_valid_user(payload.user_id)
        if is_existing_driver:
            raise DuplicateResourceException("Driver with this user ID already exists.")

        # change the role in users table (USER -> DRIVER)

        return await self.driver_repo.register_driver(payload)

    async def update_driver_status(
        self, payload: DriverStatusUpdateRequestSchema
    ) -> DriverResponseSchema:
        is_driver = await self.driver_repo.get_driver_by_id(payload.id)

        if not is_driver:
            raise ResourceNotFoundException("Driver with this ID does not exist.")

        return await self.driver_repo.update_status(payload)

    async def get_driver_status(self, id: int) -> DriverResponseSchema:
        is_driver = await self.driver_repo.get_driver_by_id(id)

        if not is_driver:
            raise ResourceNotFoundException("Driver with this ID does not exist.")

        return await self.driver_repo.get_driver_status(id)

    async def get_drivers_in_range(
        self, user_coordinates: Point, radius_km: float = 2.0
    ) -> DriversInRangeResponseSchema:
        """
        Fetch all available drivers within the specified radius from user's location.

        Args:
            user_coordinates: User's location as GeoJSON Point with [longitude, latitude]
                             Example: Point(coordinates=[78.4747, 17.3616])
                             where 78.4747°E is longitude and 17.3616°N is latitude
            radius_km: Search radius in kilometers (default: 2.0 km)

        Returns:
            DriversInRangeResponseSchema containing list of nearby drivers and count

        Example:
            user_point = Point(coordinates=[78.4747, 17.3616])  # Hyderabad coordinates
            result = await driver_service.get_drivers_in_range(user_point, radius_km=2.0)
            print(f"Found {result.count} drivers nearby")
        """
        drivers = await self.driver_repo.get_drivers_in_range(
            user_coordinates, radius_km
        )

        return DriversInRangeResponseSchema(
            drivers=drivers,
            count=len(drivers),
        )

    async def update_driver_location(
        self, payload: DriverLocationRequestSchema
    ) -> DriverLocationResponseSchema:
        """
        Update driver's current location.

        Args:
            payload: DriverLocationRequestSchema with driver_id and location (GeoJSON Point)
                    Location should be Point(coordinates=[longitude, latitude])

        Returns:
            DriverLocationResponseSchema with updated location
        """
        # Verify driver exists
        driver = await self.driver_repo.get_driver_by_id(payload.driver_id)
        if not driver:
            raise ResourceNotFoundException(
                f"Driver with ID {payload.driver_id} does not exist."
            )

        return await self.driver_repo.update_driver_location(
            payload.driver_id, payload.location
        )

    async def accept_ride(self, driver_id: int = None):
        return driver_id
