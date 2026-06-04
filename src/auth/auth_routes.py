from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_controller import AuthController
from src.auth.auth_schema import RegisterRequestSchema, RegisterResponseSchema
from src.shared.db.db_manager import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponseSchema,
)
async def register(
    payload: RegisterRequestSchema, session: AsyncSession = Depends(get_db)
):
    controller = AuthController(session)
    return await controller.register(payload)
