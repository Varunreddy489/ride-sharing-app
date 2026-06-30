from src.modules.auth.auth_schema import RegisterRequestSchema
from src.shared.utils.auth_utils import AuthUtils
from src.shared.utils.exceptions import DuplicateResourceException


class AuthService:
    def __init__(self, auth_repo):
        self.auth_repo = auth_repo
        self.utils = AuthUtils()

    async def register_user(self, payload: RegisterRequestSchema):

        existing_user = await self.auth_repo.check_user_exists(
            payload.email, payload.phone_number
        )
        if not existing_user:
            print(f"existing_user: {existing_user}")
            raise DuplicateResourceException(
                "User with this email or phone number already exists."
            )

        hashed_password = self.utils.hash_password(payload.password)
        payload.password = hashed_password

        return await self.auth_repo.create_user(payload)
