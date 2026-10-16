"""Adaptive production workspace: activities, usable versions and recoverable work.

This records operational decisions and file handoffs, never model reasoning.
The worker remains disposable; retries use saved files in a new output folder.
"""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import uuid

from .progress import JOB_ID, clean_summary, job_path, read_status, update, utcnow, workspace_key
from .work_results import failure_info, partial_files
from .state import applications, atomic_json

STEP_ID = re.compile(r'[a-z][a-z0-9_-]{0,47}\Z')
PROJECT_ID = re.compile(r'[0-9a-f]{32}\Z')
MAX_HISTORY = 20
GATEWAY_SESSION = uuid.uuid4().hex


@contextmanager
def locked(workspace):
    root = Path(workspace).resolve()
    folder = root / '.studio-project'
    if folder.is_symlink() or not folder.resolve().is_relative_to(root):
        raise ValueError('Percorso progetto non valido')
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(folder / 'project.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield folder
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def load(folder, workspace):
    path = folder / 'project.json'
    if not path.exists():
        return None
    if path.is_symlink() or path.stat().st_size > 1000000:
        raise ValueError('Stato progetto non valido')
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or not isinstance(value.get('id'), str) or not PROJECT_ID.fullmatch(value['id']):
        raise ValueError('Identificatore progetto non valido')
    steps = value.get('steps')
    if not isinstance(steps, list) or not 0 <= len(steps) <= 64:
        raise ValueError('Fasi del progetto non valide')
    for step in steps:
        if (not isinstance(step, dict) or not isinstance(step.get('id'), str)
                or not STEP_ID.fullmatch(step['id']) or not isinstance(step.get('agent'), str)
                or not isinstance(step.get('goal'), str) or not isinstance(step.get('depends_on'), list)
                or not isinstance(step.get('attempts'), list) or len(step['attempts']) > 100
                or any(not isinstance(a, dict) for a in step['attempts'])
                or step.get('status') not in ('pending', 'running', 'completed', 'needs_revision', 'review', 'paused', 'skipped')
                or (step['status'] in ('running', 'completed') and not step['attempts'])):
            raise ValueError('Stato della fase non valido')
    if value.get('workspace_key') != workspace_key(workspace):
        return None
    changed = False
    if value.get('project_type') == 'animated_video' and 'requirements' not in value:
        value['requirements'] = {'video': True, 'audio': not bool(value.get('omissions', {}).get('soundcraft'))}
        changed = True
    for step in steps:
        if step['status'] == 'running' and step['attempts'][-1].get('gateway_session') != GATEWAY_SESSION:
            step['status'] = 'paused'
            step['attempts'][-1].update(status='paused', finished_at=utcnow(),
                error='Gateway riavviato: ispeziona i file persistenti e riprendi questa fase')
            job_id = Path(step['attempts'][-1].get('output_dir', '')).name
            if JOB_ID.fullmatch(job_id):
                try:
                    progress = job_path(workspace, job_id)
                    saved = read_status(progress)
                    if saved.get('workspace_key') == workspace_key(workspace) and saved['phase'] not in ('completed', 'failed', 'timed_out'):
                        update(progress, 'failed', 'Incarico fermato dal riavvio; i file salvati sono recuperabili')
                except (OSError, ValueError):
                    pass
            changed = True
    if changed:
        value['updated_at'] = utcnow()
        atomic_json(path, value)
    return value


def artifact_path(workspace, filename):
    root = Path(workspace).resolve()
    path = Path(str(filename))
    if path.is_relative_to('/mnt/user-data'):
        path = root / path.relative_to('/mnt/user-data')
    if not path.is_absolute() or not path.resolve().is_relative_to(root):
        return None
    if not path.is_file() or path.is_symlink() or not path.stat().st_size:
        return None
    return path


def public_artifact(workspace, filename):
    path = artifact_path(workspace, filename)
    return '/mnt/user-data/' + path.relative_to(Path(workspace).resolve()).as_posix() if path else None


def available_paths(workspace, attempt):
    paths = attempt.get('output_files', [])
    if paths or not workspace or not attempt.get('output_dir'):
        return paths
    root = Path(workspace).resolve()
    folder = Path(attempt['output_dir'])
    if folder.is_relative_to('/mnt/user-data'):
        folder = root / folder.relative_to('/mnt/user-data')
    if not folder.is_absolute() or not folder.resolve().is_relative_to(root):
        return []
    return partial_files(folder)


def read_project(workspace):
    """Compact operational memory: histories remain on disk, not in every LLM turn."""
    if not (Path(workspace) / '.studio-project').exists():
        return None
    with locked(workspace) as folder:
        value = load(folder, workspace)
    if not value:
        return None
    result = {k: clean_summary(value.get(k, '')) for k in (
        'id', 'brief', 'summary', 'next_action', 'status', 'updated_at', 'product_path')}
    result['project_type'] = value.get('project_type', 'custom')
    result['requirements'] = {k: v for k, v in value.get('requirements', {}).items()
                              if k in ('audio', 'video') and type(v) is bool}
    result['product_path'] = public_artifact(workspace, value.get('product_path', '')) or ''
    result['steps'], result['results'], candidates = [], [], []
    for step in value['steps']:
        attempts = step['attempts']
        last = attempts[-1] if attempts else {}
        result['steps'].append({'id': step['id'], 'agent': step['agent'], 'goal': clean_summary(step['goal']),
            'status': step['status'], 'attempt_count': step.get('attempt_count', len(attempts)),
            'note': clean_summary(step.get('note', '')), 'error': clean_summary(last.get('error', ''))})
        # Retain previous usable versions when a newer revision failed or hit quota.
        for attempt in reversed(attempts):
            for filename in (available_paths(workspace, attempt) + attempt.get('previews', []))[:40]:
                candidates.append({'path': filename, 'agent': step['agent'], 'activity': step['id'],
                        'label': clean_summary(Path(filename).name), 'validated': attempt.get('validated',
                        attempt.get('status') == 'completed'), 'at': attempt.get('finished_at', '')})
            if attempt.get('status') == 'completed':
                break
    candidates.sort(key=lambda r: (r['path'] == value.get('product_path'), r['at']), reverse=True)
    seen = set()
    for record in candidates:
        path = public_artifact(workspace, record['path'])
        if path and path not in seen:
            seen.add(path)
            result['results'].append({**record, 'path': path})
        if len(result['results']) >= 60:
            break
    attention = value.get('attention')
    result['attention'] = {k: clean_summary(attention.get(k)) for k in ('code', 'message', 'action')} if isinstance(attention, dict) else None
    if not result['attention'] and value.get('schema_version') != 2:
        # Existing projects migrate without erasing recoverable output or demanding a new plan.
        failed = [s for s in value['steps'] if s['status'] in ('needs_revision', 'paused') and s['attempts']]
        if failed:
            latest = max(failed, key=lambda s: s['attempts'][-1].get('finished_at', ''))
            error = latest['attempts'][-1].get('error')
            if error:
                result['attention'] = failure_info(error)
    if not result['status']:
        result['status'] = 'working' if any(s['status'] == 'running' for s in value['steps']) else 'review'
    return result


def create_plan(workspace, brief, steps, project_type='', omissions=None, *, summary='', next_action='',
                status='', product_path='', requirements=None):
    """Update an evolving brief and activity board, preserving work and versions."""
    if project_type not in ('', 'custom', 'animated_video'):
        raise ValueError('Tipo di progetto non valido')
    if not isinstance(steps, list) or len(steps) > 64:
        raise ValueError('Usa al massimo 64 attività')
    if status not in ('', 'working', 'review', 'ready', 'blocked', 'idle'):
        raise ValueError('Stato progetto non valido')
    if requirements is not None and (not isinstance(requirements, dict) or any(
            k not in ('audio', 'video') or type(v) is not bool for k, v in requirements.items())):
        raise ValueError('I requisiti media accettano audio e video come booleani')
    known, incoming = {a['id'] for a in applications()}, []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError('Attività non valida')
        sid, agent, goal = step.get('id', ''), step.get('agent'), step.get('goal', '')
        if not isinstance(sid, str) or not STEP_ID.fullmatch(sid) or sid in {s['id'] for s in incoming}:
            raise ValueError('ID attività non valido o duplicato')
        if agent not in known or not isinstance(goal, str) or not goal.strip() or len(goal) > 4000:
            raise ValueError('Ogni attività richiede uno specialista del catalogo e un obiettivo concreto')
        deps = step.get('depends_on', [])
        if not isinstance(deps, list) or any(not isinstance(d, str) or not STEP_ID.fullmatch(d) for d in deps):
            raise ValueError('Riferimenti degli input non validi')
        if step.get('status', 'pending') not in ('pending', 'skipped', 'review'):
            raise ValueError('Le attività aggiornabili possono essere pending, skipped o review')
        incoming.append({**step, 'depends_on': deps})
    with locked(workspace) as folder:
        value = load(folder, workspace)
        if not value:
            if not brief.strip():
                raise ValueError('Specifica il risultato richiesto')
            value = {'id': uuid.uuid4().hex, 'workspace_key': workspace_key(workspace),
                'brief': clean_summary(brief), 'project_type': project_type or 'custom',
                'created_at': utcnow(), 'steps': [], 'requirements': {}}
        if brief:
            value['brief'] = clean_summary(brief)
        if project_type:
            value['project_type'] = project_type
        if value['project_type'] == 'animated_video' and not value.get('requirements'):
            value['requirements'] = {'video': True, 'audio': not bool((omissions or {}).get('soundcraft'))}
        if requirements is not None:
            value['requirements'] = requirements
        for item in incoming:
            previous = next((s for s in value['steps'] if s['id'] == item['id']), None)
            if previous:
                if previous['status'] == 'running':
                    raise ValueError('Non modificare un’attività in esecuzione')
                previous.update(agent=item['agent'], goal=item['goal'], depends_on=item['depends_on'])
                if 'status' in item:
                    previous['status'] = item['status']
            else:
                value['steps'].append({**item, 'status': item.get('status', 'pending'), 'attempts': []})
        if len(value['steps']) > 64:
            raise ValueError('Il progetto ha raggiunto 64 attività; archivia quelle concluse prima di un nuovo progetto')
        for key, text in [('summary', summary), ('next_action', next_action)]:
            if text:
                value[key] = clean_summary(text)
        if product_path:
            path = artifact_path(workspace, product_path)
            produced = [p for s in value['steps'] for a in s['attempts']
                        if a.get('validated', a.get('status') == 'completed') for p in a.get('output_files', [])]
            if not path or not any(artifact_path(workspace, p) == path for p in produced):
                raise ValueError('Il prodotto deve essere un file realmente prodotto e verificato da uno specialista')
            if value.get('requirements') and not any(product_path in a.get('verified_products', [])
                    for s in value['steps'] for a in s['attempts']):
                raise ValueError('Prima della consegna finale usa studio_delegate con purpose=delivery per controllare il file completo')
            value['product_path'] = product_path
        if status == 'ready' and not value.get('product_path'):
            raise ValueError('Indica il prodotto finale verificato, non un elenco di file intermedi')
        if status:
            value['status'] = status
            if status == 'ready':
                value['attention'] = None
        value.update(schema_version=2, updated_at=utcnow())
        atomic_json(folder / 'project.json', value)
    return read_project(workspace)


def revise_step(workspace, step_id, reason):
    if not reason.strip():
        raise ValueError('Specifica il problema da correggere')
    with locked(workspace) as folder:
        value = load(folder, workspace)
        step = next((s for s in (value or {}).get('steps', []) if s['id'] == step_id), None)
        if not step or step['status'] == 'running':
            raise ValueError('Attività non disponibile per la revisione')
        # A new creative revision is not a lifetime retry and does not invalidate the team.
        step.update(status='pending', revision=clean_summary(reason), revision_id=uuid.uuid4().hex)
        value.update(status='review', next_action=clean_summary(reason), updated_at=utcnow())
        atomic_json(folder / 'project.json', value)
    return read_project(workspace)


def archive_plan(workspace, reason):
    if not reason.strip():
        raise ValueError('Specifica il motivo dell’archiviazione')
    with locked(workspace) as folder:
        value = load(folder, workspace)
        if not value:
            return None
        if any(s['status'] == 'running' for s in value['steps']):
            raise ValueError('Attendi il termine dell’incarico attivo')
        value.update(archived_at=utcnow(), archive_reason=clean_summary(reason))
        atomic_json(folder / (value['id'] + '.json'), value)
        (folder / 'project.json').unlink()
    return {'id': value['id'], 'archived': True, 'files_preserved': True}


def execute_step(workspace, agent, task, step_id, invoke, *, provider=None, purpose='work', request_id=''):
    if purpose not in ('work', 'preview', 'review', 'integration', 'delivery'):
        raise ValueError('Scopo incarico non valido')
    if not read_project(workspace):
        create_plan(workspace, clean_summary(task), [])
    with locked(workspace) as folder:
        value = load(folder, workspace)
        step = next((s for s in value['steps'] if s['id'] == step_id), None) if step_id else None
        if not step:
            sid = step_id or agent + '-' + uuid.uuid4().hex[:8]
            if not STEP_ID.fullmatch(sid) or agent not in {a['id'] for a in applications()} or len(value['steps']) >= 64:
                raise ValueError('Attività o specialista non valido')
            step = {'id': sid, 'agent': agent, 'goal': clean_summary(task), 'depends_on': [], 'attempts': [], 'status': 'pending'}
            value['steps'].append(step)
        if step['status'] == 'running':
            raise ValueError('Questa attività è già in esecuzione')
        step.update(agent=agent, purpose=purpose)
        previous = step['attempts'][-1] if step['attempts'] else {}
        context = {'provider': provider, 'revision': step.get('revision_id', ''), 'purpose': purpose, 'request': request_id}
        if previous.get('context') == context and previous.get('error'):
            failure = failure_info(previous['error'])
            if not failure['retryable']:
                return json.dumps({'ok': False, 'attention': failure, 'available_results': read_results(value, workspace),
                    'error': failure['message'], 'retry_blocked': True}, ensure_ascii=False)
            recent = step['attempts'][-2:]
            if len(recent) == 2 and all(a.get('context') == context and a.get('error') == previous['error']
                    and not a.get('output_files') for a in recent):
                return json.dumps({'ok': False, 'error': 'Due tentativi identici senza risultati: cambia approccio, '
                    'riduci l’incarico o integra i file recuperati. Le altre attività restano disponibili.',
                    'retry_blocked': True, 'available_results': read_results(value, workspace)}, ensure_ascii=False)
        sources = read_results(value, workspace)
        contract = ('\n\nObiettivo del prodotto: ' + value['brief'] + '\nAttività: ' + step['goal'] +
                    '\nRisultati disponibili dei colleghi (anche provvisori):\n' + json.dumps(sources, ensure_ascii=False) +
                    '\nScegli e ispeziona gli input pertinenti. Riusa quanto valido; segnala i limiti senza '
                    'rifare tutto per un controllo facoltativo o una chiusura formale mancante.')
        if previous:
            contract += '\nUltimo incarico da riprendere: ' + json.dumps({k: previous.get(k) for k in
                ('output_dir', 'output_files', 'error')}, ensure_ascii=False)
        attempt = {'started_at': utcnow(), 'status': 'running', 'gateway_session': GATEWAY_SESSION, 'context': context}
        history = step['attempts'][-(MAX_HISTORY - 2):]
        last_usable = next((a for a in reversed(step['attempts']) if a.get('status') == 'completed'), None)
        if last_usable and last_usable not in history:
            history.insert(0, last_usable)
        step['attempts'] = [*history, attempt]
        step['attempt_count'] = step.get('attempt_count', len(step['attempts']) - 1) + 1
        step['status'] = 'running'
        value.update(schema_version=2, status='working', summary=clean_summary(step['goal']), attention=None, updated_at=utcnow())
        atomic_json(folder / 'project.json', value)
        project_id, sid = value['id'], step['id']

    def started(output_dir):
        with locked(workspace) as folder:
            current = load(folder, workspace)
            next(s for s in current['steps'] if s['id'] == sid)['attempts'][-1]['output_dir'] = output_dir
            atomic_json(folder / 'project.json', current)

    try:
        result = json.loads(invoke(task + contract, started))
        if not isinstance(result, dict):
            raise ValueError('Risposta dello specialista non valida')
    except Exception as exc:
        result = {'ok': False, 'error': clean_summary(exc)}
    handoff = result.get('handoff') or {}
    notes = [clean_summary(c.get('name')) for c in handoff.get('checks', []) if c.get('status') != 'passed']
    with locked(workspace) as folder:
        value = load(folder, workspace)
        if value['id'] != project_id:
            raise RuntimeError('Progetto cambiato durante l’incarico')
        step = next(s for s in value['steps'] if s['id'] == sid)
        attempt = step['attempts'][-1]
        step['status'] = 'completed' if result.get('ok') else 'paused'
        attempt.update(status=step['status'], finished_at=utcnow(), validated=bool(result.get('ok')),
            product_verified=bool(result.get('product_verified')),
            verified_products=result.get('verified_products', [])[:10],
            output_dir=result.get('output_dir') or attempt.get('output_dir', ''),
            output_files=(handoff.get('output_files') or result.get('available_files') or [])[:40],
            previews=handoff.get('previews', [])[:8], error=clean_summary(result.get('error', '')))
        step['note'] = clean_summary('Controlli da valutare: ' + ', '.join(notes)) if notes else ''
        attention = failure_info(attempt['error']) if attempt['error'] else None
        value.update(status='review' if result.get('ok') else 'blocked', attention=attention,
            summary='Risultati disponibili: posso integrarli e migliorare la versione.' if result.get('ok') else attention['message'],
            next_action='Prepara o aggiorna una versione completa del prodotto usando i risultati disponibili.'
                if result.get('ok') else attention['action'], updated_at=utcnow())
        atomic_json(folder / 'project.json', value)
    result.update(activity={'id': sid, 'status': step['status']}, review_notes=notes)
    if attention:
        result['attention'] = attention
    return json.dumps(result, ensure_ascii=False)


def read_results(value, workspace=None):
    """A bounded catalog of actual handoffs and partial work, not all attempt logs."""
    results = []
    for step in value['steps']:
        seen = set()
        for attempt in reversed(step['attempts']):
            paths = [p for p in available_paths(workspace, attempt) if p not in seen][:12]
            if paths or attempt.get('output_dir'):
                results.append({'activity': step['id'], 'agent': step['agent'], 'validated': attempt.get('validated',
                    attempt.get('status') == 'completed'), 'output_dir': attempt.get('output_dir'), 'files': paths,
                    'at': attempt.get('finished_at', '')})
            seen.update(paths)
            if attempt.get('status') == 'completed':
                break
    return sorted(results, key=lambda r: r['at'], reverse=True)[:20]
