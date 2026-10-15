"""Private, single-owner admin UI behind the deployment's HTTP authentication."""
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, SecretStr

from . import login
from .state import applications, catalog, update_agent, connection_status, available_skills, team, effective_agent

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
    return {'team': team(), 'effective_agents': {a['id']: effective_agent(a['id']) for a in applications()}, 'agents': catalog(), 'skills': available_skills(), 'applications': [
        {k: a[k] for k in ('id', 'name', 'role', 'description', 'version')}
        for a in applications()], 'connections': {
            engine: {'credentials_present': connection_status(engine)}
            for engine in ('codex', 'gemini', 'deepseek')}}


class AgentConfig(BaseModel):
    engine: str = Field(default='inherit', pattern='^(inherit|codex|gemini|deepseek)$')
    model: str = Field(default='', max_length=200)
    instructions: str = Field(default='', max_length=20000)
    enabled: bool = True
    skills: list[str] = Field(default_factory=list)


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


class TeamConfig(BaseModel):
    engine: str = Field(pattern='^(codex|deepseek|gemini)$')
    model: str = Field(default='', max_length=200)
    api_key: SecretStr | None = None


def validated_deepseek(key, model):
    from .deepseek import models
    if not key or len(key) > 512 or any(ord(c) < 33 for c in key):
        raise ValueError('Chiave DeepSeek non valida')
    available = models(key)
    chosen = model.strip() or next((m for m in ('deepseek-chat', 'deepseek-flash') if m in available), available[0] if available else '')
    if not chosen or chosen not in available:
        raise ValueError('Seleziona un modello DeepSeek disponibile')
    return chosen, available


@router.get('/api/team/models')
def team_models(engine: str = 'deepseek'):
    import json
    from .state import credential_dir
    from .deepseek import models
    if engine != 'deepseek':
        raise HTTPException(400, 'Elenco automatico disponibile per DeepSeek')
    path = credential_dir('deepseek') / 'api.json'
    if not path.is_file():
        raise HTTPException(400, 'Collega prima DeepSeek')
    try:
        available = models(json.loads(path.read_text())['api_key'])
    except ValueError as error:
        raise HTTPException(400, str(error)) from None
    except RuntimeError as error:
        raise HTTPException(502, str(error)) from None
    return {'models': available}


@router.put('/api/team')
def save_team(value: TeamConfig, request: Request):
    same_origin(request)
    import json
    from .state import credential_dir
    from .bootstrap import configure_team
    try:
        key = value.api_key.get_secret_value().strip() if value.api_key else None
        available = []
        chosen = value.model.strip()
        if value.engine == 'deepseek':
            if not key:
                path = credential_dir('deepseek') / 'api.json'
                if not path.is_file():
                    raise ValueError('Inserisci la chiave DeepSeek per attivare la squadra')
                key = json.loads(path.read_text())['api_key']
            chosen, available = validated_deepseek(key, chosen)
        elif not connection_status(value.engine):
            raise ValueError('Collega prima il tuo account ' + ('Gemini' if value.engine == 'gemini' else 'Codex'))
        else:
            chosen = chosen or ('gemini-2.5-pro' if value.engine == 'gemini' else 'gpt-5.4')
        configure_team(value.engine, chosen, key if value.engine == 'deepseek' else None)
    except ValueError as error:
        raise HTTPException(400, str(error)) from None
    except RuntimeError as error:
        raise HTTPException(502, str(error)) from None
    return {'ok': True, 'team': team(), 'models': available}


class CoordinatorConfig(BaseModel):
    model: str = Field(min_length=1, max_length=200)


@router.put('/api/coordinator', deprecated=True)
def set_coordinator(value: CoordinatorConfig, request: Request):
    # Compatibility endpoint: no independent coordinator setting remains.
    result = save_team(TeamConfig(engine=team()['engine'], model=value.model), request)
    return {**result, 'model': result['team']['model']}


class DeepSeekConfig(BaseModel):
    api_key: SecretStr
    model: str = Field(default='', max_length=200)


@router.put('/api/providers/deepseek')
def connect_deepseek(value: DeepSeekConfig, request: Request):
    same_origin(request)
    result = save_team(TeamConfig(engine='deepseek', model=value.model, api_key=value.api_key), request)
    return {'ok': True, 'model': result['team']['model'], 'models': result['models']}
