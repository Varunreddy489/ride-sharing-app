from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.auth_schema import RegisterRequestSchema, RegisterResponseSchema
from src.modules.users.user_model import UserModel


class AuthRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_user_exists(self, email: str, phone_number: str) -> bool:
        is_email = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        is_phone_number = await self.session.execute(
            select(UserModel).where(UserModel.phone_number == phone_number)
        )

        return (
            is_email.scalar_one_or_none() is None
            or is_phone_number.scalar_one_or_none() is None
        )

    async def create_user(
        self, payload: RegisterRequestSchema
    ) -> RegisterResponseSchema:
        new_user = payload.model_dump()
        user = UserModel(**new_user)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return RegisterResponseSchema.model_validate(user)
