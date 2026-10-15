"""Validate specialist deliverables before reporting a successful run."""
import json
from pathlib import Path


def validate_handoff(output_dir, workspace):
    output_dir, workspace = Path(output_dir).resolve(), Path(workspace).resolve()
    manifest = output_dir / 'handoff.json'
    if not manifest.resolve().is_relative_to(output_dir):
        raise ValueError('handoff.json esterno alla cartella assegnata')
    value = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or not isinstance(value.get('task'), str) or not value['task'].strip():
        raise ValueError('handoff.json: task obbligatorio')
    for field in ('source_files', 'output_files', 'previews'):
        paths = value.get(field, [] if field == 'previews' else None)
        if not isinstance(paths, list) or (field == 'output_files' and not paths):
            raise ValueError(f'handoff.json: {field} deve essere una lista di file')
        for filename in paths:
            if not isinstance(filename, str):
                raise ValueError(f'handoff.json: percorso non valido in {field}')
            path = Path(filename)
            boundary = workspace if field == 'source_files' else output_dir
            if not path.is_absolute() or not path.resolve().is_relative_to(boundary):
                raise ValueError(f'handoff.json: percorso esterno in {field}')
            if not path.is_file() or (field != 'source_files' and path.stat().st_size == 0):
                raise ValueError(f'handoff.json: file mancante o vuoto in {field}')
            if field == 'output_files' and path.resolve().is_relative_to(output_dir / 'work'):
                raise ValueError('handoff.json: i file tecnici in work/ non sono prodotti finali')
    checks = value.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('handoff.json: checks obbligatori')
    for check in checks:
        if (not isinstance(check, dict) or check.get('status') not in ('passed', 'failed', 'not_run')
                or not isinstance(check.get('name'), str) or not check['name'].strip()
                or not isinstance(check.get('evidence'), str) or not check['evidence'].strip()):
            raise ValueError('handoff.json: check richiede name, status e evidence')
    if not isinstance(value.get('warnings'), list) or not all(isinstance(w, str) for w in value['warnings']):
        raise ValueError('handoff.json: warnings deve essere una lista di stringhe')
    return value
