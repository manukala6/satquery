from enum import Enum

class AssetType(str, Enum):
    """
    AssetType enum
    """
    analytic = "analytic"
    thumbnail = "thumbnail"
    video = "video"

class SatelliteCollectionType(str, Enum):
    """
    SatelliteCollectionType enum
    """
    sentinel2 = "sentinel2"
    landsat8 = "landsat8"