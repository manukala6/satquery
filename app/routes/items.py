import os

from dotenv.main import load_dotenv
from fastapi.encoders import jsonable_encoder
import motor.motor_asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ..models.item import Item


router = APIRouter()

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
mongo = client['Satquery-1']
db = mongo['satquery-dev-db']

@router.post(
    '/',
    response_description='Add new STAC Item',
    response_model=Item,
    response_model_include={"alias"}
)
async def post_item(item: Item):
    item_json = jsonable_encoder(item)
    new_item = await db['items'].insert_one(item_json)
    created_item = await db['items'].find_one({"_id": new_item.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item)
