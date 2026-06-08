from src.drivers.driver_schema import (
    DriverRequestSchema,
    DriverResponseSchema,
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
