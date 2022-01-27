import datetime
from pydantic import BaseModel, Field, validator

class Asset(BaseModel):
    created_on: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class Analytic(Asset):
    type: str = Field(default='analytic', description="Type of asset")
    url: str = Field(..., description="Scene S3 URI")
    date: datetime.datetime = Field(..., description="Julian date of scene")
    driver: str = Field(default="GeoTIFF", description="File type of scene, either GeoTIFF or JPEG2000")
    scene_id: str = Field(..., description="Scene ID")

class Thumbnail(Asset):
    type: str = Field(default='thumbnail', description="Type of asset")
    order: int = Field(..., description="Order of asset in list")
    url: str = Field(..., description="S3 URL to thumbnail")
    date: datetime.datetime = Field(..., description="Date of thumbnail")
    index: str = Field(..., description="Index of thumbnail")
    driver: str = Field(default="image/png", description="MIME type of thumbnail")
    scene_id: str = Field(..., description="Satquery Scene ID")
