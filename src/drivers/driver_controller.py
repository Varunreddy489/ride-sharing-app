from sqlalchemy.ext.asyncio import AsyncSession

from src.drivers.driver_repo import DriverRepo
from src.drivers.driver_schema import (
    DriverRequestSchema,
    DriverResponseSchema,
    DriverStatusUpdateRequestSchema,
)
from src.drivers.driver_service import DriverService


class DriverController:
    def __init__(self, session: AsyncSession):
        repo = DriverRepo(session)
        self.service = DriverService(repo)

    async def register_driver(self, payload: DriverRequestSchema):
        return await self.service.register_driver(payload)

    async def update_status(
        self, payload: DriverStatusUpdateRequestSchema
    ) -> DriverResponseSchema:
        return await self.service.update_driver_status(payload)

    async def get_driver(self, id: int) -> DriverResponseSchema:
        return await self.service.get_driver_status(id)

    async def get_status(self, id: int) -> DriverResponseSchema:
        return await self.service.get_driver_status(id)
