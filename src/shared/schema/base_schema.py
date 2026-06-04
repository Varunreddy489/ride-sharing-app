from abc import ABC
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseResponsesSchema(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
