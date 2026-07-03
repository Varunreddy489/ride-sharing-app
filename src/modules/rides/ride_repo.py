import datetime

import pendulum
from sqlalchemy import select, update

from src.modules.rides.ride_model import RideModel
from src.modules.rides.ride_schema import RideRequestSchema
from src.shared.utils.enums import RideStatus


class RideRepo:
    def __init__(self, session):
        self.session = session

    async def create_ride(
        self,
        payload: RideRequestSchema,
        fare: float,
        distance: float,
        requested_at: datetime,
    ) -> RideModel:
        pickup_lon, pickup_lat = payload.pickup_point.coordinates
        dropoff_lon, dropoff_lat = payload.dropoff_point.coordinates

        ride = RideModel(
            rider_id=payload.rider_id,
            pickup_point=f"POINT({pickup_lon} {pickup_lat})",
            drop_off_point=f"POINT({dropoff_lon} {dropoff_lat})",
            status=payload.status,
            fare=fare,
            distance_km=distance,
            duration_minutes=payload.duration_minutes,
            requested_at=requested_at,
        )
        self.session.add(ride)
        self.session.commit()
        self.session.refresh(ride)
        return ride

    async def driver_accept_ride(
        self, ride_id: int, driver_id: int
    ) -> RideModel | None:
        # accept ride with optimistic locking
        result = await self.session.execute(
            select(
                RideModel.id,
                RideModel.lock_version,
                RideModel.status,
                RideModel.driver_id,
            ).where(RideModel.id == ride_id)
        )

        current = result.first()

        if current is None:
            return None

        if current.status != RideStatus.PENDING or current.driver_id is not None:
            return None

        accepted_at = pendulum.now("UTC").to_datetime_string()

        update_result = await self.session.execute(
            update(RideModel)
            .where(
                RideModel.id == ride_id,
                RideModel.lock_version == current.lock_version,
                RideModel.status == current.status,
                RideModel.driver_id == current.driver_id,
            )
            .values(
                driver_id=driver_id,
                status=RideStatus.PENDING,
                accepted_at=accepted_at,
                lock_version=current.lock_version + 1,
            )
            .returning(RideModel.id)
        )

        updated_id = update_result.scalar_one_or_none()

        if updated_id is None:
            return None

        ride = await self.session.get(RideModel, updated_id)
        return ride
