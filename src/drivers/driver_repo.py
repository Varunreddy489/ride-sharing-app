from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.drivers.driver_model import DriverModel
from src.drivers.driver_schema import (
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
