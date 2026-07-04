from abc import ABC
from datetime import datetime

from geojson_pydantic import Point
from pydantic import BaseModel, Field, model_validator

from src.shared.utils.enums import RideStatus


class BaseRideRequestSchema(BaseModel, ABC):
    rider_id: int = Field(..., description="User`s Id")

    pickup_point: Point = Field(..., ge=-90, le=90)

    status: RideStatus = Field(..., description="Ride Status")
    fare: float = Field(..., description="Ride for fare")
    distance_km: float = Field(..., description="Requested Ride Distance")
    duration_minutes: float = Field(..., description="ETA Ride Completion duration")
    requested_at: datetime = Field(..., description="Ride Requested Dt")


class RideLocationSchema(BaseModel, ABC):
    pickup_point: Point
    dropoff_point: Point

    @model_validator(mode="after")
    def validate_coordinates(self):
        for point in [self.pickup_point, self.dropoff_point]:
            lon, lat = point.coordinates

            if not (-180 <= lon <= 180):
                raise ValueError("Longitude must be between -180 and 180")

            if not (-90 <= lat <= 90):
                raise ValueError("Latitude must be between -90 and 90")

        return self


class RideRequestSchema(RideLocationSchema):
    rider_id: int = Field(..., description="User`s Id")
