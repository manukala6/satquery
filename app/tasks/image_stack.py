import os
from typing import Tuple
from datetime import datetime

import boto3
from satsearch import Search

from ..models import NumType
from .utils import parse_sentinel2, read_window

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

    # set up boto3 session
    boto3_session = boto3.Session(
        os.environ.get('AWS_ACCESS_KEY_ID'), 
        os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

    # read windows for red and nir bands
    reds = [read_window(scenedict, coordinates, 'B04') for scenedict in scenedicts]
    nirs = [read_window(scenedict, coordinates, 'B08') for scenedict in scenedicts]
