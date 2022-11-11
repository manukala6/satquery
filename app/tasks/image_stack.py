import os
import pprint 
from typing import Tuple
from datetime import datetime

import boto3
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
import numpy as np
from satsearch import Search
from PIL import Image
from rio_tiler.utils import render, linear_rescale
from fastapi.params import Body

from app.models.item import UpdateItem
from ..models.types import NumType
from ..models.assets import Thumbnail, Analytic
from .utils import parse_sentinel2, read_window

load_dotenv()

# TODO
# 1. connect to db (create function in db.py)
# 2. upload image bytes to s3 (create function in utils.py?)
# 3. perform a query that returns a dictionary of scenes
# 4. parse the dictionary using functions specific to satellite type
# 5. identify index and read the bands
# 6. calculate the index
# 7. generate images with desired colormap
# 8. upload images to s3
# 9. update database with new image stack (create function in db.py)

# set up boto3 session
#TODO try/except error
def set_up_boto3_session():
    boto3_session = boto3.Session(
        os.environ.get('AWS_ACCESS_KEY_ID'), 
        os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    return boto3_session

def upload_bytes_to_s3(bytes, bucket, key):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=key, Body=bytes)

async def create_image_stack(
    coordinates: Tuple[NumType, NumType, NumType, NumType],
    start_date: str, 
    end_date: str, 
    cloud_cover: int,
    item_id: str,
    db
):
    timerange = f'{start_date}/{end_date}'
    search = Search(
        bbox=coordinates,
        datetime=timerange,
        query={'eo:cloud_cover': cloud_cover},
        url='https://earth-search.aws.element84.com/v0',
        collections=['sentinel-s2-l2a'] ##TODO: support sentinel-1 and landsat-8
    )

    # list items from satsearch query ##TODO: possible optimization
    scenes = [str(item) for item in search.items()]
    print(f'Found {len(scenes)} Sentinel-2 scenes')

    # parse satellite scene IDs ##TODO: add parsing for landsat-8 and sentinel-1
    scenedicts = [parse_sentinel2(str(scene)) for scene in scenes]

    # COMPUTE INDEX (NDVI-only for now)
    # read windows for red and nir bands
    boto3_session = set_up_boto3_session()
    print('Collecting red band')
    reds = [read_window(scenedict, coordinates, 'B04', boto3_session) for scenedict in scenedicts]
    print('Collecting near infrared band')
    nirs = [read_window(scenedict, coordinates, 'B08', boto3_session) for scenedict in scenedicts]

    # calculate ndvi 
    print('Calculating NDVI')
    ndvi_arrs = []
    ndvi_num = []
    for i in range(len(scenedicts)):
        ndvi_arr = (nirs[i] - reds[i]) / (nirs[i] + reds[i])
        ndvi_arrs.append(ndvi_arr)
        ndvi_num.append(np.mean(ndvi_arr))


    # rescale and convert to bytes
    print('Rescaling and rendering')
    rescaled = [linear_rescale(ndvi_arr, (-1,1)).astype('uint8') for ndvi_arr in ndvi_arrs]
    for i in range(len(rescaled)):
        upload_bytes_to_s3(render(rescaled[i]), 'satquery-dec-test', f'{item_id}/{i}_{item_id}.png')
    
    # update database with new image stack
    print('Updating database')
    assets = []
    for i in range(len(rescaled)):
        asset_dict = {
            'type': 'thumbnail',
            'order': i,
            'url': f'https://satquery-dec-test.s3.amazonaws.com/{item_id}/{i}_{item_id}.png',
            'date': datetime.utcnow(),
            'driver': 'image/png',
            'index': 'NDVI',
            'value': ndvi_num[i],
            'scene_id': str(item_id)
        }
        new_asset = await db.assets.insert_one(
            jsonable_encoder(asset_dict)
        )
        assets.append(jsonable_encoder(Thumbnail(**asset_dict)))
    update_item_req = {k: v for k, v in UpdateItem(assets=assets).dict().items() if v is not None}
    print(update_item_req)
    old_document = await db.items.find_one(filter={'_id': item_id})
    print('old document was %s' % pprint.pformat(old_document))
    update_result = await db.items.update_one(filter={'_id': item_id}, update={'$set': jsonable_encoder(update_item_req)})
    print('updated %s document' % update_result.modified_count)
    new_document = await db.items.find_one(filter={'_id': item_id})
    print('document is now %s' % pprint.pformat(new_document))
    print('Done')