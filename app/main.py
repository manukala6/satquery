import os
from typing import Optional, Set
from motor import motor_asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from .routes import bboxes

load_dotenv()

# connect to db
client = motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
db = client['query-ts-1']

# initialize fastapi application
app = FastAPI()

app.include_router(bboxes.router, prefix='/bboxes')