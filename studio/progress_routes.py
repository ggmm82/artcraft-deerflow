"""Conversation-owned progress, separate from administrator configuration."""
from fastapi import APIRouter, Request, Response
from starlette.concurrency import run_in_threadpool
from app.gateway.authz import require_permission
from deerflow.config.paths import get_paths
from deerflow.runtime.user_context import get_effective_user_id
from deerflow.utils.thread_id import ThreadId

from .progress import list_jobs
from .projects import read_project

router = APIRouter()


@router.get('/api/threads/{thread_id}/studio-jobs')
@require_permission('threads', 'read', owner_check=True, require_existing=True)
async def job_progress(thread_id: ThreadId, request: Request, response: Response):
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    return {'jobs': await run_in_threadpool(list_jobs, workspace),
            'project': await run_in_threadpool(read_project, workspace)}
