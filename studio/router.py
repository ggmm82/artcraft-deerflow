"""Private, single-owner admin UI behind the deployment's HTTP authentication."""
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import login
from .state import applications, catalog, update_agent, connection_status, available_skills

router = APIRouter(prefix='/studio', tags=['ArtCraft Studio'])


def same_origin(request):
    if request.headers.get('sec-fetch-site') == 'cross-site':
        raise HTTPException(403, 'Richiesta da un altro sito')
    origin = request.headers.get('origin')
    if origin and urlsplit(origin).netloc != request.headers.get('host'):
        raise HTTPException(403, 'Origine non consentita')


@router.get('')
@router.get('/')
def page():
    return FileResponse(Path(__file__).parent / 'index.html')


@router.get('/api/catalog')
def get_catalog():
    return {'agents': catalog(), 'skills': available_skills(), 'applications': [
        {k: a[k] for k in ('id', 'name', 'role', 'description', 'version')}
        for a in applications()], 'connections': {
            engine: {'credentials_present': connection_status(engine)}
            for engine in ('codex', 'gemini')}}


class AgentConfig(BaseModel):
    engine: str = Field(pattern='^(codex|gemini)$')
    model: str = Field(default='', max_length=200)
    instructions: str = Field(default='', max_length=20000)
    enabled: bool = True
    skills: list[str] = Field(default_factory=list, max_length=14)


@router.put('/api/agents/{identifier}')
def save_agent(identifier: str, value: AgentConfig, request: Request):
    same_origin(request)
    try:
        return update_agent(identifier, value.model_dump())
    except ValueError as error:
        raise HTTPException(400, str(error)) from None


@router.post('/api/login/{engine}')
def begin_login(engine: str, request: Request):
    same_origin(request)
    if engine not in ('codex', 'gemini'):
        raise HTTPException(400, 'Motore sconosciuto')
    try:
        return login.start(engine)
    except (RuntimeError, OSError, ValueError) as error:
        raise HTTPException(409, str(error)) from None


@router.get('/api/login-session/{identifier}')
def read_login(identifier: str):
    session = login.SESSIONS.get(identifier)
    if not session:
        raise HTTPException(404, 'Sessione non trovata')
    return session.public()


class LoginInput(BaseModel):
    text: str = Field(max_length=4096)


@router.post('/api/login-session/{identifier}/input')
def login_input(identifier: str, value: LoginInput, request: Request):
    same_origin(request)
    session = login.SESSIONS.get(identifier)
    if not session:
        raise HTTPException(404, 'Sessione non trovata')
    try:
        session.write(value.text)
    except (ValueError, OSError) as error:
        raise HTTPException(409, str(error)) from None
    return {'ok': True}


@router.delete('/api/login-session/{identifier}')
def cancel_login(identifier: str, request: Request):
    same_origin(request)
    session = login.SESSIONS.get(identifier)
    if session:
        session.cancel()
    return {'ok': True}


class CoordinatorConfig(BaseModel):
    model: str = Field(min_length=1, max_length=200)


@router.put('/api/coordinator')
def set_coordinator(value: CoordinatorConfig, request: Request):
    same_origin(request)
    if any(ord(c) < 32 for c in value.model):
        raise HTTPException(400, 'Modello non valido')
    from .bootstrap import configure_coordinator
    configure_coordinator(value.model)
    return {'ok': True, 'model': value.model}
