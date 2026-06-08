from pydantic import BaseModel, ConfigDict, Field

from src.shared.schema.base_schema import BaseResponsesSchema


class DriverResponseSchema(BaseResponsesSchema):
    id: int = Field(..., description="Driver's unique identifier")
    user_id: int = Field(..., description="Driver's User ID")
    license_number: str = Field(..., description="Driver's license number")
    is_online: bool = Field(..., description="Driver's online status")
    is_available: bool = Field(..., description="Driver's availability status")


class DriverListResponseSchema(BaseResponsesSchema):
    drivers: list[DriverResponseSchema] = Field(..., description="List of drivers")


class DriverRequestSchema(BaseModel):
    user_id: int = Field(..., description="Driver's User ID")
    license_number: str = Field(..., description="Driver's license number")
    is_online: bool | None = Field(None, description="Driver's online status")
    is_available: bool | None = Field(None, description="Driver's availability status")


class DriverStatusUpdateRequestSchema(BaseModel):
    # Todo: Use decoded acccess_token for user_id
    id: int = Field(..., description="Driver's unique identifier")
    is_online: bool | None = Field(None, description="Driver's online status")
    is_available: bool | None = Field(None, description="Driver's availability status")


class DriverStatusResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_online: bool = Field(..., description="Driver's online status")
    is_available: bool = Field(..., description="Driver's availability status")
