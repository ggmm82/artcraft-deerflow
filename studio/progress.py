"""Bounded, persistent operational progress shared by Gateway and native workers.

Only explicit work summaries and allowlisted event metadata are recorded. CLI
transcripts, prompts, reasoning blocks and tool arguments are never published.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time

JOB_ID = re.compile(r'artcraft-job-[0-9a-f]{12}\Z')
TERMINAL = {'completed', 'failed', 'timed_out'}
PHASES = {'queued', 'starting', 'preparing', 'planning', 'waiting_model',
          'running_tool', 'creating', 'exporting', 'checking', 'finalizing', *TERMINAL}
LABELS = {
    'queued': 'In attesa della squadra', 'starting': 'Avvio dello specialista',
    'preparing': 'Preparazione degli strumenti e delle skill',
    'planning': 'Definizione del piano operativo', 'waiting_model': 'In attesa della risposta del modello',
    'running_tool': 'Esecuzione di uno strumento', 'creating': 'Creazione dei file',
    'exporting': 'Esportazione dei risultati', 'checking': 'Verifica dei file e dei sorgenti',
    'finalizing': 'Preparazione della consegna', 'completed': 'Incarico concluso; risultati disponibili',
    'failed': 'Incarico non completato', 'timed_out': 'Tempo massimo raggiunto',
}
SECRET = re.compile(r'(?i)\b(?:sk-[a-z0-9_-]{8,}|ya29\.[a-z0-9_.-]+|4/0[a-z0-9_-]+)|'
                    r'(?i:bearer\s+)[a-z0-9_.-]+|(?i:(?:api[_-]?key|token|password)\s*[:=]\s*)\S+')
APPS = {'photocraft', 'vectorcraft', 'filmcraft', 'lightcraft', 'pdfcraft', 'effectcraft',
        'designcraft', 'gridcraft', 'wordcraft', 'deckcraft', 'cadcraft', 'soundcraft', 'figcraft', 'blender', 'calibre',
        'playwright', 'aubio', 'fluidsynth', 'epubcheck', 'pandoc', 'typst', 'freecad', 'whisper', 'ffmpeg', 'workspace'}


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def workspace_key(workspace):
    return hashlib.sha256(os.fsencode(Path(workspace).resolve())).hexdigest()


def clean_summary(value, limit=280):
    return SECRET.sub('[omesso]', str(value or '')).replace('\x00', '')[:limit]


def job_path(workspace, job_id):
    if not JOB_ID.fullmatch(job_id):
        raise ValueError('Identificatore incarico non valido')
    root = Path(workspace).resolve()
    path = root / '.studio-jobs' / job_id / 'progress.json'
    if not path.resolve().is_relative_to(root):
        raise ValueError('Percorso avanzamento non valido')
    return path


def read_status(path):
    path = Path(path)
    if path.is_symlink() or path.stat().st_size > 100000:
        raise ValueError('Stato avanzamento non valido')
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or value.get('phase') not in PHASES:
        raise ValueError('Stato avanzamento non valido')
    return value


@contextmanager
def edit_status(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock_fd = os.open(path.with_suffix('.lock'), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(lock_fd, 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            value = read_status(path) if path.exists() else {}
            yield value
            fd, temporary = tempfile.mkstemp(dir=path.parent)
            try:
                with os.fdopen(fd, 'w') as stream:
                    json.dump(value, stream, ensure_ascii=False, allow_nan=False)
                os.replace(temporary, path)
            finally:
                Path(temporary).unlink(missing_ok=True)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def update(path, phase=None, summary=None, **fields):
    with edit_status(path) as value:
        now = utcnow()
        value.update(fields)
        value['updated_at'] = now
        if phase:
            if phase not in PHASES:
                raise ValueError('Fase non valida')
            if summary and phase in {'planning', 'creating', 'exporting', 'checking', 'finalizing'}:
                value['work_summary'] = clean_summary(summary)
            summary = clean_summary(summary or LABELS[phase])
            if value.get('phase') != phase:
                value['phase_started_at'] = now
            value.update(phase=phase, summary=summary, last_activity_at=now)
            if phase == 'running_tool':
                value.update(execution_state='tool', execution_started_at=now)
            elif phase == 'waiting_model':
                value.update(execution_state='model', execution_started_at=now)
            elif phase in TERMINAL:
                value['execution_state'] = 'finished'
            if phase in TERMINAL:
                value['finished_at'] = now
            history = value.setdefault('events', [])
            if not history or history[-1]['phase'] != phase or history[-1]['summary'] != summary:
                value['event_count'] = value.get('event_count', 0) + 1
                history.append({'seq': value['event_count'], 'at': now, 'phase': phase, 'summary': summary})
                value['events'] = history[-60:]
        return value.copy()


def create_job(workspace, job_id, agent, engine, model, tool_call_id=None):
    path = job_path(workspace, job_id)
    update(path, 'queued', job_id=job_id, agent=agent, engine=engine, model=clean_summary(model),
           workspace_key=workspace_key(workspace),
           tool_call_id=tool_call_id, created_at=utcnow(), heartbeat_at=None,
           started_at=None, deadline_at=None, files=[], files_count=0)
    return path


def tool_label(command):
    """Describe the installed app, never publish shell arguments or contents."""
    if not isinstance(command, str):
        return LABELS['running_tool']
    names = '|'.join(sorted(APPS))
    command = command.lower()
    match = re.search(r'\bcraft\s+(?:(?:batch|run|help|commands|tools)\s+)?(' + names + r')\b|'
                      r'(?:^|[;&|\n])\s*(?:/usr/local/bin/)?(' + names + r')(?:-cli)?(?=\s|$)', command)
    if match:
        app = next(g for g in match.groups() if g).capitalize()
        if re.search(r'\b(?:render-frame|preview)\b', command):
            return 'Controllo un’anteprima con ' + app
        if re.search(r'\b(?:render|export|bounce|bounce_mix)\b', command):
            return 'Esporto il risultato con ' + app
        if re.search(r'\b(?:info|inspect)\b', command):
            return 'Verifico il progetto con ' + app
        if re.search(r'\b(?:help|commands|tools)\b', command):
            return 'Consulto i comandi di ' + app
        return 'Comando ' + app + ' in esecuzione'
    if re.search(r'(?:^|[;&|\n])\s*(?:/[^\s]+/)?(?:ebook-(?:convert|meta|polish)|calibre-debug|calibredb)\b', command):
        return 'Comando Calibre in esecuzione'
    if re.search(r'\bffprobe\b', command):
        return 'Verifico formato, durata e tracce del file'
    if re.search(r'\bffmpeg\b', command) and 'volumedetect' in command:
        return 'Misuro il segnale audio del risultato'
    if re.search(r'\b(?:craft)\s+(?:help|commands|tools)\b', command):
        return 'Consultazione dei comandi dello strumento'
    return LABELS['running_tool']


def output_snapshot(output_dir):
    root = Path(output_dir).resolve()
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in ('work', '.git', '.cache')
                         and not (Path(directory) / d).is_symlink())[:30]
        for name in sorted(names):
            path = Path(directory) / name
            if name.startswith('.') or name == 'handoff.json' or path.is_symlink():
                continue
            try:
                if path.resolve().is_relative_to(root) and path.is_file():
                    stat = path.stat()
                    files.append({'name': clean_summary(path.relative_to(root).as_posix()),
                                  'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns})
            except OSError:
                continue
            if len(files) >= 100:
                return files
    return files


class Reporter:
    def __init__(self, output_dir, job):
        self.output_dir = Path(output_dir)
        workspace = self.output_dir.parents[2]
        self.path = job_path(workspace, job['run_id'])
        if not self.path.exists():
            create_job(workspace, job['run_id'], job['agent'], job['engine'], job['model'])
        self.stop_event = threading.Event()
        self.thread = None
        self.last_cli_event = None
        self.last_signal = 0
        self.execution_state = 'model'
        self.tool_events = []
        self.engine, self.model = job['engine'], job['model']

    def emit(self, phase, summary=None, **fields):
        if phase in ('running_tool', 'waiting_model'):
            self.execution_state = 'tool' if phase == 'running_tool' else 'model'
        try:
            update(self.path, phase, summary, **fields)
        except (OSError, ValueError):
            pass  # Telemetry must not abort a valid delivery.

    def start(self, timeout):
        now = time.time()
        self.emit('preparing', started_at=utcnow(),
                  deadline_at=datetime.fromtimestamp(now + timeout, timezone.utc).isoformat())
        self.pulse()
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()
        return self

    def pulse(self):
        try:
            files = output_snapshot(self.output_dir)
            with edit_status(self.path) as value:
                now = utcnow()
                if value.get('files') != files:
                    value['last_activity_at'] = now
                    value['last_file_change_at'] = now
                value.update(heartbeat_at=now, updated_at=now, files=files, files_count=len(files))
                try:
                    from .resource_usage import snapshot
                    from .operations import identity
                except ImportError:
                    from resource_usage import snapshot
                    from operations import identity
                value['resources'] = snapshot()
                operations = []
                for record in sorted((self.output_dir / 'work/operations').glob('*/status.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:8]:
                    if not record.is_symlink() and record.stat().st_size < 30000:
                        operation = json.loads(record.read_text())
                        if operation.get('state') == 'running' and operation.get('pid') and identity(operation['pid']) != operation.get('process_identity'):
                            operation['state'] = 'interrupted'
                        operations.append(operation)
                previous = {o.get('id'): o for o in value.get('operations', []) if isinstance(o, dict)}
                value['operations'] = operations
                active = next((o for o in operations if o.get('state') == 'running'), None)
                if active and active.get('progress') and active.get('progress') != previous.get(active.get('id'), {}).get('progress'):
                    value['last_activity_at'] = now
        except (OSError, ValueError, TypeError):
            pass

    def _watch(self):
        while not self.stop_event.wait(2):
            self.pulse()

    def close(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=3)
        self.pulse()

    def model_signal(self):
        # A provider event is distinct from the monitor heartbeat and file changes.
        try:
            update(self.path, last_model_event_at=utcnow())
        except (OSError, ValueError):
            pass

    def cli_event(self, engine, event):
        if not isinstance(event, dict):
            return
        self.model_signal()
        # Persist only tool identity/lifecycle, never arguments, text or reasoning.
        item = event.get('item') or {}
        item_type = item.get('type') if isinstance(item, dict) else None
        if event.get('type') in ('item.started', 'item.completed') and item_type in (
                'command_execution', 'mcp_tool_call', 'image_generation', 'image_generation_call', 'web_search'):
            self.tool_events.append({'at': utcnow(), 'event': event['type'], 'tool_type': item_type,
                                     'tool': clean_summary(item.get('tool') or item_type, 80)})
            self.tool_events = self.tool_events[-250:]
            try:
                folder = self.output_dir / 'work'
                folder.mkdir(exist_ok=True)
                path = folder / 'tool-events.json'
                if not folder.is_symlink() and folder.resolve().is_relative_to(self.output_dir.resolve()) and not path.is_symlink():
                    path.write_text(json.dumps({'engine': self.engine, 'model': clean_summary(self.model), 'events': self.tool_events}))
                    path.chmod(0o600)
            except (OSError, ValueError):
                pass
        kind = event.get('type') if engine == 'codex' else event.get('event')
        if engine == 'codex' and kind not in ('item.started', 'item.completed', 'turn.started', 'turn.completed'):
            return
        if engine == 'gemini':
            if kind != 'step_update':
                return
            step = event.get('step_update') or {}
            identity = (step.get('step_index'), step.get('state'), step.get('step_type'))
            # Repeated duration/status frames are a signal of life, not new work.
            # New generated text counts as activity, but its contents stay private.
            if identity == self.last_cli_event and not step.get('text_delta'):
                return
            self.last_cli_event = identity
        if time.monotonic() - self.last_signal > 2:
            self.last_signal = time.monotonic()
            try:
                update(self.path, last_activity_at=utcnow())
            except (OSError, ValueError):
                pass
        if engine == 'codex':
            item = event.get('item') or {}
            if kind == 'item.started' and item.get('type') == 'command_execution':
                self.emit('running_tool', tool_label(item.get('command')))
            elif kind == 'item.completed' and item.get('type') == 'command_execution':
                code = item.get('exit_code')
                self.emit('waiting_model', 'Comando concluso' + (f' (uscita {code})' if isinstance(code, int) else ''))
            elif kind == 'item.started' and item.get('type') == 'mcp_tool_call':
                self.emit('running_tool', 'Esecuzione di uno strumento MCP')
            elif kind == 'item.completed' and item.get('type') == 'mcp_tool_call':
                self.emit('waiting_model', 'Strumento MCP concluso; elaborazione del risultato')
            elif kind == 'item.started' and item.get('type') in ('image_generation', 'image_generation_call'):
                self.emit('running_tool', 'Generazione di immagini tramite il modello')
            elif kind == 'item.completed' and item.get('type') in ('image_generation', 'image_generation_call'):
                self.emit('waiting_model', 'Generazione immagini conclusa; elaborazione del risultato')
            elif kind == 'turn.started':
                self.emit('waiting_model')
        elif kind == 'step_update':
            step = event.get('step_update') or {}
            if step.get('step_type') == 'tool':
                if step.get('state') == 'DONE':
                    self.emit('waiting_model', 'Strumento concluso; elaborazione del risultato')
                elif step.get('state') == 'ACTIVE':
                    info = step.get('tool_info') or {}
                    parameters = info.get('parameters') or {}
                    if not isinstance(parameters, dict):
                        parameters = {}
                    self.emit('running_tool', tool_label(parameters.get('command')))
            elif step.get('step_type') == 'finish':
                self.emit('finalizing')


def public_status(value):
    """Allowlist every returned field even if a worker modified its own file."""
    result = {key: clean_summary(value.get(key)) for key in (
        'job_id', 'agent', 'role_id', 'role_title', 'role_version', 'engine', 'model', 'phase', 'summary', 'work_summary', 'created_at',
        'started_at', 'finished_at', 'deadline_at', 'phase_started_at', 'execution_state', 'execution_started_at', 'last_model_event_at', 'last_file_change_at', 'last_activity_at', 'heartbeat_at', 'updated_at', 'error_code', 'action', 'worker_exit_at', 'cleanup_started_at', 'cleanup_finished_at')}
    result['resources_reclaimed'] = value.get('resources_reclaimed') is True
    result['cleanup_error'] = value.get('cleanup_error') is True
    result['cancel_error'] = value.get('cancel_error') is True
    result['can_stop'] = value.get('can_stop') is True
    result['cancel_requested'] = value.get('cancel_requested') is True
    position = value.get('queue_position', 0)
    result['queue_position'] = position if type(position) is int and 0 <= position <= 100000 else 0
    result['events'] = [{k: clean_summary(e.get(k)) for k in ('at', 'phase', 'summary')}
                        for e in value.get('events', [])[-60:] if isinstance(e, dict)]
    result['files'] = [{'name': clean_summary(f.get('name')), 'size': f.get('size', 0)}
                       for f in value.get('files', [])[:100] if isinstance(f, dict)
                       and isinstance(f.get('size'), int) and f['size'] >= 0]
    result['files_count'] = len(result['files'])
    result['event_count'] = len(result['events'])
    def numbers(source, keys):
        import math
        if not isinstance(source, dict):
            return {}
        return {k: source.get(k) for k in keys if type(source.get(k)) in (int, float) and math.isfinite(source[k]) and source[k] >= 0}
    result['resources'] = numbers(value.get('resources') or {}, ('memory_bytes', 'memory_peak_bytes', 'memory_limit_bytes', 'oom_kills', 'cpu_seconds'))
    result['limits'] = numbers(value.get('limits') or {}, ('cpus', 'memory_mib', 'tmp_mib', 'model_wait_seconds'))
    result['operations'] = []
    for op in value.get('operations', [])[:8]:
        if not isinstance(op, dict):
            continue
        item = {k: clean_summary(op.get(k), 100) for k in ('id', 'label', 'state')}
        item.update(numbers(op, ('elapsed_seconds', 'oom_kills', 'estimate_seconds')))
        item['progress'] = numbers(op.get('progress') or {}, ('done', 'total'))
        result['operations'].append(item)
    return result


def list_jobs(workspace):
    root = Path(workspace).resolve()
    jobs = root / '.studio-jobs'
    if not jobs.exists() or jobs.is_symlink():
        return []
    values = []
    for directory in jobs.iterdir():
        if directory.is_symlink() or not JOB_ID.fullmatch(directory.name):
            continue
        try:
            path = job_path(root, directory.name)
            value = read_status(path)
            # DeerFlow copies user-data when branching a conversation. A copied
            # progress file must not masquerade as a worker on the new thread.
            if value.get('workspace_key') == workspace_key(root):
                values.append(public_status(value))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    return sorted(values, key=lambda v: (v['phase'] not in TERMINAL, v['created_at']), reverse=True)[:20]


def main():
    parser = argparse.ArgumentParser(description='Pubblica un breve aggiornamento operativo ArtCraft')
    parser.add_argument('--phase', choices=['planning', 'creating', 'exporting', 'checking', 'finalizing'], required=True)
    parser.add_argument('--summary', required=True)
    args = parser.parse_args()
    output = Path(os.environ['ARTCRAFT_OUTPUT_DIR'])
    update(job_path(output.parents[2], output.name), args.phase, args.summary)
    print('Aggiornamento operativo registrato')


if __name__ == '__main__':
    main()
