"""Runtime-owned delivery identity and technical acceptance, separate from taste."""
import json
from pathlib import Path
import subprocess

try:
    from .source_packages import digest, verify_archive, sample, NATIVE
except ImportError:
    from source_packages import digest, verify_archive, sample, NATIVE


def read_review(handoff, output_dir, workspace, engine):
    """Read a separate review of an existing product, never of a self-made export."""
    path = Path(output_dir) / 'quality-review.json'
    if not path.is_file() or str(path) not in handoff['output_files'] or path.stat().st_size > 30000:
        return None
    value = json.loads(path.read_text())
    target = Path(value.get('product_path', '')).resolve()
    if (not target.is_relative_to(Path(workspace).resolve()) or target.is_relative_to(Path(output_dir).resolve())
            or str(target) not in handoff['source_files'] or not target.is_file()):
        raise ValueError('La revisione deve riguardare un prodotto esistente in source_files, non un nuovo export')
    criteria = value.get('criteria', [])
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= 20:
        raise ValueError('Revisione: specificare criteri concreti del brief')
    for criterion in criteria:
        if (not isinstance(criterion, dict) or not criterion.get('criterion') or not criterion.get('evidence')
                or criterion.get('status') not in ('passed', 'failed', 'not_run')
                or criterion.get('method') not in ('visual', 'listening', 'technical', 'content')):
            raise ValueError('Revisione: criterio, metodo, stato ed evidenza obbligatori')
        # Current DeepSeek transport accepts text only. Numeric measurements do
        # not become an image inspection or an audition by naming them so.
        if engine == 'deepseek' and criterion['method'] in ('visual', 'listening'):
            criterion.update(status='not_run', evidence='Il collegamento DeepSeek attuale è testuale; valutazione sensoriale non disponibile.')
    visual = target.suffix.lower() in ('.mp4', '.mov', '.webm', '.gif', '.png', '.jpg', '.jpeg', '.pdf', '.svg', '.glb')
    audio = target.suffix.lower() in ('.wav', '.mp3', '.m4a', '.ogg')
    for needed, method in ((visual, 'visual'), (audio, 'listening')):
        if needed and not any(c['method'] == method for c in criteria):
            criteria.append({'criterion': 'Qualità del contenuto ' + method, 'method': method,
                             'status': 'not_run', 'evidence': 'Il rapporto contiene soltanto controlli di altre modalità.'})
    return {'product_path': str(target), 'sha256': digest(target), 'criteria': criteria,
            'status': 'passed' if all(c['status'] == 'passed' for c in criteria) else 'needs_review',
            'report_path': str(path), 'note': 'Valutazione dello specialista; non una garanzia oggettiva di qualità artistica.'}


def build_delivery(handoff, output_dir, *, purpose='work', native=True):
    root = Path(output_dir)
    delivery = handoff['delivery']
    issues, files, packages = [], [], []
    for item in delivery['files']:
        path = Path(item['path'])
        record = {**item, 'sha256': digest(path), 'size': path.stat().st_size}
        if item['role'] == 'source_archive':
            try:
                if path.suffix.lower() != '.zip':
                    raise ValueError('Archivio sorgenti: usare ZIP per il collaudo di trasferimento')
                record['verification'] = verify_archive(path, native=native)
                packages.append(record)
            except (OSError, ValueError, RuntimeError) as error:
                record['verification'] = {'status': 'failed', 'error': str(error)[:1000]}
                issues.append(path.name + ': ' + str(error)[:1000])
        if item['role'] in ('editable_source', 'source_archive') and item['reopen']['status'] != 'passed':
            issues.append(path.name + ': riapertura non verificata')
        files.append(record)
    if delivery['source_status'] == 'unavailable':
        issues.append('Sorgenti modificabili mancanti: ' + delivery['source_note'])
    if any(Path(f['path']).suffix in NATIVE and f['role'] == 'editable_source' for f in files) and not packages:
        issues.append('Progetto nativo senza pacchetto portabile verificato: usare source_packages.py pack')
    for item in files:
        if Path(item['path']).suffix in NATIVE and item['role'] == 'editable_source':
            item['open_with'] = 'Usa il pacchetto sorgenti ZIP della stessa consegna e le sue istruzioni; questo progetto isolato può perdere i media.'
            item['limitations'] = [*item.get('limitations', []), 'Il progetto scaricato da solo non include le risorse collegate.']
    renders = [c for p in packages for c in p['verification']['checks'] if c.get('check') == 'filmcraft_render']
    if purpose == 'delivery' and renders:
        for item in files:
            if item['role'] != 'export' or Path(item['path']).suffix.lower() not in ('.mp4', '.mov', '.webm', '.mkv'):
                continue
            try:
                probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', item['path']],
                                       capture_output=True, text=True, check=True, timeout=30)
                info = json.loads(probe.stdout)
                video = next(s for s in info['streams'] if s['codec_type'] == 'video')
                matches = []
                for rendered in renders:
                    if (abs(float(info['format']['duration']) - rendered['duration']) > .15
                            or video['width'] != rendered['width'] or video['height'] != rendered['height']):
                        continue
                    errors = [sum(abs(a-b) for a, b in zip(sample(item['path'], s['seconds']), s['luma'])) / 144
                              for s in rendered['samples']]
                    if max(errors) <= 12:
                        matches.append({'source': rendered['file'], 'mean_luma_errors': errors})
                item['source_match'] = matches
                if not matches:
                    issues.append(Path(item['path']).name + ': il render dei sorgenti non corrisponde al video consegnato (durata, dimensioni o tre fotogrammi)')
            except (OSError, ValueError, StopIteration, subprocess.SubprocessError) as error:
                issues.append('Confronto sorgente/video non completato: ' + str(error)[:300])
    issues.extend(c['name'] + ': ' + c['evidence'][:300] for c in handoff['checks'] if c['status'] == 'failed')
    value = {'id': root.name, 'title': handoff['task'][:200], 'purpose': purpose,
             'technical_status': 'passed' if not issues else 'needs_revision',
             'issues': issues[:20], 'files': files, 'source_status': delivery['source_status'],
             'source_note': delivery['source_note'][:1000],
             'quality_status': 'not_reviewed',
             'note': 'I controlli tecnici non certificano qualità visiva, musicale o aderenza creativa al brief.'}
    # Owned by the runtime; never trust a model-authored file with this name.
    path = root / 'delivery-manifest.json'
    if path.is_symlink():
        raise ValueError('Manifesto di consegna non valido')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    return value
