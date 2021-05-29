from typing import Tuple, Union
from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, validator

# types
NumType = Union[float, int]
Bounds = Tuple[NumType, NumType, NumType, NumType]

# database validators
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Geonos bounding box
class BboxModel(BaseModel):
    alias: str = Field(..., description="user-defined alias")
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user: str = Field(...)
    created_on: datetime = Field(default_factory=datetime.utcnow)
    coordinates: Tuple[NumType, NumType, NumType, NumType]
    area_m: NumType = Field(...)
    #start_time: datetime = Field(...)
    #end_time: datetime = Field(...)
    #cloud_cover: float = Field(...)

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
