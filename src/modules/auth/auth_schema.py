from pydantic import BaseModel, Field

from src.shared.schema.base_schema import BaseResponsesSchema
from src.shared.utils.enums import UserRoles


class RegisterRequestSchema(BaseModel):
    name: str = Field(..., description="User's name")
    email: str = Field(..., description="User's email")
    phone_number: str = Field(..., description="User's phone number")
    role: UserRoles | None = Field(None, description="User's role")
    password: str = Field(..., description="User's password")


class RegisterResponseSchema(BaseResponsesSchema):
    id: int = Field(..., description="User's unique identifier")
    name: str = Field(..., description="User's name")
    email: str = Field(..., description="User's email")
    phone_number: str = Field(..., description="User's phone number")
    role: UserRoles = Field(..., description="User's role")
    access_token: str | None = Field(None, description="Access token")


class LoginRequestSchema(BaseModel):
    phone_number: str = Field(..., description="User's phone number")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")
