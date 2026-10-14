"""Initialize persistent configuration before the Gateway imports DeerFlow."""
import hashlib
import json
import os
import secrets
import uuid
from pathlib import Path

import yaml

from .state import STATE, ROOT, catalog


def configure_coordinator(model):
    from .state import LOCK
    with LOCK:
        path = STATE / 'config.yaml'
        content = yaml.safe_load(path.read_text())
        for item in content['models']:
            if item['name'] == 'studio-codex':
                item['model'] = model
        temporary = path.with_suffix('.yaml.tmp')
        temporary.write_text(yaml.safe_dump(content, allow_unicode=True, sort_keys=False))
        temporary.chmod(0o600)
        temporary.replace(path)


def initialize():
    STATE.mkdir(parents=True, exist_ok=True)
    password = os.getenv('STUDIO_PASSWORD', '')
    if len(password) < 16:
        raise ValueError('STUDIO_PASSWORD deve contenere almeno 16 caratteri')
    identifier = STATE / 'installation-id'
    if not identifier.exists():
        identifier.write_text(uuid.uuid4().hex)
    key = STATE / 'credentials-key'
    if not key.exists():
        import base64
        key.write_text(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())
        key.chmod(0o600)
    os.environ['DEER_FLOW_CREDENTIALS_KEY'] = key.read_text().strip()
    os.environ['BETTER_AUTH_SECRET'] = hashlib.sha256(password.encode()).hexdigest()
    path = STATE / 'config.yaml'
    if not path.exists():
        path.write_text((ROOT / 'deerflow.yaml').read_text())
        path.chmod(0o600)
    extension = STATE / 'extensions_config.json'
    if not extension.exists():
        extension.write_text((ROOT / 'extensions_config.json').read_text())
    catalog()


def main():
    initialize()
    from .docker_runtime import cleanup_orphans
    cleanup_orphans()
    # exec preserves signal delivery, while the env secrets stay in this process tree.
    os.execvp('uvicorn', ['uvicorn', 'studio.app:app', '--host', '0.0.0.0',
                        '--port', '8001', '--workers', '1',
                        '--timeout-graceful-shutdown', '15'])


if __name__ == '__main__':
    main()
