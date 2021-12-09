import os

from dotenv.main import load_dotenv
from fastapi.encoders import jsonable_encoder
import motor.motor_asyncio

from fastapi import APIRouter, status, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.item import Geometry, Item, ItemRequest, Properties
from ..tasks.image_stack import create_image_stack


router = APIRouter()

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
db = client['satquery-dev-db']

@router.post(
    '/',
    response_description='Add new STAC Item',
    response_model=Item,
    response_model_include={'alias'}
)
async def post_item(item_req: ItemRequest, background_tasks: BackgroundTasks):
    # read query properties from request body
    item_props = Properties(
        area_m=item_req.area_m,
        start_date=item_req.start_date,
        end_date=item_req.end_date,
        cloud_cover=item_req.cloud_cover,
        satellite=item_req.satellite,
        index=item_req.index,
    )
    # map bounding box to GeoJSON polygon
    item_geom = Geometry(
        type='Polygon',
        coordinates=[
            [
                (item_req.bbox[0], item_req.bbox[1]),
                (item_req.bbox[2], item_req.bbox[1]),
                (item_req.bbox[2], item_req.bbox[3]),
                (item_req.bbox[0], item_req.bbox[3]),
                (item_req.bbox[0], item_req.bbox[1])
            ],
        ]
    )
    # instantiate an Item object
    item = Item(
        bbox=item_req.bbox,
        geometry=item_geom,
        properties=item_props,
    )
    # encode item object to JSON
    item_json = jsonable_encoder(item)
    # insert item into database
    new_item = await db['items'].insert_one(item_json)
    # return item object as response
    created_item = await db['items'].find_one({"_id": new_item.inserted_id})
    # generate image stack
    background_tasks.add_task(
        create_image_stack, item_req.bbox, item_req.start_date, item_req.end_date, item_req.cloud_cover, item.id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item)