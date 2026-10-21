"""Portable native sources: inspect actual references, relocate, then reopen.

No generated script from a delivery is executed. Only this trusted module and
the pinned CLIs run. The same standalone file prepares local paths after download.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
import zipfile

NATIVE = {'.fcproj', '.ecproj', '.scraft'}
MAX_BYTES = 512 * 1024 * 1024
MAX_FILES = 12000
# Exact preparers published on main before the verifier gained more formats.
# They are never executed here: prepare() below is the trusted runtime code.
# Keep these identities when extending format checks, so existing sources reopen.
RELEASED_PREPARERS = {
    'dc64bb7d149025adba6c380ab676d0d19bbb74ea0779f70e0e514dd1a8b4c73a',  # 6e19bcabb8
    '5cc17a70890beeb481d9782cb85ecf184b64b137e1eee02f440a16eb2ddf9ede',  # 0f7da4742f
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def references(value):
    """Yield mutable path slots from native documents, including footage frames.

Names are not paths. Embedded MIDI, geometries and shapes remain untouched.
Unknown external URI schemes fail closed rather than claiming offline portability.
"""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('path', 'file_path', 'filename') and isinstance(item, str) and item:
                yield value, key, item
            elif isinstance(item, (dict, list)):
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def document(path):
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Progetto troppo grande per la verifica: ' + path.name)
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError('Documento nativo non valido: ' + path.name)
    if path.suffix == '.fcproj':
        if value.get('format') != 'filmcraft.project':
            raise ValueError('Formato FilmCraft non riconosciuto')
        sequences = [i['kind']['Sequence'] for i in value.get('project', {}).get('items', {}).values()
                     if 'Sequence' in i.get('kind', {})]
        if not any(t.get('items') for seq in sequences for k in ('video_tracks', 'audio_tracks') for t in seq.get(k, [])):
            raise ValueError('Timeline FilmCraft vuota: ' + path.name)
    elif path.suffix == '.ecproj':
        if not any(i.get('kind', {}).get('type') == 'Comp' and i['kind'].get('layers')
                   for i in value.get('items', {}).values()):
            raise ValueError('Composizione EffectCraft vuota: ' + path.name)
    elif path.suffix == '.scraft' and not value.get('tracks'):
        raise ValueError('Sessione SoundCraft vuota: ' + path.name)
    return value


def resolved_reference(project, ref, boundary, *, portable=False):
    path = Path(ref)
    if '\\' in ref or '://' in ref or (len(ref) > 1 and ref[1] == ':'):
        raise ValueError('Riferimento non portabile: ' + ref[:180])
    if portable and path.is_absolute():
        raise ValueError('Percorso assoluto nel pacchetto: ' + ref[:180])
    candidate = path if path.is_absolute() else project.parent / path
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(boundary.resolve()):
        raise ValueError('Dipendenza esterna al pacchetto/workspace: ' + ref[:180])
    if not candidate.is_file() or not candidate.stat().st_size:
        raise ValueError('Dipendenza mancante: ' + project.name + ' → ' + ref[:180])
    return candidate.resolve()


def extract(archive, destination, budget=None):
    """Bounded extraction; no links, traversal, duplicates or encrypted entries."""
    budget = budget if budget is not None else {'bytes': 0, 'files': 0}
    with zipfile.ZipFile(archive) as z:
        seen = set()
        for info in z.infolist():
            name = PurePosixPath(info.filename)
            if (name.is_absolute() or '..' in name.parts or '\\' in info.filename
                    or ':' in info.filename or not name.parts or name in seen
                    or stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1):
                raise ValueError('Archivio non sicuro o ambiguo: ' + info.filename[:100])
            seen.add(name)
            budget['bytes'] += info.file_size
            budget['files'] += 1
            if budget['bytes'] > MAX_BYTES or budget['files'] > MAX_FILES:
                raise ValueError('Pacchetto oltre il budget di verifica (512 MiB / 12000 file)')
        z.extractall(destination)  # CRC checked by ZipFile while reading each file.


def prepare(folder):
    """Trusted local preparation, no app/install/network dependency.

FilmCraft 0.7.2 resolves relative media against process cwd. Generate adjacent
*.locale.fcproj copies with local absolute paths; originals stay portable.
"""
    folder = Path(folder).resolve()
    made = []
    for project in sorted(folder.rglob('*.fcproj')):
        if project.stem.endswith('.locale'):
            continue
        value = document(project)
        for owner, key, ref in references(value.get('project', {}).get('items', {})):
            owner[key] = str(resolved_reference(project, ref, folder, portable=True))
        target = project.with_name(project.stem + '.locale.fcproj')
        if target.is_symlink():
            raise ValueError('Destinazione locale non valida')
        target.write_text(json.dumps(value, ensure_ascii=False))
        made.append(target)
    return made


def run(argv, cwd, timeout=60):
    result = subprocess.run([str(a) for a in argv], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise ValueError('Riapertura nativa fallita: ' + Path(str(argv[0])).name + ' ' + result.stderr[-500:])
    return result.stdout


def sample(path, seconds=0):
    result = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(seconds), '-i', str(path),
        '-frames:v', '1', '-vf', 'scale=16:9,format=gray', '-f', 'rawvideo', '-'],
        capture_output=True, timeout=30, check=True)
    if len(result.stdout) != 144:
        raise ValueError('Impossibile leggere il fotogramma: ' + Path(path).name)
    return list(result.stdout)


def inspect_blend(path, boundary, *, native=True):
    """Reopen using trusted code, then verify portable dependencies, not a claim."""
    if not native:
        return {'file': Path(path).name, 'status': 'not_run', 'check': 'blender_reopen'}
    result = subprocess.run(['blender-cli', 'inspect', str(path)], cwd=boundary,
        env={**os.environ, 'ARTCRAFT_WORKSPACE_ROOT': str(Path(boundary).resolve())},
        capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError('Blender: riapertura fallita: ' + result.stderr[-500:])
    info = json.loads(result.stdout)
    if not any(o.get('type') in ('MESH', 'CURVE', 'SURFACE', 'FONT', 'VOLUME', 'POINTCLOUD', 'GREASEPENCIL')
               for o in info.get('objects', [])):
        raise ValueError('Blender: progetto senza geometria modificabile')
    if info.get('limitations'):
        raise ValueError('Blender: dipendenze non collaudate: ' + '; '.join(info['limitations'])[:700])
    for dependency in info.get('dependencies', []):
        ref = dependency['reference']
        if not ref.startswith('//') or not dependency['exists']:
            raise ValueError('Blender: risorsa mancante o percorso non portabile: ' + ref)
        actual = Path(dependency['path']).resolve()
        if not actual.is_relative_to(Path(boundary).resolve()):
            raise ValueError('Blender: dipendenza fuori dal pacchetto: ' + ref)
    return {'file': Path(path).relative_to(boundary).as_posix(), 'status': 'passed',
            'check': 'blender_reopen', 'objects': len(info['objects']),
            'dependencies': len(info.get('dependencies', [])),
            'note': 'CLI nativa, geometria e risorse; qualità artistica e GUI non certificate'}


def inspect_ebook(path, boundary, *, native=True):
    """Native content-container checks, independent of a project's domain or role."""
    if not native:
        return {'file': Path(path).name, 'status': 'not_run', 'check': 'calibre_structure'}
    boundary = Path(boundary).resolve()
    result = subprocess.run(['calibre-cli', 'check', str(path)], cwd=boundary,
        env={**os.environ, 'ARTCRAFT_WORKSPACE_ROOT': str(boundary), 'ARTCRAFT_OUTPUT_DIR': str(boundary)},
        capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise ValueError('Calibre: controllo fallito: ' + (result.stderr or result.stdout)[-1200:])
    info = json.loads(result.stdout)
    if info.get('status') != 'passed' or not info.get('spine') or any(i.get('severity') == 'error' for i in info.get('issues', [])):
        raise ValueError('Calibre: struttura o risorse non valide')
    return {'file': Path(path).relative_to(boundary).as_posix(), 'status': 'passed',
            'check': 'calibre_structure', 'reading_order': len(info['spine']), 'resources': info.get('resources'),
            'warnings': info.get('issues', []), 'note': info.get('note', 'Controllo nativo; GUI e resa non provate')}


def inspect_freecad(path, boundary, *, native=True):
    """Actual native reopening; neither a STEP export nor a ZIP header is enough."""
    if not native:
        return {'file': Path(path).name, 'status': 'not_run', 'check': 'freecad_reopen'}
    boundary = Path(boundary).resolve()
    with tempfile.TemporaryDirectory(prefix='.freecad-proof-', dir=boundary) as temp:
        output = Path(temp) / 'inspection.json'
        result = subprocess.run(['freecad-cli', 'call', 'inspect', json.dumps({'input': str(path), 'output': str(output)})],
            cwd=boundary, env={**os.environ, 'ARTCRAFT_WORKSPACE_ROOT': str(boundary), 'ARTCRAFT_OUTPUT_DIR': temp},
            capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise ValueError('FreeCAD: riapertura fallita: ' + result.stderr[-1000:])
        info = json.loads(output.read_text())
    objects = info.get('objects', [])
    if not objects or any(o.get('invalid') or o.get('valid') is False for o in objects):
        raise ValueError('FreeCAD: documento vuoto, oggetti invalidi o solidi non validi')
    for reference in info.get('dependencies', []):
        ref = Path(reference)
        actual = (Path(path).parent / ref).resolve()
        if ref.is_absolute() or not actual.is_relative_to(boundary) or not actual.is_file():
            raise ValueError('FreeCAD: dipendenza mancante o non portabile: ' + reference)
    return {'file': Path(path).relative_to(boundary).as_posix(), 'status': 'passed', 'check': 'freecad_reopen',
            'objects': len(objects), 'dependencies': len(info.get('dependencies', [])),
            'note': 'Riapertura e geometria native; vincoli progettuali, GUI e conformità ingegneristica non certificate'}


def inspect_tree(folder, *, native=False, budget=None, depth=0):
    folder = Path(folder).resolve()
    projects, checks = [], []
    for path in sorted(folder.rglob('*.blend')):
        checks.append(inspect_blend(path, folder, native=native))
    for path in sorted(folder.rglob('*')):
        if path.suffix.lower() == '.fcstd':
            checks.append(inspect_freecad(path, folder, native=native))
        if path.suffix.lower() in ('.epub', '.azw3'):
            checks.append(inspect_ebook(path, folder, native=native))
        if path.suffix in NATIVE:
            value = document(path)
            scope = value.get('project', {}).get('items', {}) if path.suffix == '.fcproj' else value
            deps = [resolved_reference(path, ref, folder, portable=True) for _, _, ref in references(scope)]
            projects.append((path, value))
            checks.append({'file': path.relative_to(folder).as_posix(), 'dependencies': len(deps),
                           'status': 'passed', 'check': 'structure_and_dependencies'})
    # Nested archives are deliverables too: an intact top-level timeline does
    # not make a broken colleague source complete. Share extraction budget.
    for archive in sorted(folder.rglob('*.zip')):
        if depth >= 2:
            raise ValueError('Archivi troppo annidati: estrarre i sorgenti nel pacchetto')
        with tempfile.TemporaryDirectory(prefix='artcraft-nested-') as temp:
            extract(archive, Path(temp), budget)
            checks.extend({**c, 'file': archive.relative_to(folder).as_posix() + '/' + c['file']}
                          for c in inspect_tree(Path(temp), native=native, budget=budget, depth=depth+1))
    if native:
        # A different cwd reproduces the actual download/open failure.
        with tempfile.TemporaryDirectory(prefix='artcraft-unrelated-') as other:
            prepare(folder)
            for path, value in projects:
                if path.suffix == '.fcproj':
                    local = path.with_name(path.stem + '.locale.fcproj')
                    info = json.loads(run(['filmcraft-cli', '--project', local, 'inspect'], other))
                    media = json.loads(run(['filmcraft-cli', '--project', local, 'exec', 'media.status'], other))
                    if not info.get('sequence', {}).get('durationFrames') or any(m.get('status') != 'online' for m in media):
                        raise ValueError('FilmCraft: timeline vuota o media offline dopo il trasferimento')
                    duration = info['sequence']['duration'] / 254016000000
                    samples = []
                    for index, time in enumerate((0, duration * .5, max(0, duration - .1))):
                        frame = Path(other) / f'frame-{index}.png'
                        run(['filmcraft-cli', '--project', local, 'render', '--seconds', str(time),
                             '--out', str(frame), '--scale', '.25'], other)
                        samples.append({'seconds': time, 'luma': sample(frame)})
                    checks.append({'file': path.relative_to(folder).as_posix(), 'status': 'passed',
                        'check': 'filmcraft_render', 'duration': duration,
                        'width': info['sequence']['settings']['width'], 'height': info['sequence']['settings']['height'],
                        'samples': samples})
                elif path.suffix == '.ecproj':
                    run(['effectcraft-cli', '--project', path, 'info'], path.parent)
                else:
                    run(['soundcraft-cli', 'run', '--in', path, '--inspect'], path.parent)
                checks.append({'file': path.relative_to(folder).as_posix(), 'status': 'passed',
                               'check': 'native_reopen', 'app': path.suffix,
                               'note': 'FilmCraft: preparazione locale, media online e tre frame renderizzati; GUI non provata'
                               if path.suffix == '.fcproj' else 'CLI nativa; GUI non provata'})
    return checks


def verify_archive(archive, *, native=False):
    with tempfile.TemporaryDirectory(prefix='artcraft-relocated-') as temp:
        folder = Path(temp)
        budget = {'bytes': 0, 'files': 0}
        extract(archive, folder, budget)
        checks = inspect_tree(folder, native=native, budget=budget)
        status = 'passed' if all(c['status'] == 'passed' for c in checks) else 'not_run'
        if any(c['file'].endswith('.fcproj') for c in checks):
            helper = folder / 'PREPARA_SORGENTI.py'
            # Do not execute an untrusted generated helper, even if named alike.
            if not helper.is_file() or digest(helper) not in {digest(__file__), *RELEASED_PREPARERS}:
                raise ValueError('FilmCraft richiede il pacchetto preparato con source_packages.py pack: '
                                 'percorsi relativi da soli non sono riapribili da altre cartelle')
        return {'status': status, 'sha256': digest(archive), 'files': budget['files'], 'checks': checks,
                'coverage': 'CRC e inventario; dipendenze/struttura FilmCraft, EffectCraft, SoundCraft; '
                            'Blender: riapertura, geometria e dipendenze se native=True; '
                            'Calibre: struttura e risorse EPUB/AZW3 se native=True; '
                            'FreeCAD: riapertura, oggetti e geometria .FCStd se native=True; '
                            'altri formati richiedono la prova specifica della skill'}


def pack(project, destination, workspace):
    """Collect exact references; never guess a file by name or flatten sources."""
    project, destination, workspace = Path(project).resolve(), Path(destination).resolve(), Path(workspace).resolve()
    if project.suffix not in NATIVE or not project.is_relative_to(workspace) or not destination.is_relative_to(workspace):
        raise ValueError('Progetto o destinazione fuori dal workspace/formato supportato')
    value = document(project)
    scope = value.get('project', {}).get('items', {}) if project.suffix == '.fcproj' else value
    with tempfile.TemporaryDirectory(prefix='artcraft-pack-') as temp:
        folder = Path(temp)
        (folder / 'Media').mkdir()
        total, count = 0, 0
        for owner, key, ref in references(scope):
            source = resolved_reference(project, ref, workspace)
            total += source.stat().st_size
            count += 1
            if total > MAX_BYTES or count > MAX_FILES:
                raise ValueError('Dipendenze oltre il budget: suddividere il pacchetto')
            name = digest(source)[:16] + '-' + source.name
            shutil.copyfile(source, folder / 'Media' / name)
            owner[key] = 'Media/' + name
        (folder / project.name).write_text(json.dumps(value, ensure_ascii=False))
        shutil.copyfile(__file__, folder / 'PREPARA_SORGENTI.py')
        (folder / 'LEGGIMI.txt').write_text(
            'Estrarre TUTTO lo ZIP in una cartella. Non spostare il progetto da solo.\n'
            'FilmCraft 0.7.2: eseguire PREPARA_SORGENTI.py con Python 3, poi aprire il file .locale.fcproj '
            'generato, dalla app desktop FilmCraft compatibile con schema 15.\n'
            'Comando: python3 PREPARA_SORGENTI.py prepare .\n'
            'Windows: py PREPARA_SORGENTI.py prepare .\n'
            'La preparazione è offline, non installa software e non modifica gli originali. '
            'Se sposti la cartella, ripetila. In alternativa usa File > Link Media in FilmCraft '
            'e seleziona i media nella cartella Media.\n'
            'EffectCraft/SoundCraft: aprire il progetto con le risorse accanto. '
            'La verifica CLI non certifica app web o versioni GUI diverse.\n')
        (folder / 'CONTENUTO.json').write_text(json.dumps({'project': project.name,
            'files': [{'path': p.relative_to(folder).as_posix(), 'size': p.stat().st_size, 'sha256': digest(p)}
                      for p in sorted(folder.rglob('*')) if p.is_file()]}, ensure_ascii=False, indent=2))
        destination.parent.mkdir(parents=True, exist_ok=True)
        tempzip = destination.with_suffix('.partial')
        try:
            with zipfile.ZipFile(tempzip, 'w', zipfile.ZIP_DEFLATED) as z:
                for path in sorted(folder.rglob('*')):
                    if path.is_file():
                        z.write(path, path.relative_to(folder))
            verify_archive(tempzip, native=True)
            os.replace(tempzip, destination)
        finally:
            tempzip.unlink(missing_ok=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action')
    p = subs.add_parser('prepare'); p.add_argument('folder', nargs='?', default=str(Path(__file__).parent))
    p = subs.add_parser('verify'); p.add_argument('archive'); p.add_argument('--native', action='store_true')
    p = subs.add_parser('pack'); p.add_argument('project'); p.add_argument('destination'); p.add_argument('--workspace', default='/mnt/user-data')
    args = parser.parse_args()
    if args.action == 'pack':
        print(pack(args.project, args.destination, args.workspace))
    elif args.action == 'verify':
        print(json.dumps(verify_archive(args.archive, native=args.native), ensure_ascii=False))
    else:
        folder = getattr(args, 'folder', str(Path(__file__).parent))
        print('Apri questi progetti locali:', *prepare(folder), sep='\n')


if __name__ == '__main__':
    main()
