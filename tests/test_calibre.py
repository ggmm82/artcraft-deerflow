"""Calibre adapter contracts and runtime verification, independent of project domain."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import calibre_cli as cli
from scripts.install_artcraft import install_binaries
from studio.deliveries import build_delivery
from studio.source_packages import inspect_ebook, verify_archive


class CalibreTests(unittest.TestCase):
    def test_official_multi_binary_distribution_uses_declared_root_launchers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); destination = root / 'app'; links = root / 'links'; links.mkdir()
            (destination / 'bin').mkdir(parents=True)
            for name in ('ebook-convert', 'ebook-meta'):
                (destination / name).write_text('root launcher')
                (destination / 'bin' / name).write_text('bundled duplicate')
            app = {'executable': 'calibre-cli', 'binary': 'ebook-convert',
                   'binary_paths': {'ebook-convert': 'ebook-convert', 'ebook-meta': 'ebook-meta'}}
            self.assertEqual(install_binaries(app, destination, links), destination / 'ebook-convert')
            self.assertEqual((links / 'ebook-meta').resolve(), destination / 'ebook-meta')
            with self.assertRaisesRegex(RuntimeError, 'sovrascrivo'):
                install_binaries(app, destination, links)
            app['binary_paths'] = {'escape': '../outside'}
            (root / 'outside').write_text('outside')
            with self.assertRaisesRegex(RuntimeError, 'interno'):
                install_binaries(app, destination, links)
            self.assertFalse((links / 'escape').exists())

    def test_scope_inputs_no_overwrite_and_zip_paths(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(cli, 'ROOT', Path(temp)):
            root = Path(temp); source = root / 'input.txt'; source.write_text('original')
            with self.assertRaisesRegex(ValueError, 'workspace'):
                cli.invoke('inspect', {'input': '/etc/passwd'})
            with self.assertRaisesRegex(ValueError, 'sovrascrivo'):
                cli.invoke('convert', {'input': str(source), 'output': str(source)})
            (root / 'link.txt').symlink_to(source)
            with self.assertRaisesRegex(ValueError, 'link'):
                cli.invoke('convert', {'input': str(root / 'link.txt'), 'output': str(root / 'new.epub')})
            bad = root / 'bad.epub'
            with zipfile.ZipFile(bad, 'w') as z:
                z.writestr('../outside', 'unsafe')
            with self.assertRaisesRegex(ValueError, 'sicura'):
                cli.safe_book(bad)
            self.assertEqual(source.read_text(), 'original')

    def test_native_failure_exposes_exit_and_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(cli, 'ROOT', Path(temp)), patch.object(cli, 'environment', return_value=Path(temp)):
            source = Path(temp) / 'source.txt'; source.write_text('original')
            with patch.object(cli, 'supervise', return_value=(subprocess.CompletedProcess([], -11, 'crashed', ''), {})):
                with self.assertRaisesRegex(RuntimeError, 'exit -11'):
                    cli.invoke('convert', {'input': str(source), 'output': str(Path(temp) / 'out.pdf')})
            self.assertEqual(source.read_text(), 'original')

    def test_unpack_marker_prevents_silent_cross_format_repack(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(cli, 'ROOT', Path(temp)), patch.object(cli, 'environment', return_value=Path(temp)):
            root = Path(temp); sources = root / 'Sources'; sources.mkdir()
            (sources / '.artcraft-source.json').write_text(json.dumps({'format': '.epub'}))
            with patch.object(cli, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'formato originale'):
                    cli.invoke('pack', {'source': str(sources), 'output': str(root / 'bad.docx')})
                run.assert_not_called()
            with self.assertRaisesRegex(ValueError, 'argomenti'):
                cli.invoke('convert', {'input': 'a', 'output': 'b', 'arbitrary_args': '--unsafe'})

    def test_mcp_discovery_and_error_are_explicit(self):
        requests = [ {'id': 1, 'method': 'initialize'}, {'id': 2, 'method': 'tools/list'},
            {'id': 3, 'method': 'tools/call', 'params': {'name': 'calibre.inspect', 'arguments': {'input': '/outside.epub'}}} ]
        output = io.StringIO()
        with patch('sys.stdin', io.StringIO('\n'.join(map(json.dumps, requests)))), contextlib.redirect_stdout(output):
            cli.mcp()
        replies = list(map(json.loads, output.getvalue().splitlines()))
        self.assertEqual(len(replies[1]['result']['tools']), 8)
        self.assertEqual(replies[1]['result']['tools'][0]['name'], 'calibre.convert')
        self.assertIn('error', replies[2])

    def test_mcp_structural_failure_stops_batch_even_if_process_itself_succeeded(self):
        request = {'id': 1, 'method': 'tools/call', 'params': {'name': 'calibre.check', 'arguments': {'input': 'fixture'}}}
        output = io.StringIO()
        with patch('sys.stdin', io.StringIO(json.dumps(request))), contextlib.redirect_stdout(output), patch.object(cli, 'invoke', return_value={'status': 'failed', 'issues': [{'severity': 'error'}]}):
            cli.mcp()
        self.assertTrue(json.loads(output.getvalue())['result']['isError'])

    def test_delivery_ignores_model_reopen_claim_when_native_check_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); book = root / 'book.epub'; book.write_bytes(b'not valid')
            item = {'path': str(book), 'role': 'editable_source', 'reopen': {'status': 'passed'}}
            handoff = {'task': 'Any project', 'checks': [], 'delivery': {'source_status': 'included', 'source_note': '', 'files': [item]}}
            with patch('studio.source_packages.subprocess.run', return_value=subprocess.CompletedProcess([], 2, '', 'Missing referenced image')):
                result = build_delivery(handoff, root, agent='workspace', tools=['calibre'])
            self.assertEqual(result['technical_status'], 'needs_revision')
            self.assertIn('Missing referenced image', result['issues'][0])
            self.assertEqual(inspect_ebook(book, root, native=False)['status'], 'not_run')

    def test_relocated_archive_checks_native_resources_and_retains_warnings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); archive = root / 'Sources.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('book.epub', 'fixture; native result mocked explicitly')
            warning = {'severity': 'warning', 'message': 'Unused image'}
            def check(argv, **kwargs):
                relocated = Path(kwargs['cwd'])
                self.assertNotEqual(relocated, root)
                self.assertTrue((relocated / 'book.epub').is_file())
                self.assertEqual(kwargs['env']['ARTCRAFT_OUTPUT_DIR'], str(relocated))
                return subprocess.CompletedProcess(argv, 0, json.dumps({'status': 'passed', 'spine': [{'file': 'chapter.xhtml'}], 'resources': 3, 'issues': [warning]}), '')
            with patch('studio.source_packages.subprocess.run', side_effect=check):
                result = verify_archive(archive, native=True)
            self.assertEqual(result['status'], 'passed')
            self.assertEqual(result['checks'][0]['warnings'], [warning])
            self.assertEqual(verify_archive(archive, native=False)['status'], 'not_run')
