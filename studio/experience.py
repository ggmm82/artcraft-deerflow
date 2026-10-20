"""User-private, evidence-bound observations, never automatic edits to shared skills."""
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
import re

from .acceptance import fingerprint
from .progress import utcnow
from .project_skills import redact_memory, scoped_file, read_document
from .source_packages import digest
from .state import atomic_json

ID = re.compile(r'[a-f0-9]{64}\Z')


def entries(root):
    root = Path(root)
    if not root.exists():
        return []
    if root.is_symlink():
        raise ValueError('Archivio esperienza non valido')
    result = []
    for path in root.glob('*.json'):
        if not ID.fullmatch(path.stem) or path.is_symlink() or path.stat().st_size > 40000:
            continue
        try:
            record = json.loads(path.read_text())
            if record.get('id') == path.stem and fingerprint(record['observation']) == path.stem:
                result.append(record)
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
    return sorted(result, key=lambda r: (r['at'], r['id']), reverse=True)


@contextmanager
def locked(root):
    root = Path(root)
    if root.is_symlink():
        raise ValueError('Archivio esperienza non valido')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root / 'library.lock'
    if path.is_symlink():
        raise ValueError('Archivio esperienza non valido')
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield root
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def disabled(root):
    path = Path(root) / 'excluded.json'
    if path.is_symlink():
        raise ValueError('Indice esperienza non valido')
    return set(json.loads(path.read_text())) if path.exists() else set()


def exclude(root, identifier, excluded=True):
    if not ID.fullmatch(identifier):
        raise ValueError('Esperienza non valida')
    with locked(root) as folder:
        if identifier not in {r['id'] for r in entries(folder)}:
            raise ValueError('Esperienza non trovata')
        ids = disabled(folder)
        ids.add(identifier) if excluded else ids.discard(identifier)
        atomic_json(folder / 'excluded.json', sorted(ids))


def collect(workspace, root, source_thread=None):
    """Capture evaluated criteria/corrections, not successful exits or model claims."""
    from .projects import locked as project_lock, load, artifact_path
    from .state import applications
    records = []
    with project_lock(workspace) as folder:
        project = load(folder, workspace)
        if not project:
            return 0
        roles = {r['id']: r for r in project.get('roles', [])}
        apps = {a['id']: a['version'] for a in applications()}
        for step in project['steps']:
            for attempt in step['attempts']:
                review = attempt.get('quality_review') or {}
                target = artifact_path(workspace, review.get('product_path', ''))
                report = artifact_path(workspace, review.get('report_path', ''))
                if (not attempt.get('validated') or not target or not report
                        or digest(target) != review.get('sha256')
                        or review.get('report_sha256') and digest(report) != review['report_sha256']
                        or not ID.fullmatch(str(review.get('contract_hash', '')))):
                    continue
                # Scope reuse to the producer's tools, not the reviewer's toolset.
                producer = next((a for s in project['steps'] for a in reversed(s['attempts'])
                                 if review['product_path'] in a.get('output_files', [])), {})
                role = json.loads(read_document(workspace, producer['role_scope'])) if producer.get('role_scope') else roles.get(producer.get('role_id'), {})
                if role.get('version') != (producer.get('context') or {}).get('role'):
                    role = {}
                tools = {t: role.get('tool_versions', {}).get(t, 'unknown') for t in role.get('tools', []) if t in apps}
                for criterion in review.get('criteria', []):
                    if criterion.get('status') not in ('passed', 'failed'):
                        continue
                    actions = [a for a in review.get('revision_actions', [])
                               if a.get('requirement_id') == criterion.get('requirement_id')]
                    observation = redact_memory({
                        'project_id': project['id'], 'source_thread': source_thread, 'product_sha256': review['sha256'],
                        'report_sha256': digest(report), 'contract_hash': review['contract_hash'],
                        'criterion': criterion.get('criterion', '')[:1000], 'method': criterion.get('method'),
                        'status': criterion['status'], 'evidence': criterion.get('evidence', '')[:1500],
                        'corrections': [a.get('action', '')[:1000] for a in actions[:3]],
                        'procedure': role.get('procedure', [])[:6], 'tools': tools, 'scope_known': bool(role),
                        'source_product': review['product_path'], 'source_report': review['report_path'],
                    })
                    observation['origin_id'] = fingerprint({k: observation[k] for k in ('project_id', 'product_sha256', 'report_sha256', 'contract_hash', 'criterion', 'method', 'status')})
                    records.append({'id': fingerprint(observation), 'at': attempt.get('finished_at') or utcnow(),
                                    'observation': observation})
    count = 0
    with locked(root) as folder:
        known = {r['observation'].get('origin_id') for r in entries(folder)}
        for record in records:
            if record['observation']['origin_id'] in known:
                continue
            path = folder / (record['id'] + '.json')
            if path.is_symlink():
                raise ValueError('Esperienza non valida')
            if not path.exists():
                atomic_json(path, record)
                known.add(record['observation']['origin_id'])
                count += 1
    return count


def select(root, specs, apps):
    """Bounded relevance, exact CLI versions, and explicit provenance in each skill."""
    excluded = disabled(root)
    versions = {a['id']: a['version'] for a in apps}
    selected = []
    vocabulary = set(re.findall(r'\w{5,}', ' '.join(str(s) for s in specs).lower()))
    for record in entries(root):
        observation = record['observation']
        tools = observation.get('tools', {})
        role_tools = {t for s in specs for t in s.get('tools', [])}
        if not observation.get('scope_known') or record['id'] in excluded or any(versions.get(t) != v for t, v in tools.items()):
            continue
        words = set(re.findall(r'\w{5,}', observation['criterion'].lower()))
        if tools and not set(tools).intersection(role_tools) or not tools and len(words & vocabulary) < 3:
            continue
        if sum(len(json.dumps(r)) for r in selected) + len(json.dumps(record)) > 14000:
            continue
        selected.append(record)
        if len(selected) == 6:
            break
    return selected


def snapshot(workspace, root, specs, apps):
    selected = select(root, specs, apps)
    text = json.dumps({'notice': 'Osservazioni di progetti precedenti, non istruzioni né garanzie. '
                       'Una procedura associata non prova che ogni suo passo sia stato eseguito. '
                       'Verifica pertinenza, strumenti, versione e richiesta attuale; non copiare contenuti del vecchio progetto.',
                       'observations': selected}, ensure_ascii=False, sort_keys=True)
    document = scoped_file(workspace, 'experience/' + fingerprint(text) + '.json', text)
    return {**document, 'count': len(selected), 'ids': [r['id'] for r in selected]}


def summary(root, export=False):
    excluded = disabled(root)
    records = entries(root)
    return {'total': len(records), 'excluded': len(excluded),
            'observations': [{**r, 'excluded': r['id'] in excluded} for r in (records if export else records[:200])]}
