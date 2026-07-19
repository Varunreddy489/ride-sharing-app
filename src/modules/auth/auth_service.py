from src.modules.auth.auth_schema import (
    LoginRequestSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
)
from src.shared.utils.auth_utils import AuthUtils
from src.shared.utils.exceptions import (
    DuplicateResourceException,
    InvalidPasswordException,
)


class AuthService:
    def __init__(self, auth_repo):
        self.auth_repo = auth_repo
        self.utils = AuthUtils()

    async def register_user(
        self, payload: RegisterRequestSchema
    ) -> RegisterResponseSchema:

        existing_user = await self.auth_repo.check_user_exists(payload.phone_number)
        if existing_user:
            raise DuplicateResourceException(
                "User with this phone number already exists."
            )

        hashed_password = self.utils.hash_password(payload.password)
        payload.password = hashed_password

        response = await self.auth_repo.create_user(payload)

        access_token = self.utils.create_access_token(response.id, response.role)

        return response.model_copy(update={"access_token": access_token})

    async def login_user(self, payload: LoginRequestSchema):
        # Use phone_number for login, return RegisterResponseSchema with token
        user = await self.auth_repo.check_user_exists(payload.phone_number)
        if not user:
            raise Exception("User not found.")

        if not self.utils.verify_password(payload.password, user.password):
            raise InvalidPasswordException("Invalid password.")

        access_token = self.utils.create_access_token(user.id, user.role)
        response = RegisterResponseSchema.model_validate(user)
        return response.model_copy(update={"access_token": access_token})
