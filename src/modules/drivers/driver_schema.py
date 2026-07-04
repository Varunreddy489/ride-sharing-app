from geojson_pydantic import Point
from pydantic import BaseModel, ConfigDict, Field

from src.shared.schema.base_schema import BaseResponsesSchema


class DriverResponseSchema(BaseResponsesSchema):
    id: int = Field(..., description="Driver's unique ")
    user_id: int = Field(..., description="Driver's User ID")
    license_number: str = Field(..., description="Driver's license number")
    is_online: bool = Field(..., description="Driver's online status")
    is_available: bool = Field(..., description="Driver's availability status")


class DriverListResponseSchema(BaseResponsesSchema):
    drivers: list[DriverResponseSchema] = Field(..., description="List of drivers")


class DriverLocationRequestSchema(BaseModel):
    """Schema for updating driver location"""

    driver_id: int = Field(..., description="Driver's ID")
    location: Point = Field(
        ..., description="Driver's current location as GeoJSON Point"
    )


class DriverLocationResponseSchema(BaseResponsesSchema):
    """Schema for driver location response"""

    id: int = Field(..., description="Location record ID")
    driver_id: int = Field(..., description="Driver's ID")
    location: Point = Field(..., description="Driver's location as GeoJSON Point")


class DriverWithLocationResponseSchema(BaseResponsesSchema):
    """Schema for driver with location info"""

    id: int = Field(..., description="Driver's unique ID")
    user_id: int = Field(..., description="Driver's User ID")
    license_number: str = Field(..., description="Driver's license number")
    is_online: bool = Field(..., description="Driver's online status")
    is_available: bool = Field(..., description="Driver's availability status")
    location: Point | None = Field(None, description="Driver's current location")


class DriversInRangeResponseSchema(BaseResponsesSchema):
    """Schema for drivers within a specified radius"""

    drivers: list[DriverWithLocationResponseSchema] = Field(
        ..., description="List of drivers within range"
    )
    count: int = Field(..., description="Number of drivers found")


class DriverRequestSchema(BaseModel):
    user_id: int = Field(..., description="Driver's User ID")
    license_number: str = Field(..., description="Driver's license number")
    is_online: bool | None = Field(None, description="Driver's online status")
    is_available: bool | None = Field(None, description="Driver's availability status")


class DriverStatusUpdateRequestSchema(BaseModel):
    # Todo: Use decoded access_token for user_id
    id: int = Field(..., description="Driver's unique identifier")
    is_online: bool | None = Field(None, description="Driver's online status")
    is_available: bool | None = Field(None, description="Driver's availability status")


class DriverStatusResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_online: bool = Field(..., description="Driver's online status")
    is_available: bool = Field(..., description="Driver's availability status")
