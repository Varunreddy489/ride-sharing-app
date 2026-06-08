from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.drivers.driver_controller import DriverController
from src.drivers.driver_schema import (
    DriverRequestSchema,
    DriverResponseSchema,
    DriverStatusUpdateRequestSchema,
)
from src.shared.db.db_manager import get_db

router = APIRouter(prefix="/driver", tags=["driver"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=DriverResponseSchema,
)
async def register(
    payload: DriverRequestSchema, session: AsyncSession = Depends(get_db)
) -> DriverResponseSchema:
    controller = DriverController(session)
    return await controller.register_driver(payload)


@router.patch("/status", status_code=status.HTTP_200_OK)
async def update_status(
    payload: DriverStatusUpdateRequestSchema, session: AsyncSession = Depends(get_db)
):
    controller = DriverController(session)
    return await controller.update_status(payload)


@router.get("/status/{id}", status_code=status.HTTP_200_OK)
async def get_status(id: int, session: AsyncSession = Depends(get_db)):
    controller = DriverController(session)
    return await controller.get_status(id)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=DriverResponseSchema,
)
async def get_driver(id: int, session: AsyncSession = Depends(get_db)):
    controller = DriverController(session)
    return await controller.get_driver(id)
