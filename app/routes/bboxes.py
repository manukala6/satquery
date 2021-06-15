import os
import io

from typing import List

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import motor.motor_asyncio

from ..models.bbox import BboxModel
from ..tasks.image_stack import create_image_stack

router = APIRouter()

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
db = client['query-ts-1']

@router.put(
    '/',
    response_description='Add new BBOX',
    response_model=BboxModel,
    response_model_include={"alias"}
)
async def put_bbox(bbox: BboxModel, background_tasks: BackgroundTasks):
    #bbox_json = jsonable_encoder(bbox)
    #new_bbox = await db['bboxes'].insert_one(bbox_json)
    #created_bbox = await db['bboxes'].find_one({"_id": new_bbox.inserted_id})
    #background_tasks.add_task(create_image_stack, bbox.coordinates)
    bits = create_image_stack(bbox.coordinates, bbox.start_date, bbox.end_date, bbox.cloud_cover)
    return StreamingResponse(bits, media_type="image/png")
    #return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_bbox)

@router.get(
    '/{bbox_id}',
    response_description = 'Get BBOX by id',
    response_model = BboxModel
)
async def get_bbox_by_id(bbox_id: str):
    if (bbox := await db.bboxes.find_one({'_id': bbox_id})) is not None:
        return bbox

    raise HTTPException(status_code=404, detail=f"Bbox {id} not found")
