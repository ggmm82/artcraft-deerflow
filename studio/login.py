"""CLI-owned browser authentication, displayed through a bounded pseudo-terminal."""
import os
import pty
import re
import select
import signal
import subprocess
import threading
import time
import uuid

from .docker_runtime import IMAGE, EXECUTION_LOCK, base_arguments, mount, remove
from .state import STATE, atomic_json, credential_dir

SESSIONS = {}
ANSI = re.compile(r'\x1b\][^\x07]*\x07|\x1b\[[0-?]*[ -/]*[@-~]|\x1b[>=]')


class LoginSession:
    def __init__(self, engine):
        if not EXECUTION_LOCK.acquire(blocking=False):
            raise RuntimeError('Un lavoro o un login è già attivo')
        self.id = uuid.uuid4().hex
        self.engine = engine
        self.name = 'artcraft-login-' + self.id[:12]
        self.text = ''
        self.returncode = None
        self.closed = False
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self.started = time.monotonic()
        master, slave = pty.openpty()
        self.fd = master
        credentials = credential_dir(engine)
        if engine == 'gemini':
            atomic_json(credentials / 'settings.json',
                        {'security': {'auth': {'selectedType': 'oauth-personal'}}})
            cli = ['gemini', '--prompt', 'Rispondi solo OK', '--output-format', 'json']
        elif engine == 'codex':
            cli = ['codex', 'login', '--device-auth']
        else:
            os.close(master)
            os.close(slave)
            EXECUTION_LOCK.release()
            raise ValueError('Motore sconosciuto')
        try:
            installation = (STATE / 'installation-id').read_text().strip()
            args = base_arguments(self.name) + ['-it', '--label',
                    f'org.artcraft.studio.installation={installation}', '--mount',
                    mount(credentials, '/root/' + ('.codex' if engine == 'codex' else '.gemini')),
                    IMAGE, *cli]
            self.process = subprocess.Popen(['docker', *args], stdin=slave, stdout=slave,
                                            stderr=slave, start_new_session=True)
        except Exception:
            os.close(master)
            EXECUTION_LOCK.release()
            raise
        finally:
            os.close(slave)
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            while self.process.poll() is None:
                if self._cancel.is_set() or time.monotonic() - self.started > 600:
                    self._terminate()
                    break
                ready, _, _ = select.select([self.fd], [], [], 0.3)
                if ready:
                    try:
                        chunk = os.read(self.fd, 8192)
                    except OSError:
                        break
                    if not chunk:
                        break
                    with self._lock:
                        self.text = (self.text + ANSI.sub('', chunk.decode('utf-8', 'replace')))[-64000:]
            self.returncode = self.process.wait(timeout=10)
        finally:
            if self.process.poll() is None:
                self._terminate()
            remove(self.name)
            os.close(self.fd)
            self.closed = True
            EXECUTION_LOCK.release()

    def _terminate(self):
        remove(self.name)
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGTERM)

    def public(self):
        with self._lock:
            return {'id': self.id, 'engine': self.engine, 'text': self.text,
                    'finished': self.closed, 'returncode': self.returncode}

    def write(self, text):
        if self.closed or self.process.poll() is not None:
            raise ValueError('Sessione terminata')
        if len(text) > 4096 or '\x00' in text:
            raise ValueError('Input non valido')
        os.write(self.fd, (text.strip() + '\n').encode())

    def cancel(self):
        self._cancel.set()


def start(engine):
    # Finished terminal transcripts are short-lived and never persisted to logs.
    for identifier, session in list(SESSIONS.items()):
        if session.closed and time.monotonic() - session.started > 600:
            SESSIONS.pop(identifier, None)
    session = LoginSession(engine)
    SESSIONS[session.id] = session
    return session.public()
