from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from .routes import bboxes#, #authentication

# initialize fastapi application
app = FastAPI(title="Geonos Satquery API", redoc_url="/")
app.mount("/static", StaticFiles(directory="app/static"), name="static") # mount logo file

# add routers
app.include_router(bboxes.router, prefix='/bboxes')
#app.include_router(authentication.router, prefix='/auth')

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