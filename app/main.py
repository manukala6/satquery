from celery import Celery
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from .routes import bboxes
from .routes.items import item_router
from .auth import jwt_authentication, satquery_users

# connect to db
load_dotenv()
#async def connect_to_mongo():
#    client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
#    db = client['satquery-dev-db']

# initialize fastapi application 
app = FastAPI(title="Geonos Satquery API", redoc_url="/")

# startup events
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.environ.get("MONGODB_DEV_URL"))
    app.mongodb = app.mongodb_client['satquery-dev-db']

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.add_event_handler("startup", startup_db_client) 
app.mount("/static", StaticFiles(directory="app/static"), name="static") # mount logo file

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add routers
app.include_router(
    bboxes.router, 
    prefix='/bboxes',
    tags=["Bbox API"]#,
    #dependencies=[Depends(get_db_connection)]
)
app.include_router(
    item_router(app), 
    prefix='/items',
    tags=["STAC Item API"]
)
app.include_router(
    satquery_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["Authentication API"]
)
app.include_router(
    satquery_users.get_register_router(),
    prefix="/auth",
    tags=["Authentication API"]
)
app.include_router(
    satquery_users.get_users_router(jwt_authentication),
    prefix="/users",
    tags=["User API"],
)

# OPENAPI configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Geonos Satquery API",
        version="0.1.0",
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/geonos_logo_draft.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi