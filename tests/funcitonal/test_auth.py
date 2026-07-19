import pytest

from src.modules.auth.auth_controller import AuthController
from src.modules.auth.auth_schema import LoginRequestSchema, RegisterRequestSchema


class TestUserAuth:
    @staticmethod
    @pytest.mark.asyncio
    async def test_user_registration(user_register_data, db_session):
        payload = RegisterRequestSchema(**user_register_data)
        controller = AuthController(db_session)
        response = await controller.register(payload)

        register_fields = ["name", "email", "phone_number"]

        for field in register_fields:
            assert getattr(response, field) == getattr(payload, field)

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_login(user_register_data, db_session):
        payload = RegisterRequestSchema(**user_register_data)
        controller = AuthController(db_session)
        await controller.register(payload)

        login_payload = LoginRequestSchema.model_validate(
            {
                "phone_number": user_register_data["phone_number"],
                "password": user_register_data["password"],
            }
        )

        response = await controller.login(login_payload)

        assert response.email == user_register_data["email"]
