from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.auth_repo import AuthRepo
from src.modules.auth.auth_schema import RegisterRequestSchema
from src.modules.auth.auth_service import AuthService


class AuthController:
    def __init__(self, session: AsyncSession):
        repo = AuthRepo(session)
        self.service = AuthService(repo)

    async def register(self, payload: RegisterRequestSchema):
        return await self.service.register_user(payload)
