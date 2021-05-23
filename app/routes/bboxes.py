import os
import sys
sys.path.append('../')

from uuid import UUID
from typing import List

from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from dotenv import load_dotenv
import motor.motor_asyncio

from ..models.bbox import BboxModel

router = APIRouter()

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
db = client['query-ts-1']

@router.post(
    '/',
    response_description='Add new BBOX',
    response_model=BboxModel
)
async def create_bbox(bbox: BboxModel = Body(...)):
    bbox = jsonable_encoder(bbox)
    new_bbox = await db['bboxes'].insert_one(bbox)
    created_bbox = await db['bboxes'].find_one({"_id": new_bbox.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_bbox)

@router.get(
    '/{bbox_id}',
    response_description = 'Get BBOX by id',
    response_model = BboxModel
)
async def get_bbox_by_id(bbox_id):
    if (bbox := await db.bboxes.find_one({'_id': bbox_id})) is not None:
        return bbox

    raise HTTPException(status_code=404, detail=f"Bbox {id} not found")
