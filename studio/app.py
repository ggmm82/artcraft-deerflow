"""Add the Studio routes to the pinned, otherwise unchanged DeerFlow Gateway."""
from app.gateway.app import app
from app.gateway.deps import require_admin_user
from fastapi import Depends, Request
from .router import router
from .team_routing import TeamRoutingMiddleware


async def studio_admin(request: Request):
    await require_admin_user(request, detail='La configurazione della squadra è riservata all’amministratore.')


app.include_router(router, dependencies=[Depends(studio_admin)])

app.add_middleware(TeamRoutingMiddleware)
