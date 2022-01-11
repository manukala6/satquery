import os
from typing import Tuple
from datetime import datetime

import boto3
import asyncio
from dotenv import load_dotenv
import motor.motor_asyncio
from satsearch import Search
from PIL import Image
from rio_tiler.utils import render, linear_rescale

from ..models.types import NumType
from ..models.assets import Asset
from .utils import parse_sentinel2, read_window

load_dotenv()

# connect to db
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
db = client['satquery-dev-db']

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
    item_id: str
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
    ndvis = []
    for i in range(len(scenedicts)):
        ndvis.append((nirs[i] - reds[i]) / (nirs[i] + reds[i]))

    # rescale and convert to bytes
    print('Rescaling and rendering')
    rescaled = [linear_rescale(ndvi, (-1,1)).astype('uint8') for ndvi in ndvis]
    for i in range(len(rescaled)):
        upload_bytes_to_s3(render(rescaled[i]), 'satquery-dec-test', f'{item_id}/{i}_{item_id}.png')
    
    # update database with new image stack
    print('Updating database')

    
    #for i in range(len(rescaled)):
    #    yield render(rescaled[i])
    #    await asyncio.sleep(0.5)