from fastapi import FastAPI

from src.errors import register_error_handlers
from src.middleware import register_middleware
from src.models.model_auth import User
from src.models.model_url import URL
from src.routes.route_auth import auth_router
from src.routes.route_url import url_router

version = "v1"

app = FastAPI(
    title="Uptime Guard",
    description="A REST API for book review",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redocs",
    contact={"email": "dorjizangpo75@gmail.com"},
)

register_error_handlers(app)
register_middleware(app)

app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
app.include_router(url_router, prefix=f"/api/{version}/url", tags=["url"])
