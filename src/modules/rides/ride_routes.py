from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.rides.ride_controller import RideController
from src.modules.rides.ride_schema import RideRequestSchema
from src.shared.db.db_manager import get_db

router = APIRouter(prefix="/ride", tags=["ride"])


@router.post(
    "/book",
    status_code=status.HTTP_201_CREATED,
    # response_model=RegisterResponseSchema,
)
async def register(payload: RideRequestSchema, session: AsyncSession = Depends(get_db)):
    controller = RideController(session)
    return await controller.book_ride(payload)


# @router.post("/book",status_code=HTTP_201_CREATED)
# async def book_ride(payload,session: AsyncSession = Depends(get_db)):
#     controller=RideController(session)
