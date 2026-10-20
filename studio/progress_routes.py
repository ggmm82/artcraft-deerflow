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
