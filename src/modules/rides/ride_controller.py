from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.rides.ride_repo import RideRepo
from src.modules.rides.ride_schema import RideRequestSchema
from src.modules.rides.ride_service import RideService
from src.modules.users.user_repo import UserRepo


class RideController:
    def __init__(self, session: AsyncSession):
        repo = RideRepo(session)
        user_repo = UserRepo(session)
        self.service = RideService(repo, user_repo)

    async def book_ride(self, payload: RideRequestSchema):

        await self.service.book_ride(payload)
