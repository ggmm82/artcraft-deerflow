#!/usr/bin/env python3
"""Scoped headless Blender CLI/MCP adapter. Each call opens a fresh process."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(os.environ.get('ARTCRAFT_WORKSPACE_ROOT', '/mnt/user-data')).resolve()
TOOLS = [
    {'name': 'blender.inspect', 'description': 'Reopen a .blend and inspect objects, animation and external dependencies.',
     'inputSchema': {'type': 'object', 'properties': {'project': {'type': 'string'}}, 'required': ['project'], 'additionalProperties': False}},
    {'name': 'blender.execute', 'description': 'Execute an explicit workspace Python script with bpy in a fresh Blender process. The script must save its results.',
     'inputSchema': {'type': 'object', 'properties': {'script': {'type': 'string'}}, 'required': ['script'], 'additionalProperties': False}},
    {'name': 'blender.render', 'description': 'Render one PNG frame from a saved .blend using its scene settings and CPU.',
     'inputSchema': {'type': 'object', 'properties': {'project': {'type': 'string'}, 'output': {'type': 'string'}, 'frame': {'type': 'integer'}}, 'required': ['project', 'output'], 'additionalProperties': False}},
    {'name': 'blender.export_glb', 'description': 'Export a saved scene to GLB; keep the .blend as the editable source.',
     'inputSchema': {'type': 'object', 'properties': {'project': {'type': 'string'}, 'output': {'type': 'string'}}, 'required': ['project', 'output'], 'additionalProperties': False}},
    {'name': 'blender.pack', 'description': 'Pack supported external assets into a new .blend without overwriting the input. Caches must be handled separately.',
     'inputSchema': {'type': 'object', 'properties': {'project': {'type': 'string'}, 'output': {'type': 'string'}}, 'required': ['project', 'output'], 'additionalProperties': False}},
]


def scoped(value, *, suffix=None, exists=True):
    path = Path(value).resolve()
    if not path.is_relative_to(ROOT) or (exists and not path.is_file()):
        raise ValueError('Percorso fuori dal workspace o file mancante: ' + str(value))
    if suffix and path.suffix.lower() != suffix:
        raise ValueError('Formato richiesto: ' + suffix)
    return path


def invoke(action, arguments):
    tool = next((t for t in TOOLS if t['name'] == 'blender.' + action), None)
    if not tool or not isinstance(arguments, dict):
        raise ValueError('Operazione Blender sconosciuta')
    schema = tool['inputSchema']
    if set(arguments) - set(schema['properties']) or set(schema['required']) - set(arguments):
        raise ValueError('Argomenti Blender mancanti o sconosciuti')
    for name, value in arguments.items():
        expected = int if name == 'frame' else str
        if type(value) is not expected:
            raise ValueError('Tipo argomento non valido: ' + name)
    job = {'action': action, 'workspace': str(ROOT)}
    for name in ('project', 'script'):
        if name in arguments:
            job[name] = str(scoped(arguments[name], suffix='.blend' if name == 'project' else '.py'))
    if 'output' in arguments:
        suffix = {'render': '.png', 'export_glb': '.glb', 'pack': '.blend'}[action]
        output = scoped(arguments['output'], suffix=suffix, exists=False)
        if output.exists():
            raise ValueError('Non sovrascrivo un output esistente: ' + str(output))
        output.parent.mkdir(parents=True, exist_ok=True)
        job['output'] = str(output)
    job['frame'] = arguments.get('frame')
    with tempfile.TemporaryDirectory(prefix='artcraft-blender-') as directory:
        folder = Path(directory)
        payload, result = folder / 'job.json', folder / 'result.json'
        job['result'] = str(result)
        payload.write_text(json.dumps(job))
        argv = ['blender', '--background', '--factory-startup', '--disable-autoexec',
                '--threads', '2', '--python-exit-code', '1', '--python',
                str(Path(__file__).resolve().with_name('blender_job.py')), '--', str(payload)]
        p = subprocess.run(argv, capture_output=True, text=True, timeout=1200, cwd=ROOT)
        if p.returncode or not result.is_file():
            raise RuntimeError('Blender non ha completato il lavoro: ' + (p.stderr + p.stdout)[-2500:])
        return json.loads(result.read_text())


def mcp():
    for line in sys.stdin:
        request = {}
        try:
            request = json.loads(line)
            if 'id' not in request:
                continue
            method = request.get('method')
            if method == 'initialize':
                result = {'protocolVersion': request.get('params', {}).get('protocolVersion', '2024-11-05'),
                          'capabilities': {'tools': {}}, 'serverInfo': {'name': 'artcraft-blender', 'version': '1.0'}}
            elif method == 'tools/list':
                result = {'tools': TOOLS}
            elif method == 'tools/call':
                params = request.get('params', {})
                name = params.get('name', '')
                if not name.startswith('blender.'):
                    raise ValueError('Tool Blender sconosciuto')
                value = invoke(name.removeprefix('blender.'), params.get('arguments', {}))
                result = {'content': [{'type': 'text', 'text': json.dumps(value, ensure_ascii=False)}]}
            elif method == 'ping':
                result = {}
            else:
                raise ValueError('Metodo MCP non supportato')
            response = {'jsonrpc': '2.0', 'id': request['id'], 'result': result}
        except Exception as error:
            response = {'jsonrpc': '2.0', 'id': request.get('id') if isinstance(request, dict) else None,
                        'error': {'code': -32603, 'message': str(error)[:3000]}}
        print(json.dumps(response, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='store_true')
    subs = parser.add_subparsers(dest='action')
    for name in ('commands', 'mcp'):
        subs.add_parser(name)
    p = subs.add_parser('inspect'); p.add_argument('project')
    p = subs.add_parser('execute'); p.add_argument('script')
    for name in ('render', 'pack', 'export_glb'):
        p = subs.add_parser(name); p.add_argument('project'); p.add_argument('output')
        if name == 'render':
            p.add_argument('--frame', type=int)
    args = parser.parse_args()
    if args.version:
        return subprocess.run(['blender', '--version']).returncode
    if args.action == 'mcp':
        mcp(); return 0
    if args.action == 'commands':
        print(json.dumps({'tools': TOOLS, 'session': 'stateless: save and reopen .blend between calls'})); return 0
    if not args.action:
        parser.print_help(); return 0
    values = {k: v for k, v in vars(args).items() if k not in ('action', 'version') and v is not None}
    print(json.dumps(invoke(args.action, values), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
