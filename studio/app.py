"""Add the Studio routes to the pinned, otherwise unchanged DeerFlow Gateway."""
from app.gateway.app import app
from .router import router

app.include_router(router)
