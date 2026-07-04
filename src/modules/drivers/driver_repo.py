from geojson_pydantic import Point
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.drivers.driver_location_model import DriverLocationModel
from src.modules.drivers.driver_model import DriverModel
from src.modules.drivers.driver_schema import (
    DriverLocationRequestSchema,
    DriverResponseSchema,
    DriverStatusResponseSchema,
    DriverStatusUpdateRequestSchema,
)
from src.shared.utils.exceptions import ResourceNotFoundException


class DriverRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_valid_user(self, user_id: int) -> bool:
        result = await self.session.execute(
            select(DriverModel).where(DriverModel.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_driver_by_id(self, id: int) -> DriverResponseSchema:
        result = await self.session.execute(
            select(DriverModel).where(DriverModel.id == id)
        )

        driver = result.scalar_one_or_none()

        if driver is None:
            raise ResourceNotFoundException("Driver with this ID does not exist.")

        return DriverResponseSchema.model_validate(driver)

    async def register_driver(self, payload) -> DriverResponseSchema:
        new_driver = payload.model_dump()
        driver = DriverModel(**new_driver)
        self.session.add(driver)
        await self.session.commit()
        await self.session.refresh(driver)
        return DriverResponseSchema.model_validate(driver)

    async def update_status(
        self, payload: DriverStatusUpdateRequestSchema
    ) -> DriverResponseSchema:
        driver = await self.session.get(DriverModel, payload.id)

        driver.is_online = payload.is_online
        driver.is_available = payload.is_available

        await self.session.commit()
        await self.session.refresh(driver)

        return DriverResponseSchema.model_validate(driver)

    async def get_driver_status(self, id: int) -> DriverStatusResponseSchema:
        driver = await self.session.get(DriverModel, id)

        return DriverStatusResponseSchema.model_validate(driver)

    async def update_drivers_locations(
        self, payload: DriverLocationRequestSchema
    ) -> DriverLocationRequestSchema:
        new_driver_location = payload.model_dump()
        driver_location = DriverLocationModel(**new_driver_location)

        self.session.add(driver_location)
        await self.session.commit()
        await self.session.refresh(driver_location)
        return DriverLocationRequestSchema.model_validate(driver_location)

    async def get_nearby_drivers(
        self,
        user_location: Point,
        search_radius_meters: int,
    ):
        longitude = user_location.coordinates[0]
        latitude = user_location.coordinates[1]

        pickup_point = func.ST_GeogFromText(f"SRID=4326;POINT({longitude} {latitude})")

        stmt = (
            select(DriverModel)
            .join(
                DriverLocationModel,
                DriverLocationModel.driver_id == DriverModel.id,
            )
            .where(
                DriverModel.is_online.is_(True),
                DriverModel.is_available.is_(True),
                func.ST_DWithin(
                    DriverLocationModel.location,
                    pickup_point,
                    search_radius_meters,
                ),
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
