"""Operational metadata only; never shell code, prompts or raw transcripts."""
import re
import shlex


def describe(command):
    try:
        from .progress import APPS
    except ImportError:
        from progress import APPS
    try:
        parts = shlex.split((command or '').split('\n', 1)[0])
    except ValueError:
        parts = []
    result = {'tool': 'Shell', 'action': 'Esecuzione comando'}
    for i, part in enumerate(parts):
        name = part.rsplit('/', 1)[-1]
        if name.removesuffix('-cli') in APPS or name in ('craft', 'ffprobe', 'python', 'python3'):
            result['tool'] = name
            if name in ('python', 'python3'):
                result['action'] = 'Script Python inline'
                if i + 1 < len(parts) and re.fullmatch(r'(?:/opt/studio/|/mnt/user-data/)[\w/.-]+\.py', parts[i+1]):
                    result['action'] = parts[i+1].rsplit('/', 1)[-1]
            else:
                allowed = {'render','render-frame','export','info','inspect','verify','pack','check','run','batch','help','commands','tools','get','set','script'}
                result['action'] = next((p for p in parts[i+1:] if p in allowed), 'Esecuzione strumento')
            break
    result['files'] = list(dict.fromkeys(p for p in parts if re.fullmatch(r'/mnt/user-data/(?:outputs|uploads|workspace)/[\w/ .-]{1,240}', p)))[:8]
    return result


def diagnostic(output):
    if not isinstance(output, str):
        return ''
    # Error categories provide useful context without copying data printed by
    # a command (which may be a document, credential file or model prompt).
    for pattern, label in [
        (r'FileNotFoundError|No such file|not found', 'File, dipendenza o comando non trovato'),
        (r'PermissionError|Permission denied', 'Accesso al file non consentito'),
        (r'unrecognized arguments|unknown option|unexpected argument', 'Parametro CLI non riconosciuto'),
        (r'JSONDecodeError|invalid json', 'Documento JSON non valido'),
        (r'TimeoutError|timed out', 'Tempo di esecuzione esaurito'),
        (r'AssertionError', 'Verifica dichiarata dal comando non superata'),
        (r'TypeError|ValueError', 'Tipo o valore non accettato dallo strumento')]:
        if re.search(pattern, output[-16000:], re.I):
            return label
    return ''


def public(value):
    try:
        from .progress import clean_summary
    except ImportError:
        from progress import clean_summary
    if not isinstance(value, dict):
        return {}
    result = {k: clean_summary(value[k], 180) for k in ('tool','action','diagnostic','started_at','finished_at','id') if isinstance(value.get(k), str)}
    for k in ('duration_seconds','exit_code'):
        import math
        if type(value.get(k)) in (int,float) and math.isfinite(value[k]):
            result[k] = value[k]
    if isinstance(value.get('record_path'), str) and re.fullmatch(r'/mnt/user-data/outputs/[\w/.-]+/work/commands/[a-f0-9]{24}/status\.json', value['record_path']):
        result['record_path'] = value['record_path']
    result['files'] = [clean_summary(p, 280) for p in (value.get('files') if isinstance(value.get('files'), list) else [])[:4] if isinstance(p, str) and p.startswith('/mnt/user-data/')]
    result['changed_files'] = [clean_summary(p, 180) for p in (value.get('changed_files') if isinstance(value.get('changed_files'), list) else [])[:4] if isinstance(p, str)]
    return result
