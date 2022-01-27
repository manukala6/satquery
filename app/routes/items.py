from fastapi.encoders import jsonable_encoder
from fastapi.params import Body

from fastapi import APIRouter, status, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse

import pprint

from ..models.item import Geometry, Item, ItemRequest, Properties, UpdateItem
from ..tasks.image_stack import create_image_stack

def item_router(app):
    
    router = APIRouter()

    @router.get(
        '/{item_id}',
        response_description = 'Get STAC Item by id',
        response_model = Item,
        response_model_include={"alias"}
    )
    async def get_item_by_id(request: Request, item_id: str):
        if (item := await request.app.mongodb.items.find_one({'_id': item_id})) is not None:
            print('Item found')
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(item))
        raise HTTPException(status_code=404, detail=f"Item {id} not found")

    @router.post(
        '/',
        response_description='Add new STAC Item',
        response_model=Item,
        response_model_include={'alias'}
    )
    async def post_item(request: Request, item_req: ItemRequest, background_tasks: BackgroundTasks):
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
        new_item = await request.app.mongodb['items'].insert_one(item_json)
        # return item object as response
        created_item = await request.app.mongodb['items'].find_one({"_id": new_item.inserted_id})
        print('created item: %s' % pprint.pformat(created_item))
        # generate image stack
        background_tasks.add_task(
            create_image_stack, item_req.bbox, item_req.start_date, item_req.end_date, item_req.cloud_cover, new_item.inserted_id, request.app.mongodb
        )

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item)

    @router.put(
        '/{item_id}',
        response_description='Update a STAC Item',
        response_model=Item,
        response_model_include={'alias'}
    )
    async def put_item(request: Request, item_id: str, update_item_req: UpdateItem = Body(...)):
        update_item_req = {k: v for k, v in update_item_req.dict().items() if v is not None}

        if len(update_item_req) >= 1:
            update_result = await request.app.mongodb['items'].update_one({'_id': item_id}, {'$set': update_item_req})

            if update_result.modified_count == 1:
                if (
                    updated_item := await request.app.mongodb["items"].find_one({"_id": item_id})
                ) is not None:
                    return JSONResponse(status_code=status.HTTP_201_CREATED, content=updated_item)

        if (existing_item := await request.app.mongodb["items"].find_one({"_id": item_id})):
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=existing_item)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return router