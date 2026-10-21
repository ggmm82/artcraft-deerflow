"""Adapter protocol, install boundaries and delivery acceptance regressions."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import toolkit_cli as cli
from scripts.install_artcraft import safe_unzip
from scripts.toolkit_specs import TOOLS
from studio.source_packages import inspect_freecad

REPO = Path(__file__).resolve().parents[1]


class ToolkitTests(unittest.TestCase):
    def test_every_new_adapter_can_negotiate_mcp_without_native_processes(self):
        # Discovery must work before opening any project or importing heavy apps.
        for app in TOOLS:
            with self.subTest(app=app):
                messages = [{'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2024-11-05'}},
                            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'other.execute', 'arguments': {}}},
                            {'jsonrpc': '2.0', 'id': 4, 'method': 'ping'}]
                result = subprocess.run([sys.executable, str(REPO / 'scripts/toolkit_cli.py'), '--app', app, 'mcp'],
                    input='\n'.join(json.dumps(m) for m in messages) + '\n', capture_output=True, text=True, timeout=10, check=True)
                replies = [json.loads(line) for line in result.stdout.splitlines()]
                self.assertEqual(replies[0]['result']['protocolVersion'], '2024-11-05')
                self.assertEqual(replies[1]['result']['tools'], TOOLS[app])
                self.assertIn('error', replies[2])
                self.assertEqual(replies[3]['result'], {})

    def test_external_input_existing_output_and_bad_args_do_not_start_native_jobs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);source = root / 'source.typ';source.write_text('Content')
            existing = root / 'existing.pdf';existing.write_bytes(b'original')
            with patch.object(cli, 'ROOT', root), patch.object(cli, 'run') as run:
                for args in ({'input': '/etc/passwd', 'output': str(root / 'outside.pdf')},
                             {'input': str(source), 'output': str(existing)},
                             {'input': str(source), 'output': str(root / 'x.pdf'), 'invented_option': True}):
                    with self.assertRaises(ValueError): cli.invoke('typst', 'compile', args)
                link = root / 'escape';link.symlink_to('/etc', target_is_directory=True)
                with self.assertRaises(ValueError):cli.scoped(str(link / 'passwd'))
                with self.assertRaises(ValueError):
                    cli.invoke('playwright', 'screenshot', {'url': 'file:///etc/passwd', 'output': str(root / 'x.png')})
                for width in (True, 1, 100000):
                    with self.assertRaises(ValueError):
                        cli.invoke('playwright', 'screenshot', {'url': 'https://example.com', 'output': str(root / 'x.png'), 'width': width})
                run.assert_not_called()
                self.assertEqual(existing.read_bytes(), b'original')

    def test_zip_distribution_rejects_escape_and_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('../escape', '/absolute', 'dir\\escape', 'link'):
                archive = root / 'unsafe.zip'
                with zipfile.ZipFile(archive, 'w') as z:
                    info = zipfile.ZipInfo(name)
                    if name == 'link':info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    z.writestr(info, '/etc/passwd')
                with self.assertRaises(ValueError):safe_unzip(archive, root / 'extract')
            with zipfile.ZipFile(root / 'good.zip', 'w') as z:z.writestr('epubcheck/lib/test.jar', b'actual payload')
            safe_unzip(root / 'good.zip', root / 'safe')
            self.assertEqual((root / 'safe/epubcheck/lib/test.jar').read_bytes(), b'actual payload')

    def test_freecad_delivery_needs_actual_objects_valid_geometry_and_portable_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);project = root / 'model.FCStd';project.write_bytes(b'fixture')
            def inspect(info):
                def execute(argv, **kwargs):
                    output = Path(json.loads(argv[-1])['output']);output.write_text(json.dumps(info))
                    return subprocess.CompletedProcess(argv, 0, '', '')
                with patch('studio.source_packages.subprocess.run', side_effect=execute):
                    return inspect_freecad(project, root)
            self.assertEqual(inspect_freecad(project, root, native=False)['status'], 'not_run')
            for value in ({'objects': []}, {'objects': [{'valid': False}]}, {'objects': [{'invalid': True}]},
                          {'objects': [{'valid': True}], 'dependencies': ['/etc/passwd']},
                          {'objects': [{'valid': True}], 'dependencies': ['missing.step']}):
                with self.assertRaises(ValueError):inspect(value)
            (root / 'asset.step').write_text('dependency')
            result = inspect({'objects': [{'valid': True}], 'dependencies': ['asset.step']})
            self.assertEqual(result['status'], 'passed');self.assertEqual(result['dependencies'], 1)


if __name__ == '__main__':unittest.main()
