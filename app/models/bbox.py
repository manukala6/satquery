from typing import Tuple, Union
import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, validator

from .db import PyObjectId
from .types import NumType

# Geonos bounding box
class BboxModel(BaseModel):
    #alias: str = Field(..., description="user-defined alias")
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user: str = Field(...)
    created_on: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    coordinates: Tuple[NumType, NumType, NumType, NumType] = Field(..., description="Bounding box of query area in xmin, ymin, xmax, ymax format")
    area_m: NumType = Field(...)
    start_date: str = Field(..., description="Filter by scenes after this date. In YYYY-MM-DD format.")
    end_date: str = Field(...,  description="Filter by scenes before this date. In YYYY-MM-DD format")
    cloud_cover: int = Field(default=25, description="Maximum cloud cover percentage, between 1-100")

    @validator('area_m')
    def area_m_below_50sqkm(cls, v):
        if v > 50000000:
            raise ValueError('Area of bounding box must be below 50 square meters')
        return v

 #   @validator('coordinates')
 #   def four_coordinates(cls, v):
 #       if len(v) != 5:
 #           raise ValueError('Bounding box must have only four coordinates')
 #       return v

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
