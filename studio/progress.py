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
    'finalizing': 'Preparazione della consegna', 'completed': 'Consegna verificata',
    'failed': 'Incarico non completato', 'timed_out': 'Tempo massimo raggiunto',
}
SECRET = re.compile(r'(?i)\b(?:sk-[a-z0-9_-]{8,}|ya29\.[a-z0-9_.-]+|4/0[a-z0-9_-]+)|'
                    r'(?i:bearer\s+)[a-z0-9_.-]+|(?i:(?:api[_-]?key|token|password)\s*[:=]\s*)\S+')
APPS = {'photocraft', 'vectorcraft', 'filmcraft', 'lightcraft', 'pdfcraft', 'effectcraft',
        'designcraft', 'gridcraft', 'wordcraft', 'deckcraft', 'cadcraft', 'soundcraft', 'figcraft'}


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def workspace_key(workspace):
    return hashlib.sha256(os.fsencode(Path(workspace).resolve())).hexdigest()


def clean_summary(value):
    return SECRET.sub('[omesso]', str(value or '')).replace('\x00', '')[:280]


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
            value.update(phase=phase, summary=summary, last_activity_at=now)
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
    match = re.search(r'(?:\bcraft\s+|(?:^|[;&|])\s*(?:/usr/local/bin/)?)(' + names + r')(?=\s|$)', command.lower())
    if match:
        return 'Comando ' + match.group(1).capitalize() + ' in esecuzione'
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

    def emit(self, phase, summary=None, **fields):
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
                value.update(heartbeat_at=now, updated_at=now, files=files, files_count=len(files))
        except (OSError, ValueError):
            pass

    def _watch(self):
        while not self.stop_event.wait(2):
            self.pulse()

    def close(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=3)
        self.pulse()

    def cli_event(self, engine, event):
        if not isinstance(event, dict):
            return
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
        'job_id', 'agent', 'engine', 'model', 'phase', 'summary', 'work_summary', 'created_at',
        'started_at', 'finished_at', 'deadline_at', 'last_activity_at', 'heartbeat_at', 'updated_at')}
    result['events'] = [{k: clean_summary(e.get(k)) for k in ('at', 'phase', 'summary')}
                        for e in value.get('events', [])[-60:] if isinstance(e, dict)]
    result['files'] = [{'name': clean_summary(f.get('name')), 'size': f.get('size', 0)}
                       for f in value.get('files', [])[:100] if isinstance(f, dict)
                       and isinstance(f.get('size'), int) and f['size'] >= 0]
    result['files_count'] = len(result['files'])
    result['event_count'] = len(result['events'])
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
