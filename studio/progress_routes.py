"""Conversation-owned progress, separate from administrator configuration."""
from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from app.gateway.authz import require_permission
from deerflow.config.paths import get_paths
from deerflow.runtime.user_context import get_effective_user_id
from deerflow.utils.thread_id import ThreadId

from .progress import list_jobs
from .projects import read_project, accept_delivery

router = APIRouter()


class ProjectDirection(BaseModel):
    visual_approach: str = Field(pattern='^(unspecified|generated|vector|mixed|automatic)$')
    instructions: str = Field(default='', max_length=2000)


class ProjectControl(BaseModel):
    paused: bool


@router.put('/api/threads/{thread_id}/studio-control')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def project_control(thread_id: ThreadId, body: ProjectControl, request: Request, response: Response):
    from .projects import set_user_control
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    try:
        return {'user_control': await run_in_threadpool(set_user_control, workspace, body.paused)}
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@router.put('/api/threads/{thread_id}/studio-direction')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def project_direction(thread_id: ThreadId, body: ProjectDirection, request: Request, response: Response):
    from .projects import set_user_direction
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    try:
        return await run_in_threadpool(set_user_direction, workspace, body.visual_approach, body.instructions)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@router.get('/api/threads/{thread_id}/studio-jobs')
@require_permission('threads', 'read', owner_check=True, require_existing=True)
async def job_progress(thread_id: ThreadId, request: Request, response: Response):
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    return {'jobs': await run_in_threadpool(list_jobs, workspace),
            'project': await run_in_threadpool(read_project, workspace)}


class DeliveryAcceptance(BaseModel):
    delivery_id: str = Field(min_length=1, max_length=100)


@router.post('/api/threads/{thread_id}/studio-delivery/accept')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def accept_version(thread_id: ThreadId, body: DeliveryAcceptance, request: Request, response: Response):
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    try:
        return {'project': await run_in_threadpool(accept_delivery, workspace, body.delivery_id)}
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


class ExperienceSelection(BaseModel):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    excluded: bool


def experience_root():
    return get_paths().user_dir(get_effective_user_id()) / 'artcraft-experience'


@router.get('/api/threads/{thread_id}/studio-experience')
@require_permission('threads', 'read', owner_check=True, require_existing=True)
async def experience_list(thread_id: ThreadId, request: Request, response: Response, export: bool = False):
    from .experience import summary
    response.headers['Cache-Control'] = 'no-store'
    return await run_in_threadpool(summary, experience_root(), export)


@router.post('/api/threads/{thread_id}/studio-experience/collect')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def experience_collect(thread_id: ThreadId, request: Request, response: Response):
    from .experience import collect, summary
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    try:
        await run_in_threadpool(collect, workspace, experience_root(), str(thread_id))
        return await run_in_threadpool(summary, experience_root())
    except (OSError, ValueError) as error:
        raise HTTPException(409, 'Recupero esperienza non completato') from error


@router.put('/api/threads/{thread_id}/studio-experience')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def experience_select(thread_id: ThreadId, body: ExperienceSelection, request: Request, response: Response):
    from .experience import exclude, summary
    try:
        await run_in_threadpool(exclude, experience_root(), body.id, body.excluded)
        return await run_in_threadpool(summary, experience_root())
    except (OSError, ValueError) as error:
        raise HTTPException(409, 'Esperienza non disponibile') from error


class LessonAcceptance(BaseModel):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    accepted: bool


@router.put('/api/threads/{thread_id}/studio-experience/lesson')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def lesson_accept(thread_id: ThreadId, body: LessonAcceptance, request: Request, response: Response):
    from .lessons import accept
    from .experience import summary
    response.headers['Cache-Control'] = 'no-store'
    try:
        await run_in_threadpool(accept, experience_root(), body.id, body.accepted)
        return await run_in_threadpool(summary, experience_root())
    except (OSError, ValueError) as error:
        raise HTTPException(409, 'Lezione non disponibile') from error


class PreferredMethod(BaseModel):
    delivery_id: str = Field(pattern='^artcraft-job-[a-f0-9]{12}$')
    note: str = Field(min_length=5, max_length=2000)


@router.post('/api/threads/{thread_id}/studio-experience/prefer')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def experience_prefer(thread_id: ThreadId, body: PreferredMethod, request: Request, response: Response):
    from .experience import prefer, summary
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    try:
        await run_in_threadpool(prefer, workspace, experience_root(), body.delivery_id, body.note, str(thread_id))
        return await run_in_threadpool(summary, experience_root())
    except (OSError, ValueError) as error:
        raise HTTPException(409, 'Metodo non conservato: verifica lavorazione, file e descrizione') from error


@router.post('/api/threads/{thread_id}/studio-jobs/{job_id}/stop')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def stop_job(thread_id: ThreadId, job_id: str, request: Request, response: Response):
    from .docker_runtime import request_stop
    import subprocess
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    try:
        return await run_in_threadpool(request_stop, workspace, job_id)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise HTTPException(409, 'Arresto non confermato: aggiorna lo stato della fase prima di riprovare') from error
