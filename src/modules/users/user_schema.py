from pydantic import Field

from src.shared.schema.base_schema import BaseResponsesSchema
from src.shared.utils.enums import UserRoles


class UserResponseSchema(BaseResponsesSchema):
    id: int = Field(..., description="Users's unique identifier")
    name: str = Field(..., description="Users Name")
    email: str = Field(..., description="Users Email")
    phone_number: str = Field(..., description="Users Phone Number")
    role: UserRoles = Field(..., description="Users Role")
