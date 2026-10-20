"""User-private, evidence-bound observations, never automatic edits to shared skills."""
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
import re

from .acceptance import fingerprint
from .progress import utcnow
from .project_skills import redact_memory, scoped_file, read_document, ROLE_ID
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


def method_record(workspace, attempt):
    from .projects import artifact_path
    path = artifact_path(workspace, str(Path(attempt.get('output_dir', '')) / 'work/method.json'))
    trace = artifact_path(workspace, str(Path(attempt.get('output_dir', '')) / 'work/tool-events.json'))
    trace_ref = {'path': str(trace), 'sha256': digest(trace)} if trace else None
    generation = []
    work = Path(workspace) / Path(str(Path(attempt.get('output_dir', '')) / 'work')).relative_to('/mnt/user-data') if str(attempt.get('output_dir', '')).startswith('/mnt/user-data/') else None
    if work and work.resolve().is_relative_to(Path(workspace).resolve()) and not work.is_symlink():
        for candidate in sorted(work.glob('imagegen-*.json'))[:12]:
            report = artifact_path(workspace, '/mnt/user-data/' + candidate.relative_to(workspace).as_posix())
            if report and report.stat().st_size <= 16000:
                generation.append({'path': '/mnt/user-data/' + report.relative_to(workspace).as_posix(), 'sha256': digest(report)})
    if not path or path.stat().st_size > 16000:
        return {'status': 'not_recorded', 'tool_events': trace_ref, 'generation_records': generation, 'notice': 'Procedimento eseguito non registrato; non dedurlo dal risultato.'}
    try:
        value = json.loads(path.read_text())
        if not isinstance(value, dict) or not isinstance(value.get('approach'), str):
            raise ValueError()
        clean = {'approach': value['approach'][:1500]}
        for key in ('steps', 'limits'):
            items = value.get(key, [])
            if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
                raise ValueError()
            clean[key] = [item[:1000] for item in items[:12]]
        scripts = []
        filenames = value.get('scripts', [])
        if not isinstance(filenames, list):
            raise ValueError()
        for filename in filenames[:12]:
            script = artifact_path(workspace, filename) if isinstance(filename, str) else None
            if script and script.stat().st_size <= 1048576 and script.suffix.lower() in ('.py', '.js', '.mjs', '.cjs', '.sh', '.json'):
                scripts.append({'path': filename, 'sha256': digest(script)})
        return redact_memory({'status': 'reported', 'path': str(path), 'sha256': digest(path),
                              'declared_method': clean, 'scripts': scripts, 'tool_events': trace_ref, 'generation_records': generation,
                              'notice': 'Procedimento dichiarato dal produttore, non rieseguito dal registro esperienza.'})
    except (OSError, ValueError, TypeError):
        return {'status': 'invalid', 'notice': 'Procedimento registrato in formato non utilizzabile.'}


def producer_role(workspace, attempt, roles):
    """Recover declared tool/procedure context from immutable legacy skill versions."""
    from .projects import artifact_path
    if attempt.get('role_scope'):
        return json.loads(read_document(workspace, attempt['role_scope']))
    identifier, version = attempt.get('role_id', ''), (attempt.get('context') or {}).get('role', '')
    current = roles.get(identifier, {})
    if current.get('version') == version:
        return current
    if not isinstance(identifier, str) or not ROLE_ID.fullmatch(identifier) or not isinstance(version, str) or not ID.fullmatch(version):
        return {}
    name = f'/mnt/user-data/.studio-project/roles/{identifier}/{version}/SKILL.md'
    path = artifact_path(workspace, name)
    if not path or path.stat().st_size > 100000:
        return {}
    text = path.read_text()
    def section(title):
        marker = '## ' + title + '\n\n'
        return text.split(marker, 1)[1].split('\n\n## ', 1)[0] if text.count(marker) == 1 else ''
    try:
        tools, _ = json.JSONDecoder().raw_decode(section('Strumenti effettivi').lstrip())
        if not isinstance(tools, list) or any(not isinstance(t, dict) or not isinstance(t.get('id'), str) or not isinstance(t.get('version'), str) for t in tools):
            return {}
        return {'id': identifier, 'version': version,
                'procedure': [line[2:] for line in section('Metodo operativo').splitlines() if line.startswith('- ')][:12],
                'tools': [t['id'] for t in tools], 'tool_versions': {t['id']: t['version'] for t in tools},
                'skill': {'path': name, 'sha256': digest(path)}, 'scope_origin': 'saved_legacy_skill'}
    except (ValueError, TypeError):
        return {}


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
                role = producer_role(workspace, producer, roles)
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
                        'producer_method': method_record(workspace, producer),
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
        if not observation.get('scope_known') or record['id'] in excluded or any(versions.get(t) != v and not (observation.get('kind') == 'user_preference' and v == 'unknown') for t, v in tools.items()):
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


def prefer(workspace, root, delivery_id, note, source_thread=None):
    """Explicit user preference for a method; never marks a project ready or a test passed."""
    from .projects import locked as project_lock, load, artifact_path
    if not isinstance(note, str) or not 5 <= len(note.strip()) <= 2000:
        raise ValueError('Descrivi cosa vuoi riutilizzare (5–2000 caratteri)')
    with project_lock(workspace) as folder:
        project = load(folder, workspace)
        attempt = next((a for s in (project or {}).get('steps', []) for a in s['attempts']
                        if Path(a.get('output_dir', '')).name == delivery_id and a.get('validated')), None)
        if not attempt:
            raise ValueError('Scegli una lavorazione conclusa con file verificati')
        files = []
        for name in attempt.get('output_files', []):
            path = artifact_path(workspace, name)
            if path:
                files.append({'path': name, 'sha256': digest(path)})
        if not files:
            raise ValueError('I file del metodo non sono più disponibili')
        role = producer_role(workspace, attempt, {r['id']: r for r in project.get('roles', [])})
        role_skill = role.get('skill') or next((r.get('skill') for r in project.get('roles', []) if r.get('version') == role.get('version')), None)
        observation = redact_memory({
            'kind': 'user_preference', 'project_id': project['id'], 'source_thread': source_thread,
            'criterion': note.strip(), 'method': 'user_feedback', 'status': 'preferred_by_user',
            'evidence': 'Preferenza espressa dall’utente per questa lavorazione; non è un collaudo tecnico o un risultato riproducibile garantito.',
            'corrections': [], 'producer_method': method_record(workspace, attempt), 'procedure': role.get('procedure', []),
            'tools': {t: role.get('tool_versions', {}).get(t, 'unknown') for t in role.get('tools', [])},
            'scope_known': bool(role), 'models': (attempt.get('context') or {}).get('provider', {}),
            'role_skill': role_skill, 'files': files,
            'product_sha256': fingerprint(files), 'report_sha256': '',
            'contract_hash': (project.get('acceptance') or {}).get('hash'),
            'limitations': (attempt.get('delivery_record') or {}).get('issues', []),
            'instruction': 'Considera questo metodo come candidato preferito; riscopri le capacità disponibili, '
                           'confronta il brief attuale e verifica un campione. Le versioni sconosciute non sono compatibilità accertata.',
        })
        observation['origin_id'] = fingerprint(observation)
        record = {'id': fingerprint(observation), 'at': utcnow(), 'observation': observation}
    with locked(root) as folder:
        path = folder / (record['id'] + '.json')
        if not path.exists():
            atomic_json(path, record)
    return record['id']
