"""Only the trusted Gateway controls Docker. Workers never receive its socket."""
import json
import os
import subprocess
import threading
import uuid
from pathlib import Path

from .state import STATE, effective_agent, credential_dir, connection_status

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


def base_arguments(name):
    return ['run', '--name', name, '--label', f'{LABEL}={OWNER}',
            '--init', '--cap-drop=ALL', '--security-opt=no-new-privileges',
            '--pids-limit=256', '--memory=1536m', '--memory-swap=1536m',
            '--cpus=1.5', '--network=bridge', '--tmpfs', '/tmp:rw,size=256m',
            '--env', 'NO_BROWSER=true', '--env', 'TZ=Europe/Rome']


def remove(name):
    result = subprocess.run(['docker', 'rm', '-f', name], capture_output=True,
                            text=True, timeout=30)
    if result.returncode and 'No such container' not in result.stderr:
        # Do not admit another worker unless reclamation was confirmed.
        raise RuntimeError('Rimozione sandbox non confermata; riavvia il Gateway per recuperarla')


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
        raise ValueError('Collega Gemini nel pannello La tua squadra')
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
            IMAGE, 'node', '/opt/studio/gemini_bridge.mjs', '/job.json']
        try:
            completed = subprocess.run(['docker', *args], capture_output=True, text=True,
                                       timeout=timeout + 60)
        except subprocess.TimeoutExpired:
            raise RuntimeError('Timeout Gemini: riprova dalla chat') from None
        try:
            result = json.loads(completed.stdout)
        except (ValueError, TypeError):
            raise RuntimeError('Risposta del coordinatore Gemini non valida') from None
        if completed.returncode or result.get('ok') is not True:
            raise RuntimeError('Gemini non disponibile: verifica account, quota e modello in La tua squadra')
        return result['response']
    finally:
        remove(name)
        if 'job' in locals():
            job.unlink(missing_ok=True)
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


def delegate(agent_id, task, workspace):
    settings = effective_agent(agent_id)
    if not settings or not settings['enabled']:
        raise ValueError('Specialista sconosciuto o disattivato')
    engine = settings['engine']
    if not connection_status(engine):
        raise ValueError(f'Collega {engine} nel pannello Studio prima di usare lo specialista')
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    # At most one login or worker at a time: bounded RAM and serialized credential refresh.
    if not EXECUTION_LOCK.acquire(timeout=120):
        raise RuntimeError('Studio occupato; riprova quando il lavoro attivo termina')
    name = 'artcraft-job-' + uuid.uuid4().hex[:12]
    try:
        jobs = STATE / 'jobs'
        jobs.mkdir(exist_ok=True)
        job = jobs / (name + '.json')
        payload = {'agent': agent_id, 'engine': engine, 'model': settings['model'],
                   'instructions': settings['instructions'], 'skills': settings['skills'], 'task': task,
                   'run_id': name, 'timeout': 1500}
        if engine == 'deepseek' and not payload['model']:
            import yaml
            config = yaml.safe_load((STATE / 'config.yaml').read_text())
            payload['model'] = next(m['model'] for m in config['models'] if m['use'] == 'studio.deepseek_provider:StudioDeepSeekChatModel')
        from .state import atomic_json
        atomic_json(job, payload)
        installation = (STATE / 'installation-id').read_text().strip()
        args = base_arguments(name) + ['--label', f'org.artcraft.studio.installation={installation}',
            '--mount', mount(workspace, '/mnt/user-data'),
            '--mount', mount(credential_dir(engine), '/credentials', read_only=engine == 'deepseek'),
            '--mount', mount(job, '/job.json', True),
            IMAGE, 'python3', '/opt/studio/run_agent.py', '/job.json']
        completed = subprocess.run(['docker', *args], capture_output=True, text=True,
                                   timeout=1560)
        response = completed.stdout
        if completed.returncode:
            raise RuntimeError('Lo specialista ha fallito: ' +
                               (response or completed.stderr)[-3000:])
        try:
            result = json.loads(response)
        except (ValueError, TypeError):
            raise RuntimeError('Risposta JSON dello specialista non valida') from None
        if not isinstance(result, dict) or result.get('ok') is not True:
            raise RuntimeError('Lo specialista non ha confermato il completamento')
        return json.dumps(result, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        raise RuntimeError('Timeout dello specialista; il container viene rimosso') from None
    finally:
        remove(name)
        if 'job' in locals():
            job.unlink(missing_ok=True)
        EXECUTION_LOCK.release()
