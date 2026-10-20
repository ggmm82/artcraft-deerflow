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
        from studio import runtime_settings
        host = patch.object(runtime_settings, 'capacity', return_value={'cpus': 4, 'memory_mib': 8192, 'detected': True})
        host.start()
        self.addCleanup(host.stop)
        importlib.reload(login)
        self.router = importlib.reload(router)
        (self.state.STATE / 'installation-id').write_text('test-installation')

    def tearDown(self):
        self.temp.cleanup()

    def connect_antigravity(self):
        root = self.state.credential_dir('gemini')
        (root / 'antigravity-cli').mkdir(exist_ok=True)
        (root / 'antigravity-cli/antigravity-oauth-token').write_text('fixture-native-token')
        (root / 'antigravity-account.json').write_text('{}')

    def test_configurable_engines_persist_without_credentials(self):
        self.state.update_agent('gridcraft', {'engine': 'gemini', 'model': 'custom-model',
                                            'instructions': 'Usa euro', 'enabled': True,
                                            'skills': ['artcraft-vectorcraft']})
        self.assertEqual(self.state.catalog()['gridcraft']['engine'], 'gemini')
        self.assertIn('artcraft-vectorcraft', self.state.catalog()['gridcraft']['skills'])
        self.assertIn('artcraft-gridcraft', self.state.catalog()['gridcraft']['skills'])
        self.assertFalse(self.state.connection_status('gemini'))
        self.assertEqual(set(self.state.catalog()), {app['id'] for app in self.state.applications()})

    def test_codex_payload_matches_current_cli_contract(self):
        from studio.codex_compat import modernize_codex_payload
        original = {'model': 'gpt-5.4', 'tools': [{'type': 'function'}]}
        payload = modernize_codex_payload(original)
        self.assertEqual(payload['tool_choice'], 'auto')
        self.assertTrue(payload['parallel_tool_calls'])
        self.assertEqual(payload['include'], ['reasoning.encrypted_content'])
        self.assertNotIn('tool_choice', original)

    def test_existing_config_is_migrated_without_changing_model(self):
        from studio import bootstrap
        bootstrap = importlib.reload(bootstrap)
        path = self.state.STATE / 'config.yaml'
        path.write_text('models:\n- name: studio-codex\n  use: deerflow.models.openai_codex_provider:CodexChatModel\n  model: personal-model\n')
        os.environ['STUDIO_PASSWORD'] = 'test-password-at-least-16-characters'
        with patch.object(bootstrap, 'catalog', return_value={}):
            bootstrap.initialize()
        config = __import__('yaml').safe_load(path.read_text())
        self.assertEqual(config['models'][0]['use'], 'studio.codex_provider:StudioCodexChatModel')
        self.assertEqual(config['models'][0]['model'], 'personal-model')

    def test_invalid_engine_and_unknown_specialist_rejected(self):
        for identifier, engine in [('unknown', 'codex'), ('gridcraft', 'shell')]:
            with self.assertRaises(ValueError):
                self.state.update_agent(identifier, {'engine': engine})

    def test_skill_paths_cannot_escape_the_catalog(self):
        with self.assertRaisesRegex(ValueError, 'Skill sconosciuta'):
            self.state.update_agent('gridcraft', {'engine': 'codex',
                                                'skills': ['../../credentials']})

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
        from studio import runtime_settings
        limits = {'cpus': 2, 'memory_mib': 3072, 'tmp_mib': 768, 'threads': 2}
        captured = []
        class Result:
            returncode = 0
            stdout = '{"ok": true}'
            stderr = ''
        def execute(argv, **kwargs):
            captured.append(argv)
            return Result()
        with patch.object(self.runtime, 'host_path', side_effect=lambda p: '/host/' + Path(p).name), \
             patch.object(self.runtime.subprocess, 'run', side_effect=execute), \
             patch.object(runtime_settings, 'effective', return_value=limits):
            result = self.runtime.delegate('gridcraft', 'Analizza il foglio', workspace)
        self.assertIn('true', result)
        argv = next(a for a in captured if a[:2] == ['docker', 'run'])
        self.assertIn('--memory=3072m', argv)
        self.assertIn('--cpus=2', argv)
        self.assertIn('ARTCRAFT_CPU_THREADS=2', argv)
        self.assertIn('--cap-drop=ALL', argv)
        self.assertFalse(any('docker.sock' in arg for arg in argv))
        self.assertTrue(any('dst=/mnt/user-data' in arg for arg in argv))
        self.assertEqual(captured[-1][:3], ['docker', 'rm', '-f'])
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_dynamic_role_and_selected_cli_skills_enter_actual_worker_payload(self):
        from studio import projects
        from studio.project_skills import load_compiled
        from test_project_skills import role
        credentials = self.state.credential_dir('codex')
        (credentials / 'auth.json').write_text('{}')
        workspace = Path(self.temp.name) / 'workspace'
        projects.create_plan(workspace, 'Progetto con vincoli', [])
        projects.sync_acceptance(workspace, ['Vincoli effettivi del progetto'])
        spec = role(); spec['tools'] = ['cadcraft', 'gridcraft']
        projects.sync_project_context(workspace, [spec], {'decisione': 'Confrontare alternative'})
        project = projects.read_project(workspace); compiled = project['roles'][0]
        captured = []
        def execute(argv, **kwargs):
            if argv[:2] == ['docker', 'run']:
                payload = json.loads(next((self.state.STATE / 'jobs').glob('*.json')).read_text())
                captured.append(payload)
            return type('Result', (), {'returncode': 0, 'stdout': '{"ok":true}', 'stderr': ''})()
        with patch.object(self.runtime, 'host_path', return_value='/host/fixture'), \
             patch.object(self.runtime.subprocess, 'run', side_effect=execute):
            self.runtime.delegate('workspace', 'Confronta alternative', workspace, role=compiled, acceptance=project['acceptance'])
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]['compiled_skill'], load_compiled(workspace, compiled))
        self.assertEqual(captured[0]['skills'], ['artcraft-workspace', 'artcraft-cadcraft', 'artcraft-gridcraft'])
        self.assertEqual(captured[0]['model'], self.state.team()['model'])
        self.assertEqual(captured[0]['engine'], self.state.team()['engine'])
        with self.assertRaisesRegex(ValueError, 'richiesta corrente'):
            self.runtime.delegate('workspace', 'Incarico obsoleto', workspace, role=compiled, acceptance={'hash': 'changed'})
        self.state.update_agent('cadcraft', {'engine': 'inherit', 'enabled': False})
        with self.assertRaisesRegex(ValueError, 'disabilitato'):
            self.runtime.delegate('workspace', 'Incarico', workspace, role=compiled, acceptance=project['acceptance'])

    def test_gemini_coordinator_has_no_workspace_and_cleans_up_before_delegation(self):
        self.connect_antigravity()
        captured = []
        def execute(args, **kwargs):
            captured.append(args)
            job = next((self.state.STATE / 'jobs').glob('*.json'))
            self.assertEqual(json.loads(job.read_text())['model'], 'gemini-2.5-pro')
            return type('Result', (), {'returncode': 0, 'stdout': '{"ok":true,"response":{"candidates":[]}}'})()
        with patch.object(self.runtime, 'host_path', return_value='/host/private'), \
             patch.object(self.runtime.subprocess, 'run', side_effect=execute), patch.object(self.runtime, 'remove'):
            result = self.runtime.generate_gemini({'model': 'gemini-2.5-pro', 'contents': []})
        self.assertEqual(result, {'candidates': []})
        self.assertFalse(any('dst=/mnt/user-data' in arg or 'docker.sock' in arg for arg in captured[0]))
        self.assertTrue(any('dst=/credentials' in arg for arg in captured[0]))
        self.assertFalse(list((self.state.STATE / 'jobs').glob('*.json')))
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_gemini_provider_errors_are_sanitized_and_release_admission(self):
        self.connect_antigravity()
        result = type('Result', (), {'returncode': 1, 'stdout': '{"ok":false,"error":"fixture-private-token"}'})()
        with patch.object(self.runtime, 'host_path', return_value='/host/private'), \
             patch.object(self.runtime.subprocess, 'run', return_value=result), patch.object(self.runtime, 'remove'):
            with self.assertRaisesRegex(RuntimeError, 'Antigravity non disponibile') as failure:
                self.runtime.generate_gemini({'model': 'gemini-2.5-pro'})
        self.assertNotIn('fixture-private-token', str(failure.exception))
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_worker_timeout_reclaims_container_and_releases_admission(self):
        import subprocess
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', side_effect=subprocess.TimeoutExpired('worker', 1)), \
             patch.object(self.runtime, 'remove') as remove:
            result = json.loads(self.runtime.delegate('wordcraft', 'Crea documento', Path(self.temp.name) / 'work'))
            self.assertFalse(result['ok'])
            self.assertTrue(result['partial'])
            self.assertIn('/mnt/user-data/outputs/wordcraft/artcraft-job-', result['output_dir'])
            self.assertIn('checkpoint', result['resume'])
        remove.assert_called_once()
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())
        from studio.progress import list_jobs
        status = list_jobs(Path(self.temp.name) / 'work')[0]
        self.assertTrue(status['resources_reclaimed'])
        self.assertTrue(status['cleanup_started_at'])
        self.assertTrue(status['cleanup_finished_at'])

    def test_cancelled_queued_job_cannot_start_or_stop_an_unrelated_worker(self):
        import threading
        from studio.cancellation import CURRENT
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        event = threading.Event(); event.set()
        token = CURRENT.set(event)
        self.runtime.EXECUTION_LOCK.acquire()
        try:
            with patch.object(self.runtime.subprocess, 'run') as run:
                result = json.loads(self.runtime.delegate('wordcraft','Queued',Path(self.temp.name)/'work'))
                self.assertFalse(result['ok'])
                run.assert_not_called()
            self.assertTrue(self.runtime.EXECUTION_LOCK.locked())
        finally:
            self.runtime.EXECUTION_LOCK.release()
            CURRENT.reset(token)

    def test_stop_of_owned_queued_job_never_inspects_or_stops_the_active_container(self):
        from studio.progress import create_job, read_status
        workspace=Path(self.temp.name)/'queued-chat'
        progress=create_job(workspace,'artcraft-job-123456abcdef','workspace','codex','test')
        with patch.object(self.runtime,'docker') as docker:
            result=self.runtime.request_stop(workspace,'artcraft-job-123456abcdef')
        self.assertTrue(result['queued'])
        self.assertTrue(read_status(progress)['cancel_requested'])
        docker.assert_not_called()

    def test_run_cancellation_stops_its_label_checked_docker_worker_and_reclaims_resources(self):
        import asyncio, threading
        from types import SimpleNamespace
        from studio.cancellation import call
        from studio.progress import list_jobs, workspace_key
        workspace = Path(self.temp.name)/'work'
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        ready, stopped = threading.Event(), threading.Event()
        def execute(args, **kwargs):
            name = args[args.index('--name')+1]
            output = workspace/'outputs/wordcraft'/name
            output.mkdir(parents=True); (output/'saved.txt').write_text('keep')
            ready.set()
            self.assertTrue(stopped.wait(3), 'Docker worker was left running')
            return SimpleNamespace(returncode=1,stdout='',stderr='worker stopped')
        def docker(*args, **kwargs):
            if args[0]=='inspect':
                return json.dumps({'Config':{'Labels':{'org.artcraft.studio.installation':'test-installation','org.artcraft.studio.workspace':workspace_key(workspace)}},'State':{'Running':True}})
            self.assertEqual(args[:3],('stop','--time','10'))
            stopped.set(); return ''
        async def scenario():
            task = asyncio.create_task(call(self.runtime.delegate,'wordcraft','Create',workspace))
            for _ in range(100):
                if ready.is_set(): break
                await asyncio.sleep(.01)
            self.assertTrue(ready.is_set())
            task.cancel()
            with self.assertRaises(asyncio.CancelledError): await asyncio.wait_for(task,4)
        with patch.object(self.runtime,'host_path',return_value='/host/path'), \
             patch.object(self.runtime.subprocess,'run',side_effect=execute), \
             patch.object(self.runtime,'docker',side_effect=docker), \
             patch.object(self.runtime,'remove') as remove:
            asyncio.run(scenario())
        remove.assert_called_once()
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())
        self.assertEqual(next((workspace/'outputs').rglob('saved.txt')).read_text(),'keep')
        status = list_jobs(workspace)[0]
        self.assertTrue(status['cancel_requested'])
        self.assertTrue(status['resources_reclaimed'])
        self.assertEqual(status['error_code'],'work_cancelled')

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
        from studio.progress import list_jobs
        status = list_jobs(Path(self.temp.name) / 'work')[0]
        self.assertTrue(status['cleanup_error'])
        self.assertFalse(status['resources_reclaimed'])

    def test_lifecycle_telemetry_failure_does_not_prevent_resource_reclamation(self):
        from types import SimpleNamespace
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        original = self.runtime.update
        def update(*args, **fields):
            if any(k in fields for k in ('worker_exit_at', 'cleanup_started_at', 'cleanup_finished_at')):
                raise OSError('Telemetry unavailable')
            return original(*args, **fields)
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='{"ok":true}', stderr='')), \
             patch.object(self.runtime, 'update', side_effect=update), \
             patch.object(self.runtime, 'remove') as remove:
            self.assertTrue(json.loads(self.runtime.delegate('gridcraft', 'Analyze', Path(self.temp.name) / 'work'))['ok'])
        remove.assert_called_once()
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_long_worker_response_remains_valid_json(self):
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        class Result:
            returncode = 0
            stdout = json.dumps({'ok': True, 'response': 'x' * 30000})
            stderr = ''
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', return_value=Result()), \
             patch.object(self.runtime, 'remove'):
            result = self.runtime.delegate('gridcraft', 'Analizza', Path(self.temp.name) / 'work')
        self.assertEqual(len(json.loads(result)['response']), 30000)

    def test_deepseek_credentials_are_read_only_and_absent_from_job(self):
        key = 'test-only-api-credential'
        (self.state.credential_dir('deepseek') / 'api.json').write_text(json.dumps({'api_key': key}))
        self.state.update_agent('gridcraft', {'engine': 'deepseek', 'model': 'deepseek-flash'})
        captured = []
        class Result:
            returncode = 0
            stdout = '{"ok":true}'
            stderr = ''
        def execute(argv, **kwargs):
            captured.append(argv)
            jobs = list((self.state.STATE / 'jobs').glob('*.json'))
            self.assertEqual(len(jobs), 1)
            self.assertNotIn(key, jobs[0].read_text())
            return Result()
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', side_effect=execute), \
             patch.object(self.runtime, 'remove'):
            self.runtime.delegate('gridcraft', 'Analizza', Path(self.temp.name) / 'work')
        self.assertTrue(any('dst=/credentials,readonly' in arg for arg in captured[0]))

    def test_unsuccessful_worker_json_is_not_reported_as_success(self):
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        class Result:
            returncode = 0
            stdout = '{"ok":false}'
            stderr = ''
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', return_value=Result()), \
             patch.object(self.runtime, 'remove'):
            with self.assertRaisesRegex(RuntimeError, 'completamento'):
                self.runtime.delegate('gridcraft', 'Analizza', Path(self.temp.name) / 'work')
        self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

    def test_login_setup_errors_release_admission(self):
        from studio import login
        for failing_operation in ('credential_dir', 'pty.openpty'):
            with self.subTest(operation=failing_operation), \
                 patch('studio.login.' + failing_operation, side_effect=OSError('setup failed')):
                with self.assertRaises(OSError):
                    login.LoginSession('gemini')
            self.assertFalse(self.runtime.EXECUTION_LOCK.locked())

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
