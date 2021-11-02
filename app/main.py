from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from .routes import items, bboxes
from .auth import jwt_authentication, satquery_users


# initialize fastapi application
app = FastAPI(title="Geonos Satquery API", redoc_url="/")
app.mount("/static", StaticFiles(directory="app/static"), name="static") # mount logo file

# add routers
app.include_router(
    bboxes.router, 
    prefix='/bboxes',
    tags=["Bbox API"]
)
app.include_router(
    items.router, 
    prefix='/items',
    tags=["Bbox API"]
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

# Add static files


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