from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.auth_schema import RegisterRequestSchema, RegisterResponseSchema
from src.modules.users.user_model import UserModel


class AuthRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> RegisterResponseSchema | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalar_one_or_none()
        return RegisterResponseSchema.model_validate(user) if user else None

    async def check_user_exists(self, phone_number: str) -> UserModel:
        result = await self.session.execute(
            select(UserModel).where(UserModel.phone_number == phone_number)
        )
        user = result.scalar_one_or_none()

        return user

    async def create_user(
        self, payload: RegisterRequestSchema
    ) -> RegisterResponseSchema:
        new_user = payload.model_dump()
        user = UserModel(**new_user)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return RegisterResponseSchema.model_validate(user)
