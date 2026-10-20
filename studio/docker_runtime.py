"""Only the trusted Gateway controls Docker. Workers never receive its socket."""
import json
import os
import subprocess
import threading
import time
import uuid
from pathlib import Path

from .state import STATE, effective_agent, credential_dir, connection_status, custom_connection_path
from .progress import clean_summary, create_job, read_status, update, utcnow, workspace_key
from .work_results import failure_info, partial_files

IMAGE = os.getenv('STUDIO_SANDBOX_IMAGE', 'artcraft-deerflow-sandbox:0.1.0')
EXECUTION_LOCK = threading.Lock()
LABEL = 'org.artcraft.studio.owner'
OWNER = os.getenv('HOSTNAME', 'studio')
_mounts = None


def docker(*arguments, timeout=60):
    return subprocess.check_output(['docker', *arguments], text=True, timeout=timeout).strip()


def host_path(path):
    """Resolve the named volume's real host path, independent of Compose project name."""
    global _mounts
    path = Path(path).resolve()
    if _mounts is None:
        _mounts = json.loads(docker('inspect', OWNER))[0]['Mounts']
    for mount in sorted(_mounts, key=lambda m: len(m['Destination']), reverse=True):
        destination = Path(mount['Destination'])
        if path.is_relative_to(destination):
            relative = path.relative_to(destination)
            candidate = Path(mount['Source']) / relative
            if ',' in str(candidate) or '\n' in str(candidate):
                raise ValueError('Percorso volume non valido')
            return str(candidate)
    raise ValueError('Il percorso richiesto non appartiene a un volume del Gateway')


def mount(path, target, read_only=False):
    value = f'type=bind,src={host_path(path)},dst={target}'
    return value + (',readonly' if read_only else '')


def base_arguments(name, resources=None):
    from .runtime_settings import effective
    resources = resources or effective()
    return ['run', '--name', name, '--label', f'{LABEL}={OWNER}',
            '--init', '--cap-drop=ALL', '--security-opt=no-new-privileges',
            '--pids-limit=256', f"--memory={resources['memory_mib']}m", f"--memory-swap={resources['memory_mib']}m",
            f"--cpus={resources['cpus']}", '--network=bridge', '--tmpfs', f"/tmp:rw,size={resources['tmp_mib']}m",
            '--env', f"ARTCRAFT_CPU_THREADS={resources['threads']}",
            '--env', f"ARTCRAFT_MEMORY_MIB={resources['memory_mib']}",
            '--env', 'NO_BROWSER=true', '--env', 'TZ=Europe/Rome',
            '--env', f"TOKIO_WORKER_THREADS={resources['threads']}", '--env', f"RAYON_NUM_THREADS={resources['threads']}",
            '--env', f"OMP_NUM_THREADS={resources['threads']}", '--env', f"OPENBLAS_NUM_THREADS={resources['threads']}"]


def remove(name):
    result = subprocess.run(['docker', 'rm', '-f', name], capture_output=True,
                            text=True, timeout=30)
    if result.returncode and 'No such container' not in result.stderr:
        # Do not admit another worker unless reclamation was confirmed.
        raise RuntimeError('Rimozione sandbox non confermata; riavvia il Gateway per recuperarla')


def lifecycle(progress, **fields):
    # A telemetry write must never prevent container removal or lock release.
    try:
        update(progress, **fields)
    except (OSError, ValueError):
        pass


def cleanup_orphans():
    """A Gateway restart must reclaim workers left by its previous process."""
    # Scope to the persistent installation ID, not a shared daemon-wide prefix.
    installation = (STATE / 'installation-id').read_text().strip()
    ids = docker('ps', '-aq', '--filter', f'label=org.artcraft.studio.installation={installation}')
    for container in ids.splitlines():
        remove(container)


def generate_gemini(payload, timeout=1800):
    """No file tools or conversation volume in a coordinator generation container."""
    if not connection_status('gemini'):
        raise ValueError('Collega Antigravity nel pannello La tua squadra')
    if not EXECUTION_LOCK.acquire(timeout=120):
        raise RuntimeError('Squadra occupata; attendi il termine del lavoro attivo')
    name = 'artcraft-coordinator-' + uuid.uuid4().hex[:12]
    try:
        jobs = STATE / 'jobs'
        jobs.mkdir(exist_ok=True)
        job = jobs / (name + '.json')
        from .state import atomic_json
        atomic_json(job, payload)
        installation = (STATE / 'installation-id').read_text().strip()
        args = base_arguments(name) + ['--label', f'org.artcraft.studio.installation={installation}',
            '--mount', mount(credential_dir('gemini'), '/credentials'),
            '--mount', mount(job, '/job.json', True),
            IMAGE, 'python3', '/opt/studio/antigravity_cli.py', '/job.json']
        try:
            completed = subprocess.run(['docker', *args], capture_output=True, text=True,
                                       timeout=timeout + 60)
        except subprocess.TimeoutExpired:
            raise RuntimeError('Timeout Antigravity: riprova dalla chat') from None
        try:
            result = json.loads(completed.stdout)
        except (ValueError, TypeError):
            raise RuntimeError('Risposta del coordinatore Antigravity non valida') from None
        if completed.returncode or result.get('ok') is not True:
            raise RuntimeError('Antigravity non disponibile: verifica account, quota e modello in La tua squadra')
        return result['response']
    finally:
        remove(name)
        if 'job' in locals():
            job.unlink(missing_ok=True)
        EXECUTION_LOCK.release()


def antigravity_models():
    if not connection_status('gemini'):
        raise ValueError('Collega prima Antigravity con il tuo account Google')
    if not EXECUTION_LOCK.acquire(timeout=120):
        raise RuntimeError('Squadra occupata: riprova tra poco')
    name = 'artcraft-models-' + uuid.uuid4().hex[:12]
    try:
        installation = (STATE / 'installation-id').read_text().strip()
        args = base_arguments(name) + ['--label', f'org.artcraft.studio.installation={installation}',
            '--mount', mount(credential_dir('gemini'), '/credentials'),
            IMAGE, 'python3', '/opt/studio/antigravity_cli.py', '--models']
        result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=120)
        value = json.loads(result.stdout)
        if result.returncode or value.get('ok') is not True:
            raise RuntimeError('Ricollega Antigravity o verifica la disponibilità del tuo account Google')
        return value['models']
    finally:
        remove(name)
        EXECUTION_LOCK.release()


def codex_account(models=False):
    if not EXECUTION_LOCK.acquire(timeout=120):
        raise RuntimeError('Squadra occupata: riprova tra poco')
    name = 'artcraft-refresh-' + uuid.uuid4().hex[:12]
    try:
        installation = (STATE / 'installation-id').read_text().strip()
        args = base_arguments(name) + ['--label', f'org.artcraft.studio.installation={installation}',
            '--mount', mount(credential_dir('codex'), '/root/.codex'),
            IMAGE, 'python3', '/opt/studio/refresh_codex.py', *(['--models'] if models else [])]
        result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=90)
        if result.returncode or json.loads(result.stdout).get('ok') is not True:
            raise RuntimeError('Ricollega Codex in La tua squadra')
        return json.loads(result.stdout)
    finally:
        remove(name)
        EXECUTION_LOCK.release()


def refresh_codex_credentials():
    codex_account()


def codex_models():
    return codex_account(models=True)['models']


def delegate(agent_id, task, workspace, tool_call_id=None, on_started=None, requirements=None, purpose='work', acceptance=None, role=None):
    settings = effective_agent(agent_id)
    if not settings or not settings['enabled']:
        raise ValueError('Specialista sconosciuto o disattivato')
    role_text = None
    if role:
        from .project_skills import load_compiled
        from .state import catalog
        if agent_id != 'workspace' and agent_id not in role['tools']:
            raise ValueError('La CLI assegnata deve essere inclusa negli strumenti del ruolo')
        role_text = load_compiled(workspace, role)
        if any(not catalog().get(t, {}).get('enabled') for t in role['tools']):
            raise ValueError('Il ruolo richiede uno strumento disabilitato: rivedi il metodo o la configurazione')
        if role.get('request_hash') != (acceptance or {}).get('hash'):
            raise ValueError('Ricompila il ruolo per la richiesta corrente prima della delega')
        settings = {**settings, 'skills': list(dict.fromkeys([*settings['skills'], *['artcraft-' + t for t in role['tools']]]))}
    engine = settings['engine']
    if not connection_status(engine, settings.get('connection_id')):
        raise ValueError(f'Collega {engine} nel pannello Studio prima di usare lo specialista')
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    name = 'artcraft-job-' + uuid.uuid4().hex[:12]
    progress = create_job(workspace, name, agent_id, engine, settings['model'], tool_call_id)
    if role:
        update(progress, role_id=role['id'], role_title=role['title'], role_version=role['version'])
    output_dir = '/mnt/user-data/outputs/' + agent_id + '/' + name
    # At most one login or worker at a time: bounded RAM and serialized credential refresh.
    from .cancellation import requested, watch
    def cancelled_before_start():
        update(progress, 'failed', 'Interruzione della fase richiesta dall’utente', cancel_requested=True)
        return json.dumps({'ok': False, 'error': 'Interruzione della fase richiesta dall’utente; nessun nuovo container avviato.'})
    until = time.monotonic() + 120
    while True:
        if requested():
            return cancelled_before_start()
        if EXECUTION_LOCK.acquire(timeout=min(.2, max(0, until - time.monotonic()))):
            break
        if time.monotonic() >= until:
            update(progress, 'failed', 'Squadra occupata: tempo massimo di attesa raggiunto')
            raise RuntimeError('Studio occupato; riprova quando il lavoro attivo termina')
    try:
        if requested():
            return cancelled_before_start()
        update(progress, 'starting')
        if on_started:
            on_started(output_dir)
        jobs = STATE / 'jobs'
        jobs.mkdir(exist_ok=True)
        job = jobs / (name + '.json')
        from .runtime_settings import effective
        resources = effective()
        update(progress, limits=resources, can_stop=True)
        payload = {'resources': resources, 'agent': agent_id, 'engine': engine, 'model': settings['model'],
                   'instructions': settings['instructions'], 'skills': settings['skills'], 'task': task,
                   'run_id': name, 'timeout': 1500, 'requirements': requirements or {}, 'purpose': purpose,
                   'acceptance': acceptance, 'role': role, 'compiled_skill': role_text}
        from .projects import read_project
        payload['user_direction'] = (read_project(workspace) or {}).get('user_direction')
        if engine == 'deepseek' and not payload['model']:
            import yaml
            config = yaml.safe_load((STATE / 'config.yaml').read_text())
            payload['model'] = next(m['model'] for m in config['models'] if m['use'] == 'studio.deepseek_provider:StudioDeepSeekChatModel')
        update(progress, model=clean_summary(payload['model']))
        from .state import atomic_json
        atomic_json(job, payload)
        installation = (STATE / 'installation-id').read_text().strip()
        args = base_arguments(name, resources) + ['--label', f'org.artcraft.studio.installation={installation}',
            '--label', f'org.artcraft.studio.workspace={workspace_key(workspace)}',
            '--mount', mount(workspace, '/mnt/user-data'),
            '--mount', (mount(custom_connection_path(settings.get('connection_id')), '/credentials/api.json', True)
                        if engine == 'openai' else mount(credential_dir(engine), '/credentials', read_only=engine == 'deepseek')),
            '--mount', mount(job, '/job.json', True),
            IMAGE, 'python3', '/opt/studio/run_agent.py', '/job.json']
        with watch(lambda: request_stop(workspace, name), lambda: lifecycle(progress, cancel_error=True)):
            completed = subprocess.run(['docker', *args], capture_output=True, text=True,
                                       timeout=1560)
        lifecycle(progress, worker_exit_at=utcnow())
        response = completed.stdout
        if completed.returncode:
            status = read_status(progress)
            if status['phase'] not in ('failed', 'timed_out'):
                update(progress, 'failed')
            try:
                failure = json.loads(response)
            except (ValueError, TypeError):
                failure = {}
            if not isinstance(failure, dict):
                failure = {}
            error = ('Interruzione della fase richiesta dall’utente; i file salvati sono conservati.' if status.get('cancel_requested') else failure.get('error') or completed.stderr or 'Specialista non completato')
            try:
                container_state = json.loads(docker('inspect', '--format', '{{json .State}}', name))
                if isinstance(container_state, dict) and container_state.get('OOMKilled') is True:
                    error = 'Memoria esaurita confermata dallo stato del container. ' + error
                    previous_usage = read_status(progress).get('resources') or {}
                    update(progress, resources={**previous_usage, 'oom_kills': max(1, previous_usage.get('oom_kills', 0))})
            except (OSError, ValueError, TypeError, subprocess.SubprocessError):
                pass  # Unknown cause must not be invented from exit 137.
            attention = failure_info(error)
            available = ['/mnt/user-data/' + str(Path(p).relative_to(workspace)) for p in
                         partial_files(workspace / 'outputs' / agent_id / name)]
            update(progress, 'failed', attention['message'], error_code=attention['code'],
                   action=attention['action'])
            return json.dumps({'ok': False, 'agent': agent_id, 'engine': engine, 'output_dir': output_dir,
                               'error': clean_summary(error), 'attention': attention, 'available_files': available,
                               'partial': True, 'resume': 'Ispeziona i file salvati e work/checkpoint.json, '
                               'poi assegna una continuazione mirata. I file non sono ancora una consegna verificata.'}, ensure_ascii=False)
        try:
            result = json.loads(response)
        except (ValueError, TypeError):
            raise RuntimeError('Risposta JSON dello specialista non valida') from None
        if not isinstance(result, dict) or result.get('ok') is not True:
            raise RuntimeError('Lo specialista non ha confermato il completamento')
        update(progress, 'completed')
        return json.dumps(result, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        update(progress, 'timed_out')
        return json.dumps({'ok': False, 'agent': agent_id, 'output_dir': output_dir,
                           'available_files': ['/mnt/user-data/' + str(Path(p).relative_to(workspace)) for p in
                               partial_files(workspace / 'outputs' / agent_id / name)],
                           'partial': True, 'error': 'Limite della singola fase raggiunto (25 minuti più chiusura).',
                           'resume': 'Il container viene rimosso, i file persistono. Ispeziona work/checkpoint.json '
                           'e continua questa fase in una nuova delega; non consegnare i file provvisori come verificati.'}, ensure_ascii=False)
    except Exception:
        # Retain a more specific worker timeout or failed-delivery explanation.
        try:
            if read_status(progress)['phase'] not in ('failed', 'timed_out'):
                update(progress, 'failed')
        except (OSError, ValueError):
            pass
        raise
    finally:
        lifecycle(progress, cleanup_started_at=utcnow())
        try:
            remove(name)
        except Exception:
            update(progress, 'failed', 'Pulizia del worker non confermata: la squadra richiede un controllo', cleanup_error=True)
            raise
        lifecycle(progress, cleanup_finished_at=utcnow(), resources_reclaimed=True)
        try:
            if 'job' in locals():
                job.unlink(missing_ok=True)
        finally:
            EXECUTION_LOCK.release()


def request_stop(workspace, job_id):
    """Stop only a worker bound by Docker labels to this installation and conversation."""
    from .progress import job_path, workspace_key, TERMINAL
    path = job_path(workspace, job_id)
    status = read_status(path)
    if status.get('workspace_key') != workspace_key(workspace) or status['phase'] in TERMINAL:
        raise ValueError('Questa fase non è più in esecuzione nella conversazione')
    info = json.loads(docker('inspect', '--format', '{{json .}}', job_id, timeout=10))
    labels = info.get('Config', {}).get('Labels') or {}
    if (labels.get('org.artcraft.studio.installation') != (STATE / 'installation-id').read_text().strip()
            or labels.get('org.artcraft.studio.workspace') != workspace_key(workspace)
            or not info.get('State', {}).get('Running')):
        raise ValueError('Il worker non è controllabile da questa conversazione o è già terminato')
    update(path, cancel_requested=True)
    try:
        docker('stop', '--time', '10', job_id, timeout=20)
    except (OSError, subprocess.SubprocessError):
        update(path, cancel_requested=False)
        raise
    return {'requested': True, 'job_id': job_id}
