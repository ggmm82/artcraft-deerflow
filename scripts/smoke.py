#!/usr/bin/env python3
"""Controlli reali sulle CLI installate. --render aggiunge export di prova."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile


def run(command, timeout=120):
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {'command': command, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'command': command, 'returncode': -1, 'stdout': '', 'stderr': str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--mcp', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('/tmp/artcraft-checks.json'))
    args = parser.parse_args()
    root = Path(os.environ.get('ARTCRAFT_INSTALL_ROOT', '/opt/artcraft'))
    lock = json.loads((root / 'versions.lock.json').read_text())
    checks = []
    for app in lock['applications']:
        reference = root / 'reference' / app['id']
        reference.mkdir(parents=True, exist_ok=True)
        version = run([app['executable'], '--version'])
        version['ok'] = version['returncode'] == 0 and app['version'].removeprefix('v') in version['stdout']
        checks.append(version)
        help_result = run([app['executable'], '--help'])
        help_text = help_result['stdout'] + help_result['stderr']
        # DeckCraft v0.7.0 prints usage and exits 1 on --help; it is not a linkage error.
        help_result['ok'] = help_result['returncode'] in (0, 1, 2) and ('usage' in help_text.lower() or app['executable'] in help_text)
        checks.append(help_result)
        (reference / 'help.txt').write_text(help_text, encoding='utf-8')
        registry = run([app['executable'], *app['registry_args']])
        registry['ok'] = registry['returncode'] == 0 and bool(registry['stdout'].strip())
        (reference / 'commands.txt').write_text(registry['stdout'], encoding='utf-8')
        checks.append(registry)
        if args.mcp:
            Path('/mnt/user-data').mkdir(parents=True, exist_ok=True)
            mcp = run(['craft', 'tools', app['id'], '--out', str(reference / 'mcp-tools.json')], timeout=210)
            mcp['ok'] = mcp['returncode'] == 0
            checks.append(mcp)
    if args.render:
        with tempfile.TemporaryDirectory(prefix='artcraft-render-') as directory:
            d = Path(directory)
            (d / 'input.txt').write_text('Prova ArtCraft\nDocumento di verifica in italiano.\n', encoding='utf-8')
            tasks = [
                (['gridcraft-cli', 'eval', '=SUM(1,2,3)'], None),
                (['wordcraft-cli', 'convert', str(d/'input.txt'), str(d/'documento.docx')], d/'documento.docx'),
                (['wordcraft-cli', 'convert', str(d/'documento.docx'), str(d/'documento.pdf')], d/'documento.pdf'),
                (['pdfcraft-cli', 'info', str(d/'documento.pdf')], None),
                (['deckcraft-cli', 'render', '--sample', '--slide', '1', str(d/'slide.png')], d/'slide.png'),
                (['cadcraft-cli', 'run', '--sample', '--save', str(d/'disegno.dxf')], d/'disegno.dxf'),
            ]
            for command, expected in tasks:
                result = run(command, timeout=180)
                result['ok'] = result['returncode'] == 0 and (expected is None or (expected.is_file() and expected.stat().st_size > 0))
                if command[:2] == ['gridcraft-cli', 'eval']:
                    result['ok'] = result['ok'] and result['stdout'].strip() == '6'
                checks.append(result)
    report = {'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'passed': all(x['ok'] for x in checks), 'checks': checks}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for c in checks:
        print(('OK' if c['ok'] else 'FAIL'), ' '.join(c['command']))
        if not c['ok']:
            print(c['stderr'][-2000:])
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
