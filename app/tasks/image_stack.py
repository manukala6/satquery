import os
from typing import Tuple
from datetime import datetime

import boto3
from satsearch import Search
from rio_tiler.utils import render, linear_rescale

from ..models import NumType
from .utils import parse_sentinel2, read_window

# set up boto3 session
#TODO try/except error
def set_up_boto3_session():
    boto3_session = boto3.Session(
        os.environ.get('AWS_ACCESS_KEY_ID'), 
        os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    return boto3_session

def create_image_stack(
    coordinates: Tuple[NumType, NumType, NumType, NumType], 
    start_time: str = '2018-02-12T00:00:00Z', 
    end_time: str = '2018-04-18T12:31:12Z', 
    cloud_cover: float = 10
):
    timerange = f'{start_time}/{end_time}'
    search = Search(
        bbox=coordinates,
        datetime=timerange,
        query={'eo:cloud_cover': cloud_cover},
        url='https://earth-search.aws.element84.com/v0',
        collections=['sentinel-s2-l2a']
    )

    # list items from satsearch query
    items = [str(item) for item in search.items()]

    # parse sentinel2 scene IDs
    scenedicts = [parse_sentinel2(str(item)) for item in items]

    # read windows for red and nir bands
    boto3_session = set_up_boto3_session()
    reds = [read_window(scenedict, coordinates, 'B04', boto3_session) for scenedict in scenedicts]
    nirs = [read_window(scenedict, coordinates, 'B08', boto3_session) for scenedict in scenedicts]

    # calculate ndvi
    ndvis = []
    for i in range(len(scenedicts)):
        ndvis.append((nirs[i] - reds[i]) / (nirs[i] + reds[i]))

    # rescale and convert to bytes
    rescaled = linear_rescale(ndvis[2], (-1,1))
    int_rescaled = rescaled.astype('uint8')
    bits = render(int_rescaled)
    return bits
