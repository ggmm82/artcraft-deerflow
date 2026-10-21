"""Real Docker proof that a workspace role cannot run disabled native CLIs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def inside():
    import os
    installed = {a['id']: a for a in json.loads(Path('/opt/artcraft/installed.json').read_text())}
    disabled = {'blender', 'cadcraft', 'ffmpeg', 'freecad'}
    for identifier in disabled:
        command = installed[identifier]['binary']
        if identifier in ('blender', 'cadcraft'):
            assert not Path(command).exists(), identifier + ' bundle remains exposed'
        try:
            result = subprocess.run([command, '-version' if identifier == 'ffmpeg' else '--version'], capture_output=True, timeout=15)
        except (FileNotFoundError, PermissionError):
            assert identifier in ('blender', 'cadcraft')
            continue
        assert result.returncode == 126 and b'Disabled native capability' in result.stderr, identifier + ' was not blocked by the policy'
    probe = subprocess.run(['/usr/bin/ffprobe', '-version'], capture_output=True)
    assert probe.returncode == 126 and b'Disabled native capability' in probe.stderr
    for command in (['craft', 'list'], ['craft', 'capabilities']):
        records = json.loads(subprocess.check_output(command, text=True))
        assert not disabled & {r['id'] for r in records}
        assert 'typst' in {r['id'] for r in records}
    for identifier in disabled:
        result = subprocess.run(['craft', 'commands', identifier], capture_output=True, timeout=15)
        assert result.returncode != 0, identifier + ' bypassed craft policy'
    # FreeCAD is also callable as a Python module, not only as an executable.
    code = "import sys,importlib.util;sys.path[:0]=['/usr/lib/freecad-python3/lib','/usr/lib/freecad/lib'];assert importlib.util.find_spec('FreeCAD') is None"
    assert subprocess.run(['/usr/bin/python3', '-c', code], capture_output=True).returncode == 0
    assert not Path('/mnt/skills/custom/artcraft-blender/SKILL.md').exists()
    assert subprocess.run(['typst', '--version'], capture_output=True).returncode == 0
    print('Worker policy OK: empty-tools workspace, absolute binaries, FreeCAD Python API, CLI catalogs and active tool isolation')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--inside', action='store_true')
    parser.add_argument('--image', default='artcraft-deerflow-sandbox:0.1.0'); args = parser.parse_args()
    if args.inside:
        inside(); return
    root = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(root))
    from studio.capability_policy import policy_from_names, worker_arguments
    from studio.state import applications
    disabled = {'blender', 'cadcraft', 'ffmpeg', 'freecad'}
    policy = policy_from_names({'artcraft-' + a['id'] for a in applications() if a['id'] not in disabled})
    with tempfile.TemporaryDirectory(prefix='worker-policy-') as folder:
        path = Path(folder); blocker = path / 'disabled'
        blocker.write_text('#!/bin/sh\necho "Disabled native capability" >&2\nexit 126\n'); blocker.chmod(0o755)
        job = path / 'job.json'
        job.write_text(json.dumps({'agent': 'workspace', 'role': {'tools': []}, 'capability_policy': policy}))
        subprocess.run(['docker', 'run', '--rm', '--network=none', '--cap-drop=ALL', '--security-opt=no-new-privileges',
            *worker_arguments(policy, blocker), '--mount', f'type=bind,src={root},dst=/review,readonly',
            '--mount', f'type=bind,src={job},dst=/job.json,readonly', '--entrypoint', 'python3', args.image,
            '/review/scripts/check_worker_capabilities.py', '--inside'], check=True)


if __name__ == '__main__': main()
