import sys
sys.path.append('../')

from uuid import uuid4
from typing import List
from datetime import datetime

from fastapi.encoders import jsonable_encoder

from models.bbox import BboxModel

async def create_user_bbox(coords, area):
    bbox = BboxOut(
        id=uuid4(),
        created_on=datetime.utcnow(),
        coordinates=coords,
        area_m=area
    )
    return bbox
