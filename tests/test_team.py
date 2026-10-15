"""Verify one configuration actually reaches coordination and specialist jobs."""
import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml


class TeamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {'STUDIO_STATE': self.temp.name,
            'STUDIO_PASSWORD': 'test-password-at-least-16-characters'})
        self.environment.start()
        self.native_models = patch('studio.docker_runtime.codex_models', return_value=[
            {'id': 'gpt-5.4', 'label': 'GPT-5.4', 'default': True}])
        from studio import state, bootstrap, router, docker_runtime
        self.state = importlib.reload(state)
        self.bootstrap = importlib.reload(bootstrap)
        self.bootstrap.initialize()
        self.runtime = importlib.reload(docker_runtime)
        self.native_models.start()
        self.router = importlib.reload(router)
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        app = FastAPI()
        app.include_router(self.router.router)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.native_models.stop()
        self.environment.stop()
        self.temp.cleanup()

    def save(self, **values):
        return self.client.put('/studio/api/team', json=values, headers={'origin': 'http://testserver'})

    def test_codex_catalog_ids_and_labels_are_distinct_and_invalid_names_are_not_saved(self):
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        entries = [{'id': 'gpt-6.1-sol', 'label': 'GPT-6.1-Sol', 'default': True}]
        with patch.object(self.runtime, 'codex_models', return_value=entries):
            response = self.client.get('/studio/api/team/models?engine=codex')
            self.assertEqual(response.json()['models'], ['gpt-6.1-sol'])
            self.assertEqual(self.save(engine='codex', model='GPT-6.1 Sol').status_code, 400)
            self.assertEqual(self.save(engine='codex', model='gpt-5.4').status_code, 400)
            self.assertEqual(self.save(engine='codex', model='GPT-6.1-Sol').status_code, 200)
        self.assertEqual(self.state.team()['model'], 'gpt-6.1-sol')

    def test_single_save_resets_legacy_overrides_preserves_skills_and_reaches_worker(self):
        self.state.update_agent('wordcraft', {'engine': 'gemini', 'model': 'legacy-model',
            'instructions': 'Italiano, stile sobrio', 'skills': ['artcraft-gridcraft'], 'enabled': False})
        with patch('studio.deepseek.models', return_value=['deepseek-flash']):
            response = self.save(engine='deepseek', api_key='test-team-private-key')
        self.assertEqual(response.status_code, 200)
        data = self.client.get('/studio/api/catalog').json()
        self.assertEqual(data['team'], {'engine': 'deepseek', 'model': 'deepseek-flash', 'ready': True})
        self.assertEqual(set(data['effective_agents']), {app['id'] for app in self.state.applications()})
        for identifier, settings in data['effective_agents'].items():
            self.assertEqual((settings['engine'], settings['model']), ('deepseek', 'deepseek-flash'))
            self.assertIn('artcraft-' + identifier, settings['skills'])
            self.assertIn('artcraft-workspace', settings['skills'])
        self.assertFalse(data['agents']['wordcraft']['enabled'])
        self.assertEqual(data['agents']['wordcraft']['instructions'], 'Italiano, stile sobrio')
        self.assertIn('artcraft-gridcraft', data['agents']['wordcraft']['skills'])
        self.assertNotIn('test-team-private-key', json.dumps(data))
        captured = []
        def run(*args, **kwargs):
            captured.append(json.loads(next((self.state.STATE / 'jobs').glob('*.json')).read_text()))
            return type('Result', (), {'returncode': 0, 'stdout': '{"ok": true}', 'stderr': ''})()
        with patch.object(self.runtime, 'host_path', return_value='/host/path'), \
             patch.object(self.runtime.subprocess, 'run', side_effect=run), \
             patch.object(self.runtime, 'remove'):
            self.runtime.delegate('gridcraft', 'Prepara il foglio', Path(self.temp.name) / 'work')
        self.assertEqual(captured[0]['model'], 'deepseek-flash')
        self.assertEqual(captured[0]['engine'], 'deepseek')
        self.assertNotIn('test-team-private-key', json.dumps(captured))
        profile = yaml.safe_load((self.state.STATE / 'config.yaml').read_text())['models'][0]
        self.assertEqual(profile['name'], 'studio-codex')  # stable conversation identity
        self.assertEqual(profile['display_name'], 'Squadra ArtCraft')
        self.assertEqual(profile['model'], captured[0]['model'])
        self.assertEqual(profile['use'], 'studio.deepseek_provider:StudioDeepSeekChatModel')

    def test_change_model_without_reentering_key_and_restart_keep_all_in_sync(self):
        with patch('studio.deepseek.models', return_value=['deepseek-flash', 'deepseek-pro']):
            self.assertEqual(self.save(engine='deepseek', api_key='test-team-key').status_code, 200)
            self.assertEqual(self.client.get('/studio/api/team/models').json(), {'models': ['deepseek-flash', 'deepseek-pro']})
            self.assertEqual(self.save(engine='deepseek', model='deepseek-pro').status_code, 200)
        self.bootstrap.initialize()
        for settings in self.client.get('/studio/api/catalog').json()['effective_agents'].values():
            self.assertEqual((settings['engine'], settings['model']), ('deepseek', 'deepseek-pro'))
        self.assertEqual(self.state.team()['engine'], 'deepseek')
        # Switching accounts keeps the same chat profile and skills.
        (self.state.credential_dir('codex') / 'auth.json').write_text('{}')
        self.assertEqual(self.save(engine='codex').status_code, 200)
        self.assertTrue(all(s['engine'] == 'codex' and s['model'] == 'gpt-5.4'
            for s in self.client.get('/studio/api/catalog').json()['effective_agents'].values()))
        self.assertEqual(len(yaml.safe_load((self.state.STATE / 'config.yaml').read_text())['models']), 1)

    def test_gemini_is_a_shared_coordinator_and_worker_provider_after_restart(self):
        self.assertEqual(self.save(engine='gemini').status_code, 400)
        (self.state.credential_dir('gemini') / 'oauth_creds.json').write_text('{"fixture": true}')
        response = self.save(engine='gemini')
        self.assertEqual(response.status_code, 200)
        self.bootstrap.initialize()
        catalog = self.client.get('/studio/api/catalog').json()
        self.assertEqual(catalog['team'], {'engine': 'gemini', 'model': 'gemini-2.5-pro', 'ready': True})
        for agent in catalog['effective_agents'].values():
            self.assertEqual((agent['engine'], agent['model']), ('gemini', 'gemini-2.5-pro'))
        self.assertEqual(yaml.safe_load((self.state.STATE / 'config.yaml').read_text())['models'][0]['use'],
                         'studio.gemini_provider:StudioGeminiChatModel')
        self.assertEqual(self.save(engine='gemini', model='gemini-custom').status_code, 200)
        self.assertTrue(all(a['model']=='gemini-custom' for a in self.client.get('/studio/api/catalog').json()['effective_agents'].values()))

    def test_invalid_connection_or_model_never_partially_changes_team(self):
        before = (self.state.STATE / 'config.yaml').read_bytes()
        self.assertEqual(self.save(engine='codex').status_code, 400)
        self.assertEqual(self.save(engine='deepseek').status_code, 400)
        with patch('studio.deepseek.models', return_value=['deepseek-flash']):
            self.assertEqual(self.save(engine='deepseek', api_key='test-key', model='unknown').status_code, 400)
        self.assertEqual((self.state.STATE / 'config.yaml').read_bytes(), before)
        self.assertFalse(self.state.connection_status('deepseek'))
        with patch('studio.deepseek.models') as models:
            response = self.client.put('/studio/api/team', json={'engine': 'deepseek', 'api_key': 'test-key'},
                headers={'origin': 'https://other.example'})
        self.assertEqual(response.status_code, 403)
        models.assert_not_called()

    def test_upgrade_removes_placeholder_writers_and_preserves_active_provider(self):
        with patch('studio.deepseek.models', return_value=['deepseek-flash']):
            self.assertEqual(self.save(engine='deepseek', api_key='test-team-key').status_code, 200)
        path = self.state.STATE / 'config.yaml'
        content = yaml.safe_load(path.read_text())
        content['lead_prompt_overlay']['append'] = 'Sei la Squadra ArtCraft. Old delivery instructions.'
        content['tools'].extend([
            {'name': 'write_file', 'group': 'file:write', 'use': 'deerflow.sandbox.tools:write_file_tool'},
            {'name': 'str_replace', 'group': 'file:write', 'use': 'deerflow.sandbox.tools:str_replace_tool'},
        ])
        content['tool_groups'].append({'name': 'file:write'})
        path.write_text(yaml.safe_dump(content))
        self.bootstrap.initialize()
        migrated = yaml.safe_load(path.read_text())
        self.assertEqual(self.state.team()['engine'], 'deepseek')
        self.assertFalse(any(t['name'] in ('write_file', 'str_replace') for t in migrated['tools']))
        self.assertFalse(any(g['name'] == 'file:write' for g in migrated['tool_groups']))
        self.assertIn('Non ricopiare', migrated['lead_prompt_overlay']['append'])
        self.assertIn('sottocartelle', migrated['lead_prompt_overlay']['append'])

    def test_legacy_coordinator_and_provider_routes_apply_shared_profile(self):
        # A saved conversation using the old alias also follows the global choice.
        path = self.state.STATE / 'config.yaml'
        content = yaml.safe_load(path.read_text())
        content['models'].append({**content['models'][0], 'name': 'studio-deepseek'})
        path.write_text(yaml.safe_dump(content))
        with patch('studio.deepseek.models', return_value=['deepseek-flash', 'deepseek-pro']):
            response = self.client.put('/studio/api/providers/deepseek', json={'api_key': 'test-key'})
            self.assertEqual(response.status_code, 200)
            response = self.client.put('/studio/api/coordinator', json={'model': 'deepseek-pro'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['model'], 'deepseek-pro')
        self.assertTrue(all(p['model'] == 'deepseek-pro' for p in yaml.safe_load(path.read_text())['models']))
        self.assertTrue(all(s['model'] == 'deepseek-pro'
            for s in self.client.get('/studio/api/catalog').json()['effective_agents'].values()))
