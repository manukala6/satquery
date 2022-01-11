from typing import List, Union, Optional
import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, validator

from app.models import bbox

from .enum import AssetType
from .assets import Asset
from .types import Coordinate, NumType, Bounds
from .db import PyObjectId

class Geometry(BaseModel):
    type: str = 'Feature'
    coordinates: List[List[Coordinate]]

class Properties(BaseModel):
    created_on: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    area_m: NumType = Field(...)
    start_date: str = Field(..., description="Filter by scenes after this date. In YYYY-MM-DD format.")
    end_date: str = Field(...,  description="Filter by scenes before this date. In YYYY-MM-DD format")
    cloud_cover: int = Field(default=25, description="Maximum cloud cover percentage, between 1-100")
    satellite: str = Field(default="Sentinel-2", description="Satellite name")
    index: str = Field(default='NDVI', description="Spectral index")



class Assets(BaseModel):
    assets: List[Asset] = list()
    
class ItemRequest(BaseModel):
    area_m: NumType = Field(...)
    start_date: str = Field(..., description="Filter by scenes after this date. In YYYY-MM-DD format.")
    end_date: str = Field(...,  description="Filter by scenes before this date. In YYYY-MM-DD format")
    cloud_cover: int = Field(default=25, description="Maximum cloud cover percentage, between 1-100")
    satellite: str = Field(default="Sentinel-2", description="Satellite name")
    index: str = Field(default='NDVI', description="Spectral index")
    bbox: Bounds = Field(..., description="Bounding box of GeoJSON Feature")
    
    @validator('area_m')
    def area_m_below_50sqkm(cls, v):
        if v > 50000000:
            raise ValueError('Area of bounding box must be below 50 square meters')
        return v

class Item(BaseModel):
    stac_version: str = Field(default="1.0.0")
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    bbox: Bounds = Field(..., description="Bounding box of GeoJSON Feature")
    geometry: Geometry = Field(..., description="GeoJSON Feature")
    properties: Properties = Field(..., description="Sat-query search parameters")
    assets: Optional[Assets]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UpdateItem(BaseModel):
    stac_version: Optional[str]
    bbox: Optional[Bounds]
    geometry: Optional[Geometry]
    properties: Optional[Properties]
    assets: Optional[Assets] 

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}