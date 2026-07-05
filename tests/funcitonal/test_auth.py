import pytest

from src.modules.auth.auth_controller import AuthController
from src.modules.auth.auth_schema import RegisterRequestSchema


class TestUserAuth:
    @staticmethod
    @pytest.mark.asyncio
    async def test_user_registration(user_register_data, db_session):
        payload = RegisterRequestSchema(**user_register_data)
        controller = AuthController(db_session)
        response = await controller.register(payload)
        assert response.name == payload.name
