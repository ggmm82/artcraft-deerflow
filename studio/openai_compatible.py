"""OpenAI Chat Completions transport shared by setup and sandbox workers."""
import json
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit


def endpoint(value):
    if not isinstance(value, str) or len(value) > 2000 or any(ord(c) < 33 for c in value):
        raise ValueError('Inserisci un URL HTTP o HTTPS valido, ad esempio https://host/v1')
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise ValueError('URL del provider non valido') from None
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise ValueError('Usa l’URL base del provider, senza credenziali, query o frammenti')
    path = parsed.path.rstrip('/')
    for suffix in ('/chat/completions', '/models'):
        if path.endswith(suffix):
            path = path[:-len(suffix)]
            break
    return urlunsplit((parsed.scheme, parsed.netloc, path or '/v1', '', ''))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ProviderHTTPError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(f'Provider OpenAI compatibile HTTP {code}')


def request(base_url, key, path, payload=None, timeout=120):
    req = urllib.request.Request(endpoint(base_url) + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=timeout) as response:
            value = json.load(response)
            if not isinstance(value, dict):
                raise ValueError('Risposta non valida')
            return value
    except urllib.error.HTTPError as error:
        error.close()
        if error.code in (401, 403):
            raise ValueError('Chiave API o accesso al modello rifiutato dal provider') from None
        if error.code == 429:
            raise RuntimeError('Provider OpenAI compatibile: quota o limite richieste raggiunto (HTTP 429)') from None
        if error.code in (301, 302, 303, 307, 308):
            raise ValueError('L’endpoint reindirizza: inserisci direttamente l’URL finale del servizio') from None
        raise ProviderHTTPError(error.code) from None
    except (OSError, ValueError):
        raise RuntimeError('Connessione o risposta del provider OpenAI compatibile non valida') from None


def models(base_url, key):
    data = request(base_url, key, '/models', timeout=30)
    return list(dict.fromkeys(m['id'] for m in data.get('data', [])
        if isinstance(m, dict) and isinstance(m.get('id'), str) and m['id'].strip()))


def validate_key(key):
    if not isinstance(key, str) or not key or len(key) > 4096 or any(ord(c) < 33 for c in key):
        raise ValueError('Chiave API non valida')
    return key


def validate(base_url, key, model):
    base_url = endpoint(base_url)
    validate_key(key)
    available = []
    if not model:
        try:
            available = models(base_url, key)
        except RuntimeError:
            raise ValueError('Elenco modelli non disponibile: inserisci l’ID del modello') from None
        model = available[0] if available else ''
    if not model or len(model) > 200 or any(ord(c) < 32 for c in model):
        raise ValueError('Inserisci l’ID del modello da usare')
    # A model list can be public or incomplete. Verify the actual completion API.
    check = 'artcraft_connection_check'
    payload = {'model': model,
        'messages': [{'role': 'user', 'content': 'Call artcraft_connection_check with no arguments.'}],
        'tools': [{'type': 'function', 'function': {'name': check, 'description': 'Verify tool calling.',
            'parameters': {'type': 'object', 'properties': {}, 'additionalProperties': False}}}],
        'tool_choice': {'type': 'function', 'function': {'name': check}}, 'max_tokens': 1024, 'stream': False}
    token_limit_param = 'max_tokens'
    tool_choice = 'specified'
    for fallback in range(6):
        try:
            response = request(base_url, key, '/chat/completions', payload, timeout=30)
            break
        except ProviderHTTPError as error:
            if error.code != 400 or fallback == 5:
                raise
            if fallback % 2 == 0:
                # Some providers accept only max_completion_tokens.
                token_limit_param = 'max_completion_tokens'
                payload[token_limit_param] = payload.pop('max_tokens')
            elif fallback == 1:
                # Thinking models (e.g. Kimi K3) reject a forced tool_choice:
                # require any of the offered tools instead of one named function.
                tool_choice = 'required'
                token_limit_param = 'max_tokens'
                payload['tool_choice'] = 'required'
                payload['max_tokens'] = payload.pop('max_completion_tokens')
            else:
                # Some thinking models (e.g. Kimi K2.6) reject any explicit tool_choice.
                tool_choice = 'auto'
                token_limit_param = 'max_tokens'
                del payload['tool_choice']
                payload['max_tokens'] = payload.pop('max_completion_tokens')
    if not isinstance(response.get('choices'), list) or not response['choices']:
        raise ValueError('Il provider non ha restituito una risposta Chat Completions valida')
    try:
        calls = (response['choices'][0].get('message') or {}).get('tool_calls', [])
        valid = any((c.get('function') or {}).get('name') == check
                    and json.loads(c['function'].get('arguments', '')) == {} for c in calls if isinstance(c, dict))
    except (TypeError, ValueError, AttributeError):
        valid = False
    if not valid:
        raise ValueError('Il modello non ha eseguito la chiamata di strumenti: scegli un modello con function calling')
    return base_url, model, available, token_limit_param, tool_choice


def run(model, prompt, output_dir, timeout, progress=None):
    try:
        from .deepseek import run as tool_loop
    except ImportError:
        from deepseek import run as tool_loop
    credentials = json.loads(Path('/credentials/api.json').read_text())
    def transport(path, payload, timeout):
        payload = dict(payload)
        if credentials.get('token_limit_param') == 'max_completion_tokens' and 'max_tokens' in payload:
            payload['max_completion_tokens'] = payload.pop('max_tokens')
        tool_choice = credentials.get('tool_choice')
        if isinstance(payload.get('tool_choice'), dict):
            if tool_choice == 'required':
                payload['tool_choice'] = 'required'
            elif tool_choice == 'auto':
                del payload['tool_choice']
        return request(credentials['base_url'], credentials['api_key'], path, payload, timeout)
    return tool_loop(model, prompt, output_dir, timeout, progress=progress,
        transport=transport,
        provider_label='Provider OpenAI compatibile')
