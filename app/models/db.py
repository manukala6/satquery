import os
from bson import ObjectId

# connect to mongodb atlas
async def connect_to_mongo():
    print("Connecting to MongoDB Atlas...")
    if not "MONGODB_ATLAS_URL" in os.environ:
        raise ValueError("MONGODB_ATLAS_URL environment variable not set")
        
    

# database validators
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")