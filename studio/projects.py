"""Persistent, sequential teams with dependency and delivery gates.

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

from .progress import clean_summary, utcnow, workspace_key
from .state import applications, atomic_json

STEP_ID = re.compile(r'[a-z][a-z0-9_-]{0,47}\Z')
PROJECT_ID = re.compile(r'[0-9a-f]{32}\Z')
VIDEO_TEAM = {'photocraft', 'effectcraft', 'soundcraft', 'filmcraft'}
MAX_ATTEMPTS = 3
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
    if path.is_symlink() or path.stat().st_size > 300000:
        raise ValueError('Stato progetto non valido')
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or not isinstance(value.get('id'), str) or not PROJECT_ID.fullmatch(value['id']):
        raise ValueError('Identificatore progetto non valido')
    steps = value.get('steps')
    if not isinstance(steps, list) or not 1 <= len(steps) <= 16:
        raise ValueError('Fasi del progetto non valide')
    for step in steps:
        if (not isinstance(step, dict) or not isinstance(step.get('id'), str)
                or not STEP_ID.fullmatch(step['id']) or not isinstance(step.get('agent'), str)
                or not isinstance(step.get('goal'), str) or not isinstance(step.get('depends_on'), list)
                or not isinstance(step.get('attempts'), list) or len(step['attempts']) > MAX_ATTEMPTS
                or any(not isinstance(a, dict) for a in step['attempts'])
                or step.get('status') not in ('pending', 'running', 'completed', 'needs_revision')
                or (step['status'] in ('running', 'completed') and not step['attempts'])):
            raise ValueError('Stato della fase non valido')
    if value.get('workspace_key') != workspace_key(workspace):
        return None
    changed = False
    for step in steps:
        if step['status'] == 'running' and step['attempts'][-1].get('gateway_session') != GATEWAY_SESSION:
            step['status'] = 'needs_revision'
            step['attempts'][-1].update(status='needs_revision', finished_at=utcnow(),
                error='Gateway riavviato: ispeziona i file persistenti e riprendi questa fase')
            changed = True
    if changed:
        value['updated_at'] = utcnow()
        atomic_json(path, value)
    return value


def read_project(workspace):
    if not (Path(workspace) / '.studio-project').exists():
        return None
    with locked(workspace) as folder:
        value = load(folder, workspace)
    if value:
        value.pop('workspace_key', None)
        for step in value['steps']:
            step['goal'] = clean_summary(step['goal'])
            for attempt in step['attempts']:
                attempt.pop('gateway_session', None)
    return value


def create_plan(workspace, brief, steps, project_type='custom', omissions=None):
    """Only explicit user exclusions can remove a default video discipline."""
    if project_type not in ('custom', 'animated_video'):
        raise ValueError('project_type: custom oppure animated_video')
    if not isinstance(brief, str) or not brief.strip() or len(brief) > 4000:
        raise ValueError('Brief obbligatorio, massimo 4000 caratteri')
    if not isinstance(steps, list) or not 1 <= len(steps) <= 16:
        raise ValueError('Il piano richiede da 1 a 16 fasi')
    omissions = omissions or {}
    if not isinstance(omissions, dict) or any(k not in VIDEO_TEAM or not isinstance(v, str)
            or not v.strip() or len(v) > 500 for k, v in omissions.items()):
        raise ValueError('Le omissioni richiedono specialista e requisito esplicito dell’utente')
    known = {a['id'] for a in applications()}
    seen, ancestors, normalized = set(), {}, []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError('Fase non valida')
        sid, agent, goal = step.get('id', ''), step.get('agent'), step.get('goal')
        deps = step.get('depends_on', [])
        if not isinstance(sid, str) or not STEP_ID.fullmatch(sid) or sid in seen:
            raise ValueError('ID fase non valido o duplicato')
        if agent not in known or not isinstance(goal, str) or not goal.strip() or len(goal) > 4000:
            raise ValueError('Ogni fase richiede uno specialista del catalogo e un obiettivo verificabile')
        if not isinstance(deps, list) or any(not isinstance(d, str) or d not in seen for d in deps):
            raise ValueError('Le dipendenze devono riferirsi a fasi precedenti')
        ancestors[sid] = set(deps)
        for dep in deps:
            ancestors[sid].update(ancestors[dep])
        seen.add(sid)
        normalized.append({'id': sid, 'agent': agent, 'goal': goal,
                           'depends_on': list(dict.fromkeys(deps)), 'status': 'pending', 'attempts': []})
    if seen - {normalized[-1]['id']} - ancestors[normalized[-1]['id']]:
        raise ValueError('La consegna finale deve integrare tutte le fasi del piano')
    if project_type == 'animated_video':
        required = VIDEO_TEAM - omissions.keys()
        if required - {s['agent'] for s in normalized}:
            raise ValueError('Video animato: pianifica PhotoCraft, EffectCraft, SoundCraft e FilmCraft; '
                             'omissioni solo per requisiti espliciti dell’utente')
        if 'filmcraft' in required and normalized[-1]['agent'] != 'filmcraft':
            raise ValueError('FilmCraft deve integrare e verificare il prodotto audiovisivo finale')
        for s in normalized:
            if s['agent'] == 'effectcraft' and 'photocraft' in required and not any(
                    p['agent'] == 'photocraft' and p['id'] in ancestors[s['id']] for p in normalized):
                raise ValueError('L’animazione deve utilizzare gli asset di PhotoCraft')
    with locked(workspace) as folder:
        old = load(folder, workspace)
        if old and any(s['status'] != 'completed' for s in old['steps']):
            raise ValueError('Esiste già un piano aperto: leggilo e prosegui le fasi, senza cancellare i risultati')
        if old:
            atomic_json(folder / (old['id'] + '.json'), old)
        value = {'id': uuid.uuid4().hex, 'workspace_key': workspace_key(workspace),
                 'brief': clean_summary(brief), 'project_type': project_type,
                 'omissions': {k: clean_summary(v) for k, v in omissions.items()},
                 'created_at': utcnow(), 'updated_at': utcnow(), 'steps': normalized}
        atomic_json(folder / 'project.json', value)
    return read_project(workspace)


def revise_step(workspace, step_id, reason):
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('Specifica il problema da correggere nel brief')
    with locked(workspace) as folder:
        project = load(folder, workspace)
        if not project or not any(s['id'] == step_id for s in project['steps']):
            raise ValueError('Fase non trovata')
        if any(s['status'] == 'running' for s in project['steps']):
            raise ValueError('Attendi il termine della fase attiva prima della revisione')
        invalid = {step_id}
        for step in project['steps']:
            if step['id'] in invalid or invalid.intersection(step['depends_on']):
                invalid.add(step['id'])
                step.update(status='needs_revision', revision=clean_summary(reason))
        project['updated_at'] = utcnow()
        atomic_json(folder / 'project.json', project)
    return read_project(workspace)


def archive_plan(workspace, reason):
    """End an abandoned plan without deleting a single product or attempt."""
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('Specifica il motivo dell’archiviazione')
    with locked(workspace) as folder:
        value = load(folder, workspace)
        if not value:
            return None
        if any(s['status'] == 'running' for s in value['steps']):
            raise ValueError('Non archiviare un piano con una fase in esecuzione')
        value.update(archived_at=utcnow(), archive_reason=clean_summary(reason))
        atomic_json(folder / (value['id'] + '.json'), value)
        (folder / 'project.json').unlink()
    return {'id': value['id'], 'archived': True, 'files_preserved': True}


def execute_step(workspace, agent, task, step_id, invoke):
    """Enforce assignments and real input links, then persist outcome before returning."""
    snapshot = read_project(workspace)
    if not step_id and (not snapshot or all(s['status'] == 'completed' for s in snapshot['steps'])):
        return invoke(task)
    with locked(workspace) as folder:
        project = load(folder, workspace)
        if not project:
            raise ValueError('Crea prima il piano con studio_plan')
        step = next((s for s in project['steps'] if s['id'] == step_id), None)
        if not step or step['agent'] != agent:
            raise ValueError('Indica lo step_id assegnato a questo specialista nel piano')
        if any(s['status'] == 'running' for s in project['steps']):
            raise ValueError('Una fase del progetto è già in esecuzione')
        if step['status'] == 'completed':
            raise ValueError('Fase già completata: prosegui la fase successiva')
        if len(step['attempts']) >= MAX_ATTEMPTS:
            raise ValueError('Tre tentativi già eseguiti: segnala il blocco e i file salvati, senza riprovare in ciclo')
        deps = [s for s in project['steps'] if s['id'] in step['depends_on']]
        if any(s['status'] != 'completed' for s in deps):
            raise ValueError('Completa e verifica le dipendenze prima di questa fase')
        inputs = [{'step_id': s['id'], 'agent': s['agent'],
                   'output_files': s['attempts'][-1]['output_files']} for s in deps]
        previous = step['attempts'][-1] if step['attempts'] else None
        attempt = {'started_at': utcnow(), 'status': 'running', 'gateway_session': GATEWAY_SESSION}
        step['attempts'].append(attempt)
        step['status'] = 'running'
        project['updated_at'] = utcnow()
        atomic_json(folder / 'project.json', project)
        project_id = project['id']
        contract = ('\n\nPiano della squadra: fase ' + step_id + ', obiettivo: ' + step['goal'] +
                    '\nPassaggi verificati dei colleghi (usa i file pertinenti come input reali e '
                    'registrali in source_files; non ricrearli):\n' + json.dumps(inputs, ensure_ascii=False))
        if previous:
            contract += ('\nRipresa del tentativo precedente: ' + json.dumps(previous, ensure_ascii=False) +
                         '\nIspeziona i file salvati e work/checkpoint.json se presente; riusa quanto valido, '
                         'non ricominciare da zero. Non modificare i file precedenti: '
                         'porta nella nuova cartella i sorgenti necessari, ripristina i collegamenti e verifica nuovamente.')
    def started(output_dir):
        with locked(workspace) as folder:
            value = load(folder, workspace)
            current = next(s for s in value['steps'] if s['id'] == step_id)
            current['attempts'][-1]['output_dir'] = output_dir
            atomic_json(folder / 'project.json', value)

    try:
        result = json.loads(invoke(task + contract, started))
        handoff = result.get('handoff', {})
        issues = []
        if result.get('ok'):
            if not handoff.get('output_files') or not handoff.get('checks'):
                issues.append('Mancano output o controlli della consegna')
            if any(c.get('status') != 'passed' for c in handoff.get('checks', [])):
                issues.append('Controlli falliti o non eseguiti: revisione necessaria')
            delivery = handoff.get('delivery', {})
            if delivery.get('source_status') not in ('included', 'not_applicable') or any(
                    f.get('reopen', {}).get('status') != 'passed' for f in delivery.get('files', [])):
                issues.append('Sorgenti o riapertura non verificati')
            used = set(handoff.get('source_files', []))
            for dep in inputs:
                if not used.intersection(dep['output_files']):
                    issues.append('Manca il collegamento agli output della fase ' + dep['step_id'])
        if issues:
            result.update(ok=False, error='; '.join(issues))
    except Exception as exc:
        result = {'ok': False, 'error': clean_summary(str(exc))}
    with locked(workspace) as folder:
        project = load(folder, workspace)
        if not project or project['id'] != project_id:
            raise RuntimeError('Piano cambiato durante l’esecuzione')
        step = next(s for s in project['steps'] if s['id'] == step_id)
        attempt = step['attempts'][-1]
        step['status'] = 'completed' if result.get('ok') else 'needs_revision'
        attempt.update(status=step['status'], finished_at=utcnow(),
                       output_dir=result.get('output_dir') or attempt.get('output_dir', ''),
                       output_files=result.get('handoff', {}).get('output_files', [])[:100],
                       error=clean_summary(result.get('error', '')))
        project['updated_at'] = utcnow()
        atomic_json(folder / 'project.json', project)
    result['project'] = {'id': project_id, 'step_id': step_id, 'status': step['status'],
                         'attempt': len(step['attempts']), 'max_attempts': MAX_ATTEMPTS,
                         'next_steps': [s['id'] for s in project['steps'] if s['status'] == 'pending'
                                        and all(next(p for p in project['steps'] if p['id'] == d)['status'] == 'completed'
                                                for d in s['depends_on'])]}
    return json.dumps(result, ensure_ascii=False)
