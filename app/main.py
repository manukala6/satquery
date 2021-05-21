import os
from typing import Optional, Set

from fastapi import FastAPI
from pydantic import BaseModel
import motor.motor_asyncio

from .routes import bboxes

# initialize fastapi application
app = FastAPI()

# connect to mongodb database
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.college

app.include_router(bboxes.router, prefix='/bboxes')