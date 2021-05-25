import rasterio as rio
from rasterio.session import AWSSession
from rio_tiler.io import COGReader

def parse_sentinel2(sceneid):
    return {
        'utm': sceneid[4:6],
        'lat': sceneid[6],
        'sq': sceneid[7:9],
        'year': sceneid[10:14],
        'month': sceneid[14:16].strip('0'),
        'day': sceneid[14:16].strip('0'),
        'sceneid': sceneid
    }

def read_window(scene_dict, bounds, band, boto3_session):
    s3_uri = 's3://sentinel-cogs/sentinel-s2-l2a-cogs/{utm}/{lat}/{sq}/{year}/{month}/{sceneid}/'
    s3_uri = s3_uri.format(**scene_dict)

    with rio.Env(AWSSession(boto3_session)):
        with COGReader(f'{s3_uri}{band}.tif')as cog:
            img: ImageData = cog.part(bounds, max_size=100)

    return img.data[0, 2:]