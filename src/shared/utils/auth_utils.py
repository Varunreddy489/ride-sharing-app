import uuid

import jwt
import pendulum
from pwdlib import PasswordHash

from src.shared.utils.config import get_settings
from src.shared.utils.enums import UserRoles


class AuthUtils:
    def __init__(self):
        self.password_hash = PasswordHash.recommended()
        self.settings = get_settings()

    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def create_access_token(self, user_id: int, role: UserRoles) -> str:
        now = pendulum.now()
        expire = now.add(minutes=self.settings.jwt_expire_minutes)

        jwt_payload = {
            "sub": str(user_id),
            "role": role.value,
            "iat": now.int_timestamp,
            "exp": expire.int_timestamp,
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(
            jwt_payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm
        )
