from typing import List, Union, Optional
import datetime

from pydantic import BaseModel, Field, validator

from .enum import AssetType

class Analytic(BaseModel):
    type: str = Field(default='analytic', description="Type of asset")
    url: str = Field(..., description="Scene S3 URI")
    date: datetime.datetime = Field(..., description="Date of scene")
    driver: str = Field(default="GeoTIFF", description="File type of scene, either GeoTIFF or JPEG2000")
    scene_id: str = Field(..., description="Scene ID")


class Thumbnail(BaseModel):
    type: str = Field(default='thumbnail', description="Type of asset")
    url: str = Field(..., description="S3 URL to thumbnail")
    date: datetime.datetime = Field(..., description="Date of thumbnail")
    driver: str = Field(default="image/png", description="MIME type of thumbnail")

Asset = Union[Analytic, Thumbnail]