import os
from dotenv import load_dotenv

import motor.motor_asyncio
from fastapi import APIRouter
from fastapi_users.db import MongoDBUserDatabase
from fastapi_users.authentication import JWTAuthentication

from ..models.user import *

router = APIRouter()

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"), uuidRepresentation="standard")
db = client['satquery-dev-db']
collection = db['users']

user_db = MongoDBUserDatabase(UserDB, collection)