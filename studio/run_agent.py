"""Runs inside a disposable container. All tools act on this thread's files."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from .handoff import validate_handoff
except ImportError:  # Direct invocation inside the worker image.
    from handoff import validate_handoff

ALLOWED_AUTH = {
    'codex': ('auth.json',),
    'gemini': ('oauth_creds.json', 'google_accounts.json', 'settings.json'),
    'deepseek': ('api.json',),
}


def copy_credentials(source, destination, engine):
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    for filename in ALLOWED_AUTH[engine]:
        path = source / filename
        if path.is_symlink():
            raise ValueError('Link nelle credenziali non consentiti')
        if path.is_file():
            target = destination / filename
            if target.is_symlink():
                raise ValueError('Destinazione credenziali non valida')
            shutil.copyfile(path, target)
            target.chmod(0o600)


def command(engine, model, prompt, output):
    if engine == 'codex':
        args = ['codex', 'exec', '--json', '--skip-git-repo-check',
                '--dangerously-bypass-approvals-and-sandbox',
                '--output-last-message', str(output)]
        if model:
            args += ['--model', model]
        return args + ['-']
    if engine == 'gemini':
        args = ['gemini', '--approval-mode', 'yolo', '--output-format', 'json',
                '--skip-trust', '--include-directories', '/mnt/user-data']
        if model:
            args += ['--model', model]
        return args + ['--prompt', prompt]
    raise ValueError('Motore non valido')


def worker_error(engine, result):
    """Prefer structured CLI failures; never return a quoted system prompt."""
    if engine == 'codex':
        errors = []
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') == 'turn.failed':
                errors.append(str(event.get('error', {}).get('message', 'Turno Codex fallito')))
            elif event.get('type') == 'error':
                errors.append(str(event.get('message', 'Errore Codex')))
        if errors:
            return errors[-1][:1200]
    lines = (result.stderr or '').splitlines()
    important = [line for line in lines if any(word in line.lower() for word in ('error:', 'error ', 'failed', 'permission denied', 'unauthorized', 'unsupported'))]
    return ('\n'.join(important[-4:]) or '\n'.join(lines[:4]) or 'Worker terminato senza dettagli diagnostici')[:1200]


def handoff_error(output_dir, error):
    """Keep a failed delivery failed, but expose the recorded operational cause."""
    details = []
    try:
        path = output_dir / 'handoff.json'
        if not path.resolve().is_relative_to(output_dir.resolve()):
            return str(error)[:1800]
        manifest = json.loads(path.read_text())
        for check in manifest.get('checks', []):
            if isinstance(check, dict) and check.get('status') == 'failed':
                evidence = check.get('evidence')
                if isinstance(evidence, str):
                    details.append(evidence[:500])
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    return (str(error) + ('; ' + '; '.join(details[:3]) if details else ''))[:1800]


def main():
    job = json.loads(Path(sys.argv[1]).read_text())
    engine = job['engine']
    auth = Path('/root') / ('.' + engine)
    if engine != 'deepseek':
        copy_credentials(Path('/credentials'), auth, engine)
    output_dir = Path('/mnt/user-data/outputs') / job['agent'] / job['run_id']
    output_dir.mkdir(parents=True)
    (output_dir / 'work').mkdir()
    (output_dir / 'previews').mkdir()
    selected = []
    for name in job['skills']:
        if not name.startswith('artcraft-') or '/' in name or '..' in name:
            raise ValueError('Nome skill non valido')
        source = Path('/mnt/skills/custom') / name
        selected.append((source / 'SKILL.md').read_text())
        recipe = source / 'references/CLI-RECIPE.md'
        if recipe.is_file():
            selected.append(recipe.read_text())
        # Native skill discovery for either CLI, scoped to this disposable run.
        if engine != 'deepseek':
            skills_root = Path('/root/.agents/skills') if engine == 'codex' else auth / 'skills'
            target = skills_root / name
            shutil.copytree(source, target, dirs_exist_ok=True)
    # Only the selected specialist's instructions and common procedure enter context.
    prompt = '\n\n'.join([
        'Sei lo specialista ' + job['agent'] + '. Lavora in italiano.',
        'Le skill aggiuntive sono procedure di supporto: non cambiano il tuo ruolo '
        'né i requisiti dell’incarico.',
        'Gli strumenti ArtCraft sono già installati. Usa craft help, craft commands e craft tools '
        'per scoprire i comandi della release reale. Non installare software. '
        'Python: /usr/bin/python3 (non python). CLI native e craft: /usr/local/bin; '
        'non usare /opt/artcraft/bin, che non esiste.',
        'Questa è una sandbox Docker. Non delegare e non pubblicare nulla. '
        'Non leggere o modificare credenziali, /credentials, .codex, .gemini o .deepseek.',
        'Input e risultati degli altri specialisti: /mnt/user-data. '
        'Non sovrascrivere gli input. Salva i tuoi risultati in ' + str(output_dir) + '.',
        'La variabile ARTCRAFT_OUTPUT_DIR indica questa cartella. Scrivi qui handoff.json '
        'secondo lo schema artcraft-workspace, incluso delivery obbligatorio per ogni output; '
        'il runtime verifica file e metadati. Consegna anche il sorgente modificabile '
        'riaperto nell’app reale, con dipendenze necessarie. Un export o un viewer '
        'non dimostra compatibilità con l’app dello specialista. Se impossibile, '
        'dichiara source_status unavailable, motivo e limiti senza fingere un sorgente.',
        *selected, job['instructions'],
        'Incarico del coordinatore:\n' + job['task'],
        'Vincolo di consegna: i percorsi di output proposti nell’incarico sono nomi desiderati, '
        'non cambiano la cartella assegnata. Salva tutti i file prodotti e handoff.json in '
        + str(output_dir) + '. Restituisci al coordinatore i percorsi effettivi in questa cartella.',
        'Restituisci percorsi assoluti, verifiche effettuate e limiti. '
        'Non dichiarare verifiche visive/audio che non hai eseguito.'
    ])
    final = Path('/tmp/last-message.txt')
    try:
        if engine == 'deepseek':
            try:
                from .deepseek import run
            except ImportError:
                from deepseek import run
            os.environ['ARTCRAFT_OUTPUT_DIR'] = str(output_dir)
            message = run(job['model'], prompt, output_dir, job['timeout'])
        else:
            result = subprocess.run(command(engine, job['model'], prompt, final), cwd=output_dir,
                                input=prompt if engine == 'codex' else None,
                                env={**os.environ, 'ARTCRAFT_OUTPUT_DIR': str(output_dir)},
                                capture_output=True, text=True, timeout=job['timeout'])
            if result.returncode:
                print(json.dumps({'ok': False, 'engine': engine, 'agent': job['agent'],
                              'exit_code': result.returncode,
                              'error': worker_error(engine, result)}))
                return result.returncode
            if engine == 'codex':
                message = final.read_text() if final.exists() else result.stdout
            else:
                parsed = json.loads(result.stdout)
                if parsed.get('error'):
                    raise RuntimeError(str(parsed['error']))
                message = parsed.get('response', '')
        try:
            handoff = validate_handoff(output_dir, Path('/mnt/user-data'), require_delivery=True)
        except ValueError as exc:
            print(json.dumps({'ok': False, 'agent': job['agent'], 'engine': engine,
                              'output_dir': str(output_dir),
                              'error': handoff_error(output_dir, exc)}, ensure_ascii=False))
            return 1
        print(json.dumps({'ok': True, 'agent': job['agent'], 'engine': engine,
                          'output_dir': str(output_dir), 'handoff': handoff,
                          'response': message}, ensure_ascii=False))
        return 0
    finally:
        # One worker at a time. Preserve refreshed tokens for the next run.
        if engine != 'deepseek':
            copy_credentials(auth, Path('/credentials'), engine)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)[-2000:]}))
        sys.exit(1)
