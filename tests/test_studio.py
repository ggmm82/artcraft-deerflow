import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['STUDIO_STATE'] = self.temp.name
        from studio import state
        self.state = importlib.reload(state)
        from studio import docker_runtime, login, router
        self.runtime = importlib.reload(docker_runtime)
        importlib.reload(login)
        self.router = importlib.reload(router)
        (self.state.STATE / 'installation-id').write_text('test-installation')

    def tearDown(self):
        self.temp.cleanup()

    def test_configurable_engines_persist_without_credentials(self):
        self.state.update_agent('gridcraft', {'engine': 'gemini', 'model': 'custom-model',
                                            'instructions': 'Usa euro', 'enabled': True})
        self.assertEqual(self.state.catalog()['gridcraft']['engine'], 'gemini')
        self.assertFalse(self.state.connection_status('gemini'))
        self.assertEqual(len(self.state.catalog()), 13)

    def test_invalid_engine_and_unknown_specialist_rejected(self):
        for identifier, engine in [('unknown', 'codex'), ('gridcraft', 'shell')]:
            with self.assertRaises(ValueError):
                self.state.update_agent(identifier, {'engine': engine})

    def test_volume_resolution_excludes_host_paths_and_traversal(self):
        self.runtime._mounts = [{'Destination': '/studio-state', 'Source': '/host/state'}]
        self.assertEqual(self.runtime.host_path('/studio-state/jobs/task.json'),
                         '/host/state/jobs/task.json')
        for path in ['/etc/passwd', '/studio-state/../etc/passwd']:
            with self.assertRaises(ValueError):
                self.runtime.host_path(path)

    def test_container_uses_one_thread_and_no_docker_socket(self):
        credentials = self.state.credential_dir('codex')
        (credentials / 'auth.json').write_text('{}')
        workspace = Path(self.temp.name) / 'workspace'
        captured = []
        class Result:
            returncode = 0
            stdout = '{"ok": true}'
            stderr = ''
        def execute(argv, **kwargs):
            captured.append(argv)
            return Result()
        with patch.object(self.runtime, 'host_path', side_effect=lambda p: '/host/' + Path(p).name), \
             patch.object(self.runtime.subprocess, 'run', side_effect=execute):
            result = self.runtime.delegate('gridcraft', 'Analizza il foglio', workspace)
        self.assertIn('true', result)
        argv = captured[0]
        self.assertIn('--memory=1536m', argv)
        self.assertIn('--cap-drop=ALL', argv)
        self.assertFalse(any('docker.sock' in arg for arg in argv))
        self.assertTrue(any('dst=/mnt/user-data' in arg for arg in argv))
        self.assertEqual(captured[-1][:3], ['docker', 'rm', '-f'])
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_worker_timeout_reclaims_container_and_releases_admission(self):
        import subprocess
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', side_effect=subprocess.TimeoutExpired('worker', 1)), \
             patch.object(self.runtime, 'remove') as remove:
            with self.assertRaisesRegex(RuntimeError, 'Timeout'):
                self.runtime.delegate('wordcraft', 'Crea documento', Path(self.temp.name) / 'work')
        remove.assert_called_once()
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_only_auth_files_are_copied_and_links_rejected(self):
        from studio.run_agent import copy_credentials
        source = Path(self.temp.name) / 'source'
        destination = Path(self.temp.name) / 'dest'
        source.mkdir()
        (source / 'auth.json').write_text('{}')
        (source / 'history.json').write_text('private history')
        copy_credentials(source, destination, 'codex')
        self.assertEqual(list(p.name for p in destination.iterdir()), ['auth.json'])
        (source / 'auth.json').unlink()
        (source / 'auth.json').symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):
            copy_credentials(source, destination, 'codex')

    def test_unconfirmed_cleanup_blocks_new_worker(self):
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        class Result:
            returncode = 0
            stdout = '{"ok":true}'
            stderr = ''
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', return_value=Result()), \
             patch.object(self.runtime, 'remove', side_effect=RuntimeError('cleanup failed')):
            with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
                self.runtime.delegate('gridcraft', 'Analizza', Path(self.temp.name) / 'work')
        self.assertTrue(self.runtime.EXECUTION_LOCK.locked())
        self.runtime.EXECUTION_LOCK.release()

    def test_browser_api_rejects_cross_origin_configuration(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        app = FastAPI()
        app.include_router(self.router.router)
        client = TestClient(app)
        payload = {'engine': 'gemini', 'model': '', 'instructions': '', 'enabled': True}
        response = client.put('/studio/api/agents/gridcraft', json=payload,
                              headers={'origin': 'https://other.example'})
        self.assertEqual(response.status_code, 403)
        response = client.put('/studio/api/agents/gridcraft', json=payload,
                              headers={'origin': 'http://testserver'})
        self.assertEqual(response.status_code, 200)
        catalog = client.get('/studio/api/catalog').json()
        self.assertNotIn('auth.json', json.dumps(catalog))
        self.assertEqual(catalog['agents']['gridcraft']['engine'], 'gemini')


if __name__ == '__main__':
    unittest.main()
