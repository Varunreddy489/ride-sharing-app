from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.drivers.driver_repo import DriverRepo
from src.modules.rides.ride_repo import RideRepo
from src.modules.rides.ride_schema import RideRequestSchema
from src.modules.rides.ride_service import RideService
from src.modules.users.user_repo import UserRepo


class RideController:
    def __init__(self, session: AsyncSession):
        repo = RideRepo(session)
        user_repo = UserRepo(session)
        driver_repo = DriverRepo(session)
        self.service = RideService(repo, user_repo, driver_repo)

    async def book_ride(self, payload: RideRequestSchema):
        ride_data = await self.service.create_ride(payload)

    async def accept_ride(self, ride_id: int, driver_id: int):
        ride = await self.service.accept_ride(ride_id, driver_id)
        return ride
