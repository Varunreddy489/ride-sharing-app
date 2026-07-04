from src.modules.users.user_model import UserModel
from src.modules.users.user_schema import UserResponseSchema
from src.shared.utils.enums import UserRoles
from src.shared.utils.exceptions import ResourceNotFoundException


class UserRepo:
    def __init__(self, session):
        self.session = session

    async def change_user_role(self, user_id: int) -> UserResponseSchema:
        user = await self.session.get(UserModel, user_id)

        user.role = UserRoles.DRIVER
        await self.session.commit()
        await self.session.refresh(user)

        return UserResponseSchema.model_validate(user)

    async def get_user_by_id(self, id: int) -> UserResponseSchema:
        user = await self.session.ger(UserModel, id)

        if not user:
            raise ResourceNotFoundException("User not found")

        return UserResponseSchema.model_validate(user)
