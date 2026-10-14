"""Runs inside a disposable container. All tools act on this thread's files."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ALLOWED_AUTH = {
    'codex': ('auth.json',),
    'gemini': ('oauth_creds.json', 'google_accounts.json', 'settings.json'),
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
        args = ['codex', 'exec', '--skip-git-repo-check',
                '--dangerously-bypass-approvals-and-sandbox',
                '--output-last-message', str(output)]
        if model:
            args += ['--model', model]
        return args + [prompt]
    if engine == 'gemini':
        args = ['gemini', '--approval-mode', 'yolo', '--output-format', 'json']
        if model:
            args += ['--model', model]
        return args + ['--prompt', prompt]
    raise ValueError('Motore non valido')


def main():
    job = json.loads(Path(sys.argv[1]).read_text())
    engine = job['engine']
    auth = Path('/root') / ('.codex' if engine == 'codex' else '.gemini')
    copy_credentials(Path('/credentials'), auth, engine)
    output_dir = Path('/mnt/user-data/outputs') / job['agent'] / job['run_id']
    output_dir.mkdir(parents=True)
    workspace = Path('/mnt/user-data/workspace')
    workspace.mkdir(exist_ok=True)
    Path('/mnt/user-data/work').mkdir(exist_ok=True)
    specific = Path('/mnt/skills/custom') / ('artcraft-' + job['agent']) / 'SKILL.md'
    common = Path('/mnt/skills/custom/artcraft-workspace/SKILL.md')
    # Only the selected specialist's instructions and common procedure enter context.
    prompt = '\n\n'.join([
        'Sei lo specialista ' + job['agent'] + '. Lavora in italiano.',
        'Gli strumenti ArtCraft sono già installati. Usa craft help, craft commands e craft tools '
        'per scoprire i comandi della release reale. Non installare software.',
        'Questa è una sandbox Docker. Non delegare e non pubblicare nulla. '
        'Non leggere o modificare credenziali, .codex o .gemini.',
        'Input e risultati degli altri specialisti: /mnt/user-data. '
        'Non sovrascrivere gli input. Salva i tuoi risultati in ' + str(output_dir) + '.',
        common.read_text(), specific.read_text(), job['instructions'],
        'Incarico del coordinatore:\n' + job['task'],
        'Restituisci percorsi assoluti, verifiche effettuate e limiti. '
        'Non dichiarare verifiche visive/audio che non hai eseguito.'
    ])
    final = Path('/tmp/last-message.txt')
    try:
        result = subprocess.run(command(engine, job['model'], prompt, final), cwd=workspace,
                                capture_output=True, text=True, timeout=job['timeout'])
        if result.returncode:
            print(json.dumps({'ok': False, 'engine': engine, 'agent': job['agent'],
                              'error': (result.stderr or result.stdout)[-2500:]}))
            return result.returncode
        if engine == 'codex':
            message = final.read_text() if final.exists() else result.stdout
        else:
            parsed = json.loads(result.stdout)
            if parsed.get('error'):
                raise RuntimeError(str(parsed['error']))
            message = parsed.get('response', '')
        print(json.dumps({'ok': True, 'agent': job['agent'], 'engine': engine,
                          'output_dir': str(output_dir), 'response': message}, ensure_ascii=False))
        return 0
    finally:
        # One worker at a time. Preserve refreshed tokens for the next run.
        copy_credentials(auth, Path('/credentials'), engine)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)[-2000:]}))
        sys.exit(1)
