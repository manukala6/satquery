import os
from typing import Optional, Set
from motor import motor_asyncio

from fastapi import FastAPI
from dotenv import load_dotenv

from .routes import bboxes#, #authentication

load_dotenv()

# connect to db
#client = motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
#db = client['query-ts-1']

# initialize fastapi application
app = FastAPI()

app.include_router(bboxes.router, prefix='/bboxes')
#app.include_router(authentication.router, prefix='/auth')