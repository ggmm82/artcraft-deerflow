"""DeepSeek API transport and bounded tool loop used by the real worker."""
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

BASE_URL = 'https://api.deepseek.com'

try:
    from .handoff import validate_handoff
except ImportError:
    from handoff import validate_handoff


def request(key, path, payload=None, timeout=120):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE_URL + path, data=data,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Provider response bodies can contain reflected request information.
        if error.code == 401:
            raise ValueError('Chiave DeepSeek rifiutata') from None
        raise RuntimeError(f'DeepSeek HTTP {error.code}') from None
    except (OSError, ValueError) as error:
        if isinstance(error, ValueError) and str(error) == 'Chiave DeepSeek rifiutata':
            raise
        raise RuntimeError('Connessione DeepSeek non riuscita') from None


def models(key):
    result = request(key, '/models', timeout=30)
    return [m['id'] for m in result['data'] if isinstance(m.get('id'), str)]


def run(model, prompt, output_dir, timeout):
    key = json.loads(Path('/credentials/api.json').read_text())['api_key']
    messages = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content':
        'Esegui adesso l’incarico del coordinatore con run_command. '
        'Scrivi realmente i file e handoff.json nella cartella assegnata dal sistema.'}]
    tools = [{'type': 'function', 'function': {'name': 'run_command',
        'description': 'Esegue un comando shell nella sandbox ArtCraft. Salva i risultati nella cartella assegnata.',
        'parameters': {'type': 'object', 'properties': {'command': {'type': 'string'}}, 'required': ['command']}}}]
    deadline = time.monotonic() + timeout
    usage = []
    for turn in range(32):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Timeout dello specialista DeepSeek')
        if turn == 28:
            messages.append({'role': 'user', 'content': 'Completa ora la consegna e handoff.json. Indica not_run per i controlli non svolti.'})
        result = request(key, '/chat/completions', {
            'model': model, 'messages': messages, 'tools': tools, 'max_tokens': 6000,
            'thinking': {'type': 'disabled'}}, timeout=min(remaining, 180))
        usage.append(result.get('usage', {}))
        (output_dir / 'work/deepseek-usage.json').write_text(json.dumps(usage))
        choice = result['choices'][0]
        if choice.get('finish_reason') == 'length':
            raise RuntimeError('Risposta DeepSeek troncata dal limite token')
        message = choice['message']
        messages.append(message)
        calls = message.get('tool_calls', [])
        if not calls:
            try:
                validate_handoff(output_dir, Path('/mnt/user-data'))
            except (OSError, ValueError) as error:
                messages.append({'role': 'user', 'content':
                    'La consegna non è ancora valida: ' + str(error).replace(key, '[REDACTED]')[:800] +
                    '. Correggi i file con run_command. La cartella obbligatoria è ' + str(output_dir) +
                    '; salva qui handoff.json secondo lo schema della skill. La risposta finale non scrive file.'})
                continue
            return message.get('content') or ''
        for call in calls:
            try:
                if call['function']['name'] != 'run_command':
                    raise ValueError('Tool sconosciuto')
                command = json.loads(call['function']['arguments'])['command']
                if not isinstance(command, str):
                    raise ValueError('command deve essere una stringa')
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Timeout dello specialista DeepSeek')
                completed = subprocess.run(['bash', '-lc', command], cwd=output_dir,
                    capture_output=True, text=True, errors='replace', timeout=min(90, remaining))
                response = {'returncode': completed.returncode,
                            'stdout': completed.stdout[-12000:], 'stderr': completed.stderr[-3000:]}
            except (ValueError, KeyError, subprocess.TimeoutExpired) as error:
                response = {'error': str(error).replace(key, '[REDACTED]')}
            messages.append({'role': 'tool', 'tool_call_id': call['id'],
                             'content': json.dumps(response, ensure_ascii=False)})
    raise RuntimeError('Limite dei turni DeepSeek raggiunto prima della conclusione')
