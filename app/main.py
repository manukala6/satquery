import os
from typing import Optional, Set

from fastapi import FastAPI
from pydantic import BaseModel

from .routes import bboxes

# initialize fastapi application
app = FastAPI()

app.include_router(bboxes.router, prefix='/bboxes')