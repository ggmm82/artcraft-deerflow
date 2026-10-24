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


async def production_running(request, thread_id):
    from app.gateway.deps import get_run_manager
    records = await get_run_manager(request).list_by_thread(str(thread_id),user_id=get_effective_user_id())
    return any(getattr(r.status,'value',r.status) in ('pending','running') for r in records)


@router.get('/api/threads/{thread_id}/studio-guide')
@require_permission('threads', 'read', owner_check=True, require_existing=True)
async def project_guide(thread_id: ThreadId, request: Request, response: Response,
                        delivery_id: str | None = None, format: str = 'json'):
    from .project_guide import build, markdown, bundle
    from starlette.responses import StreamingResponse
    from starlette.background import BackgroundTask
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    if format not in ('json', 'markdown', 'zip') or delivery_id is not None and len(delivery_id) > 100:
        raise HTTPException(422, 'Formato o consegna non validi')
    try:
        guide = await run_in_threadpool(build, workspace, delivery_id)
        if format == 'json':
            return guide
        if format == 'markdown':
            return Response(markdown(guide), media_type='text/markdown', headers={
                'Cache-Control': 'no-store', 'Content-Disposition': 'attachment; filename="GUIDA-PROGETTO.md"'})
        stream = await run_in_threadpool(bundle, workspace, guide)
        def chunks():
            try:
                while data := stream.read(1024 * 1024):
                    yield data
            finally:
                stream.close()
        return StreamingResponse(chunks(), media_type='application/zip', background=BackgroundTask(stream.close), headers={
            'Cache-Control': 'no-store', 'Content-Disposition': 'attachment; filename="Consegna-con-guida.zip"'})
    except (ValueError, OSError) as error:
        detail = str(error)[:200] if isinstance(error, ValueError) else 'File non disponibili: aggiorna il progetto'
        raise HTTPException(409, 'Guida o pacchetto non disponibili: ' + detail) from error


def audited(workspace, operation, value):
    from .audit_log import append
    append(workspace, 'Utente', operation, 'completed')
    return value


@router.get('/api/threads/{thread_id}/studio-audit')
@require_permission('threads', 'read', owner_check=True, require_existing=True)
async def conversation_audit(thread_id: ThreadId, request: Request, response: Response,
                             after: int | None = None, before: int | None = None, export: bool = False):
    from .audit_log import page, export_rows
    from starlette.responses import StreamingResponse
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    try:
        if export:
            return StreamingResponse(export_rows(workspace), media_type='text/csv', headers={
                'Cache-Control':'no-store', 'Content-Disposition':'attachment; filename="registro-conversazione.csv"'})
        return await run_in_threadpool(page, workspace, after, before)
    except (ValueError,OSError) as error:
        raise HTTPException(409, 'Registro non disponibile') from error


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
        return audited(workspace, 'Pausa richiesta' if body.paused else 'Ripresa richiesta',
                       {'user_control': await run_in_threadpool(set_user_control, workspace, body.paused)})
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@router.put('/api/threads/{thread_id}/studio-direction')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def project_direction(thread_id: ThreadId, body: ProjectDirection, request: Request, response: Response):
    from .projects import set_user_direction
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    response.headers['Cache-Control'] = 'no-store'
    try:
        return audited(workspace, 'Indicazioni aggiornate', await run_in_threadpool(set_user_direction, workspace, body.visual_approach, body.instructions))
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
        return audited(workspace, 'Consegna accettata', {'project': await run_in_threadpool(accept_delivery, workspace, body.delivery_id)})
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
    return await run_in_threadpool(summary, experience_root(), export,source_thread=str(thread_id))


@router.post('/api/threads/{thread_id}/studio-experience/curate')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def experience_curate(thread_id: ThreadId, request: Request, response: Response):
    from .lesson_curation import curate
    from .experience import summary
    from .lessons import pending
    from .docker_runtime import EXECUTION_LOCK
    root=experience_root()
    workspace=get_paths().sandbox_user_data_dir(thread_id,user_id=get_effective_user_id())
    from .experience import collect
    try:
        await run_in_threadpool(collect,workspace,root,str(thread_id))
    except (ValueError,OSError) as error:
        raise HTTPException(409,'Fonti non disponibili: la produzione non è stata modificata.') from error
    # Never submit a competing human turn or cancel a run. No sources means
    # no provider request, even when another project is using the worker.
    sources=await run_in_threadpool(pending,root,limit=3,source_thread=str(thread_id),meaningful_only=True)
    if sources and (await production_running(request,thread_id) or EXECUTION_LOCK.locked()):
        raise HTTPException(409,'Produzione in corso: la valutazione non è stata avviata. Il lavoro continua; riprova al termine.')
    response.headers['Cache-Control']='no-store'
    try:
        outcome=await run_in_threadpool(curate,workspace,root,str(thread_id))
        data=await run_in_threadpool(summary,root,source_thread=str(thread_id))
        return audited(workspace,'Lezioni valutate senza modificare il turno di produzione',{**data,'curation':outcome})
    except (ValueError,OSError) as error:
        raise HTTPException(409,'Valutazione non completata: '+str(error)[:250]) from error
    except Exception as error:
        raise HTTPException(503,'Modello di valutazione non disponibile. Il progetto e le osservazioni sono conservati.') from error


@router.post('/api/threads/{thread_id}/studio-experience/collect')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def experience_collect(thread_id: ThreadId, request: Request, response: Response):
    from .experience import collect, summary
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    try:
        await run_in_threadpool(collect, workspace, experience_root(), str(thread_id))
        from .lessons import propose_findings
        await run_in_threadpool(propose_findings, experience_root(), str(thread_id))
        return audited(workspace, 'Recupero esperienza richiesto', await run_in_threadpool(summary, experience_root(),source_thread=str(thread_id)))
    except (OSError, ValueError) as error:
        raise HTTPException(409, 'Recupero esperienza non completato') from error


@router.put('/api/threads/{thread_id}/studio-experience')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def experience_select(thread_id: ThreadId, body: ExperienceSelection, request: Request, response: Response):
    from .experience import exclude, summary
    try:
        await run_in_threadpool(exclude, experience_root(), body.id, body.excluded)
        return await run_in_threadpool(summary, experience_root(),source_thread=str(thread_id))
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
        workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
        audited(workspace, 'Lezione accettata' if body.accepted else 'Accettazione lezione revocata', None)
        return await run_in_threadpool(summary, experience_root(),source_thread=str(thread_id))
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
        return await run_in_threadpool(summary, experience_root(),source_thread=str(thread_id))
    except (OSError, ValueError) as error:
        raise HTTPException(409, 'Metodo non conservato: verifica lavorazione, file e descrizione') from error


@router.post('/api/threads/{thread_id}/studio-jobs/{job_id}/stop')
@require_permission('threads', 'write', owner_check=True, require_existing=True)
async def stop_job(thread_id: ThreadId, job_id: str, request: Request, response: Response):
    from .docker_runtime import request_stop
    import subprocess
    workspace = get_paths().sandbox_user_data_dir(thread_id, user_id=get_effective_user_id())
    try:
        return audited(workspace, 'Arresto sandbox richiesto', await run_in_threadpool(request_stop, workspace, job_id))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise HTTPException(409, 'Arresto non confermato: aggiorna lo stato della fase prima di riprovare') from error
