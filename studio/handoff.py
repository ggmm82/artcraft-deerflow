"""Validate specialist deliverables before reporting a successful run."""
import json
from pathlib import Path


DELIVERY_SCHEMA = {
    'type': 'object', 'properties': {
        'source_status': {'type': 'string', 'enum': ['included', 'unavailable', 'not_applicable']},
        'source_note': {'type': 'string', 'minLength': 1},
        'files': {'type': 'array', 'minItems': 1, 'items': {
            'type': 'object', 'properties': {
                'path': {'type': 'string'},
                'role': {'type': 'string', 'enum': ['editable_source', 'source_archive', 'export', 'dependency', 'preview', 'report']},
                'format': {'type': 'string', 'minLength': 1},
                'open_with': {'type': 'string', 'minLength': 1},
                'editability': {'type': 'string', 'minLength': 1},
                'reopen': {'type': 'object', 'properties': {
                    'status': {'type': 'string', 'enum': ['passed', 'failed', 'not_run']},
                    'evidence': {'type': 'string', 'minLength': 1}},
                    'required': ['status', 'evidence'], 'additionalProperties': False},
                'limitations': {'type': 'array', 'items': {'type': 'string', 'minLength': 1}}},
            'required': ['path', 'role', 'format', 'open_with', 'editability', 'reopen', 'limitations'],
            'additionalProperties': False}}},
    'required': ['source_status', 'source_note', 'files'], 'additionalProperties': False}

SOURCE_REF = {'type':'object','properties':{'path':{'type':'string'},'member':{'type':'string'}},
              'required':['path'],'additionalProperties':False}
DELIVERY_SCHEMA['properties']['components'] = {'type':'array','minItems':1,'maxItems':12,'items':{
    'type':'object','properties':{'name':{'type':'string'},'tool':{'type':'string'},
        'artifacts':{'type':'array','minItems':1,'maxItems':64,'items':SOURCE_REF},
        'sources':{'type':'array','minItems':1,'maxItems':24,'items':SOURCE_REF},
        'provided_inputs':{'type':'array','maxItems':64,'items':{'type':'string'}}},
    'required':['name','tool','artifacts','sources'],'additionalProperties':False}}
DELIVERY_SCHEMA['properties']['timing'] = {'type':'object','properties':{
    'master':{'type':'string'},'cues':{'type':'array','minItems':1,'maxItems':12,'items':{
        'type':'object','properties':{'name':{'type':'string'},'visual_seconds':{'type':'number'},
            'tolerance_seconds':{'type':'number','minimum':.01,'maximum':.25}},
        'required':['name','visual_seconds'],'additionalProperties':False}}},
    'required':['master','cues'],'additionalProperties':False}


def validate_delivery(value):
    """Validate claims and downloadable sources, not actual application compatibility."""
    delivery = value.get('delivery')
    if not isinstance(delivery, dict) or delivery.get('source_status') not in ('included', 'unavailable', 'not_applicable'):
        raise ValueError('handoff.json: delivery e source_status obbligatori')
    if not isinstance(delivery.get('source_note'), str) or not delivery['source_note'].strip():
        raise ValueError('handoff.json: source_note deve spiegare sorgenti e limiti')
    files = delivery.get('files')
    if not isinstance(files, list) or not files:
        raise ValueError('handoff.json: delivery.files obbligatorio')
    outputs = set(value['output_files'])
    allowed = outputs | set(value.get('previews', []))
    seen, sources, unverified = set(), [], False
    for item in files:
        if not isinstance(item, dict):
            raise ValueError('handoff.json: metadati file non validi')
        path = item.get('path')
        if not isinstance(path, str) or path not in allowed or path in seen:
            raise ValueError('handoff.json: delivery.path deve essere unico e già elencato negli output o anteprime')
        seen.add(path)
        if item.get('role') not in ('editable_source', 'source_archive', 'export', 'dependency', 'preview', 'report'):
            raise ValueError('handoff.json: ruolo di consegna non valido')
        for field in ('format', 'open_with', 'editability'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f'handoff.json: delivery.files richiede {field}')
        reopen = item.get('reopen')
        if (not isinstance(reopen, dict) or reopen.get('status') not in ('passed', 'failed', 'not_run')
                or not isinstance(reopen.get('evidence'), str) or not reopen['evidence'].strip()):
            raise ValueError('handoff.json: riapertura richiede status ed evidence')
        limitations = item.get('limitations')
        if not isinstance(limitations, list) or not all(isinstance(s, str) and s.strip() for s in limitations):
            raise ValueError('handoff.json: limitations deve essere una lista di stringhe')
        if reopen['status'] != 'passed':
            unverified = True
            if not limitations:
                if reopen['status'] == 'not_run' and item['role'] in ('dependency', 'report'):
                    # A missing repetition of an auxiliary check must not discard
                    # an otherwise usable job. Keep not_run, add the truthful
                    # limit and warning; never promote an unverified source.
                    note = 'Riapertura non eseguita per ' + Path(path).name + ': ' + reopen['evidence']
                    item['limitations'] = [note]
                    if note not in value['warnings']:
                        value['warnings'].append(note)
                else:
                    raise ValueError('handoff.json: riapertura non verificata richiede un limite esplicito')
        if item['role'] in ('editable_source', 'source_archive'):
            if path not in outputs:
                raise ValueError('handoff.json: il sorgente modificabile deve essere scaricabile in output_files')
            sources.append(item)
    if outputs - seen:
        raise ValueError('handoff.json: mancano metadati di consegna per alcuni output')
    status = delivery['source_status']
    if (status == 'included') != bool(sources):
        raise ValueError('handoff.json: source_status non corrisponde ai sorgenti consegnati')
    if status == 'not_applicable' and (not any(item['role'] == 'report' for item in files)
            or any(item['role'] not in ('report', 'preview', 'dependency') for item in files)):
        raise ValueError('handoff.json: un prodotto esportato richiede sorgenti o indisponibilità dichiarata')
    if (status == 'unavailable' or unverified) and not any(w.strip() for w in value['warnings']):
        raise ValueError('handoff.json: sorgenti mancanti o riapertura non verificata richiedono warnings')


def validate_handoff(output_dir, workspace, *, require_delivery=False):
    output_dir, workspace = Path(output_dir).resolve(), Path(workspace).resolve()
    manifest = output_dir / 'handoff.json'
    if not manifest.resolve().is_relative_to(output_dir):
        raise ValueError('handoff.json esterno alla cartella assegnata')
    value = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or not isinstance(value.get('task'), str) or not value['task'].strip():
        raise ValueError('handoff.json: task obbligatorio')
    # Model-authored bookkeeping is retained in work/, never advertised as a
    # creative output. Normalize only known report files; sources and arbitrary
    # work files still go through all the original checks below.
    delivery = value.get('delivery')
    if isinstance(delivery, dict) and isinstance(delivery.get('files'), list) and isinstance(value.get('output_files'), list):
        bookkeeping = {str(output_dir / 'work' / name) for name in
                       ('method.json', 'checkpoint.json', 'tool-events.json', 'tool-lessons.json')}
        removed = {item.get('path') for item in delivery['files'] if isinstance(item, dict)
                   and item.get('role') == 'report' and isinstance(item.get('path'), str) and item['path'] in bookkeeping
                   and not Path(item['path']).is_symlink() and Path(item['path']).is_file()
                   and Path(item['path']).resolve().is_relative_to(output_dir)}
        if removed:
            value['output_files'] = [p for p in value['output_files'] if not isinstance(p, str) or p not in removed]
            delivery['files'] = [item for item in delivery['files'] if not isinstance(item, dict)
                                 or not isinstance(item.get('path'), str) or item['path'] not in removed]
            value['normalization'] = {'technical_reports_retained': sorted(removed)}
            if isinstance(value.get('warnings'), list):
                value['warnings'].append('Registri tecnici conservati in work/ e separati dai prodotti consegnati.')
    for field in ('source_files', 'output_files', 'previews'):
        paths = value.get(field, [] if field == 'previews' else None)
        if not isinstance(paths, list) or (field == 'output_files' and not paths):
            raise ValueError(f'handoff.json: {field} deve essere una lista di file')
        if field == 'output_files' and len(paths) > 40:
            raise ValueError('handoff.json: raggruppa risorse e sorgenti in pacchetti; massimo 40 download per consegna')
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
    if require_delivery or 'delivery' in value:
        validate_delivery(value)
    return value
