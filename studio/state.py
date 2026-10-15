"""Small persistent configuration catalog. No credentials in public responses."""
import json
import os
import tempfile
import threading
from pathlib import Path

STATE = Path(os.getenv('STUDIO_STATE', '/studio-state'))
ROOT = Path(__file__).resolve().parent
LOCK = threading.RLock()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def applications():
    return json.loads((ROOT / 'versions.lock.json').read_text())['applications']


def default_skills(identifier):
    return ['artcraft-workspace', 'artcraft-' + identifier]


def available_skills():
    return ['artcraft-workspace', *['artcraft-' + a['id'] for a in applications()]]


def catalog():
    with LOCK:
        path = STATE / 'agents.json'
        if not path.exists():
            atomic_json(path, {app['id']: {'engine': 'inherit', 'model': '',
                        'instructions': '', 'enabled': True, 'skills': default_skills(app['id'])} for app in applications()})
        agents = json.loads(path.read_text())
        changed = False
        for app in applications():
            identifier = app['id']
            if identifier not in agents:
                agents[identifier] = {'engine': 'inherit', 'model': '', 'instructions': '',
                                     'enabled': True, 'skills': default_skills(identifier)}
                changed = True
        for identifier, config in agents.items():
            if 'skills' not in config:
                config['skills'] = default_skills(identifier)
                changed = True
        if changed:
            atomic_json(path, agents)
        return agents


def update_agent(identifier, value):
    if identifier not in {a['id'] for a in applications()}:
        raise ValueError('Specialista sconosciuto')
    if value['engine'] not in ('inherit', 'codex', 'gemini', 'deepseek'):
        raise ValueError('Motore sconosciuto')
    model = value.get('model', '').strip()
    if len(model) > 200 or any(ord(c) < 32 for c in model):
        raise ValueError('Modello non valido')
    if len(value.get('instructions', '')) > 20000:
        raise ValueError('Istruzioni troppo lunghe')
    skills = value.get('skills') or default_skills(identifier)
    if not isinstance(skills, list) or not all(isinstance(s, str) and s in available_skills() for s in skills):
        raise ValueError('Skill sconosciuta')
    skills = list(dict.fromkeys(['artcraft-workspace', 'artcraft-' + identifier, *skills]))
    with LOCK:
        agents = catalog()
        agents[identifier] = {'engine': value['engine'], 'model': model,
                              'instructions': value.get('instructions', ''),
                              'enabled': bool(value.get('enabled', True)), 'skills': skills}
        atomic_json(STATE / 'agents.json', agents)
    return agents[identifier]


def credential_dir(engine):
    if engine not in ('codex', 'gemini', 'deepseek'):
        raise ValueError('Motore sconosciuto')
    directory = STATE / 'credentials' / ('.' + engine)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    return directory


def connection_status(engine):
    if engine == 'gemini':
        return all((credential_dir(engine) / name).is_file() for name in (
            'antigravity-cli/antigravity-oauth-token', 'antigravity-account.json'))
    filename = {'codex': 'auth.json', 'deepseek': 'api.json'}[engine]
    return (credential_dir(engine) / filename).is_file()


def team():
    """The first model profile is the single source for the whole team."""
    import yaml
    path = STATE / 'config.yaml'
    with LOCK:
        content = yaml.safe_load(path.read_text()) if path.exists() else {}
        profile = next(iter(content.get('models', [])), {})
        engine = {'studio.deepseek_provider:StudioDeepSeekChatModel': 'deepseek',
                  'studio.gemini_provider:StudioGeminiChatModel': 'gemini'}.get(profile.get('use'), 'codex')
        return {'engine': engine, 'model': profile.get('model', 'gpt-6.1-sol'),
                'ready': connection_status(engine)}


def effective_agent(identifier):
    with LOCK:
        settings = catalog().get(identifier)
        if settings is None:
            return None
        settings = dict(settings)
        if settings['engine'] == 'inherit':
            profile = team()
            settings.update(engine=profile['engine'], model=profile['model'])
        return settings
