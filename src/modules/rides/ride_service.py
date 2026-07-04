from typing import Any

import pendulum

from src.modules.rides.ride_schema import RideLocationSchema, RideRequestSchema
from src.modules.ws.ws_manager import WebSocketManager
from src.shared.integrations.google_maps import get_distance
from src.shared.utils.enums import RideStatus
from src.shared.utils.exceptions import ResourceNotFoundException
from src.shared.utils.ride_utils import RideUtils


class RideService:
    def __init__(self, ride_repo, user_repo, driver_repo, redis_client):
        self.ride_repo = ride_repo
        self.user_repo = user_repo
        self.driver_repo = driver_repo
        self.ride_utils = RideUtils()
        self.ws_manager = WebSocketManager()
        self.redis_client = redis_client

    async def create_ride(self, payload: RideRequestSchema):
        """ """

        requested_time = pendulum.now("UTC")

        # Validate User
        valid_user = await self.user_repo.get_user_by_id(payload.id)

        if not valid_user:
            raise ResourceNotFoundException("User does not exist")

        # Calculate Distance
        distance = await get_distance(
            RideLocationSchema.model_validate(payload.model_dump())
        )

        # calculate fare
        fare = self.ride_utils.calculate_ride_fare(distance)

        # Create Ride first so all the drivers can see the ride request and accept it
        ride = await self.ride_repo.create_ride(
            payload=payload,
            fare=fare,
            distance=distance,
            requested_at=requested_time,
        )

        # get nearby drivers
        drivers = await self.driver_repo.get_nearby_drivers(payload.pickup_point, 2000)

        ride_payload = {
            "ride_id": ride.id,
            "pickup": payload.pickup_point,
            "dropoff": payload.dropoff_point,
            "fare": fare,
            "distance": distance,
        }

        for driver in drivers:
            await self.ws_manager.send_event(
                driver_id=driver.id,
                event="ride.request",
                data=ride_payload,
            )

        return {"ride_id": ride.id, "status": ride.status}

    async def accept_ride(self, ride_id: int, driver_id: int):
        """
        Accept Ride with Optimistic Locking
        """
        ride = await self.ride_repo.driver_accept_ride(ride_id, driver_id)

        await self.redis_client.cache_ride_status(ride_id, RideStatus.DRIVER_ARRIVING)

        if not ride:
            raise ResourceNotFoundException(
                "Ride not found or already accepted by another driver"
            )

        return {"ride_id": ride.id, "driver_id": driver_id, "status": ride.status}

    async def update_ride_event(self, ride_id: int, event: RideStatus):
        """
        Update Ride Event
        """
        ride: Any
        ride = await self.ride_repo.update_ride_status(ride_id, event)

        # Add Ride Status to Redis Cache
        await self.redis_client.cache_ride_status(ride_id, event)

        if not ride:
            raise ResourceNotFoundException("Ride not found")

        return {"ride_id": ride.id, "status": ride.status}
