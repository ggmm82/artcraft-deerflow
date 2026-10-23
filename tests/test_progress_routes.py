"""Exercise the genuine Gateway ownership decorator in its built image."""
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

try:
    from app.gateway.authz import AuthContext
    from deerflow.runtime.user_context import set_current_user, reset_current_user
    from studio.progress_routes import router
except ImportError:
    if os.getenv('STUDIO_REQUIRE_GATEWAY_TESTS') == '1':
        raise
    router = None


@unittest.skipIf(router is None, 'Requires the pinned Gateway image')
class ProgressRouteTests(unittest.TestCase):
    def test_owner_can_read_after_reload_but_other_users_and_anonymous_cannot(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from studio.progress import create_job, update
        from studio.projects import create_plan
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = create_job(root / 'owner/conversation', 'artcraft-job-123456abcdef', 'cadcraft', 'codex', 'fixture')
            update(path, 'creating', 'Creazione del sorgente modificabile')
            create_plan(root / 'owner/conversation', 'Tavola tecnica', [
                {'id': 'drawing', 'agent': 'cadcraft', 'goal': 'Disegno quotato', 'depends_on': []}])
            app = FastAPI()
            app.include_router(router)

            @app.middleware('http')
            async def fixture_auth(request, call_next):
                identity = request.headers.get('X-Test-User')
                user = SimpleNamespace(id=identity, system_role='user') if identity else None
                permissions = ['threads:read', 'threads:write'] if identity != 'no-permission' else []
                request.state.auth = AuthContext(user, permissions)
                token = set_current_user(user)
                try:
                    return await call_next(request)
                finally:
                    reset_current_user(token)

            async def check_access(thread, user, require_existing=False):
                self.assertTrue(require_existing)
                return thread == 'conversation' and user == 'owner'
            store = SimpleNamespace(check_access=AsyncMock(side_effect=check_access))
            paths = SimpleNamespace(user_dir=lambda user_id: root / user_id, sandbox_user_data_dir=lambda thread, user_id: root / user_id / thread)
            with patch('app.gateway.deps.get_thread_store', return_value=store), \
                 patch('studio.progress_routes.get_paths', return_value=paths), TestClient(app) as client:
                url = '/api/threads/conversation/studio-jobs'
                for attempt in range(2):
                    result = client.get(url, headers={'X-Test-User': 'owner'})
                    self.assertEqual(result.status_code, 200, result.text)
                    self.assertEqual(result.json()['jobs'][0]['summary'], 'Creazione del sorgente modificabile')
                    self.assertEqual(result.json()['project']['steps'][0]['agent'], 'cadcraft')
                    self.assertEqual(result.headers['cache-control'], 'no-store')
                self.assertEqual(client.get(url).status_code, 401)
                self.assertEqual(client.get(url, headers={'X-Test-User': 'other'}).status_code, 404)
                self.assertEqual(client.get(url, headers={'X-Test-User': 'no-permission'}).status_code, 403)
                self.assertEqual(client.get('/api/threads/missing/studio-jobs', headers={'X-Test-User': 'owner'}).status_code, 404)
                guide_url = '/api/threads/conversation/studio-guide'
                self.assertEqual(client.get(guide_url).status_code, 401)
                self.assertEqual(client.get(guide_url, headers={'X-Test-User':'other'}).status_code, 404)
                self.assertEqual(client.get(guide_url, headers={'X-Test-User':'no-permission'}).status_code, 403)
                self.assertEqual(client.get(guide_url, headers={'X-Test-User':'owner'}).status_code, 409)
                from studio import projects
                from studio.source_packages import digest
                import json, io, zipfile
                workspace = root / 'owner/conversation'
                output = workspace / 'outputs/workspace/artcraft-job-222222222222'; output.mkdir(parents=True)
                product = output / 'result.txt'; product.write_text('Owner-only product')
                projects.execute_step(workspace, 'cadcraft', 'Tavola tecnica', 'drawing', lambda *a: json.dumps({
                    'ok':True, 'output_dir':str(output), 'handoff':{'output_files':[str(product)],'checks':[]},
                    'delivery_record':{'id':output.name,'title':'Tavola tecnica','technical_status':'passed',
                                      'files':[{'path':str(product),'role':'export','sha256':digest(product)}]}}), purpose='delivery')
                guide = client.get(guide_url, headers={'X-Test-User':'owner'})
                self.assertEqual(guide.status_code, 200, guide.text)
                self.assertEqual(guide.json()['delivery_id'], output.name)
                self.assertEqual(guide.headers['cache-control'], 'no-store')
                md = client.get(guide_url+'?format=markdown', headers={'X-Test-User':'owner'})
                self.assertIn('Guida del progetto', md.text)
                self.assertIn('attachment', md.headers['content-disposition'])
                zipped = client.get(guide_url+'?format=zip', headers={'X-Test-User':'owner'})
                self.assertEqual(zipped.status_code, 200, zipped.text if zipped.status_code != 200 else '')
                with zipfile.ZipFile(io.BytesIO(zipped.content)) as archive:
                    self.assertEqual(archive.read('File/result.txt'), b'Owner-only product')
                    self.assertIn('GUIDA-PROGETTO.md', archive.namelist())
                self.assertEqual(client.get(guide_url+'?format=zip', headers={'X-Test-User':'other'}).status_code, 404)
                self.assertEqual(client.get(guide_url+'?delivery_id=other', headers={'X-Test-User':'owner'}).status_code, 409)
                audit_url='/api/threads/conversation/studio-audit'
                self.assertEqual(client.get(audit_url).status_code,401)
                self.assertEqual(client.get(audit_url,headers={'X-Test-User':'other'}).status_code,404)
                audit=client.get(audit_url,headers={'X-Test-User':'owner'})
                self.assertEqual(audit.status_code,200)
                self.assertTrue(audit.json()['events'])
                export=client.get(audit_url+'?export=true',headers={'X-Test-User':'owner'})
                self.assertIn('text/csv',export.headers['content-type'])
                self.assertIn('timestamp_utc',export.text)
                control_url = '/api/threads/conversation/studio-control'
                self.assertEqual(client.put(control_url,json={'paused':True}).status_code,401)
                self.assertEqual(client.put(control_url,json={'paused':True},headers={'X-Test-User':'other'}).status_code,404)
                self.assertEqual(client.put(control_url,json={'paused':True},headers={'X-Test-User':'owner'}).json()['user_control']['paused'],True)
                self.assertEqual(client.put(control_url,json={'paused':False},headers={'X-Test-User':'owner'}).json()['user_control']['paused'],False)
                experience_url = '/api/threads/conversation/studio-experience'
                self.assertEqual(client.get(experience_url).status_code, 401)
                self.assertEqual(client.get(experience_url, headers={'X-Test-User':'other'}).status_code, 404)
                self.assertEqual(client.get(experience_url, headers={'X-Test-User':'no-permission'}).status_code, 403)
                self.assertEqual(client.get(experience_url, headers={'X-Test-User':'owner'}).json()['total'], 0)
                self.assertEqual(client.post(experience_url+'/collect', headers={'X-Test-User':'other'}).status_code, 404)
                self.assertEqual(client.post(experience_url+'/collect', headers={'X-Test-User':'owner'}).status_code, 200)
                self.assertEqual(client.put(experience_url,json={'id':'a'*64,'excluded':True},headers={'X-Test-User':'other'}).status_code,404)
                self.assertEqual(client.post(experience_url+'/prefer',json={'delivery_id':'artcraft-job-123456abcdef','note':'Preferenza personale'},headers={'X-Test-User':'other'}).status_code,404)
                self.assertEqual(client.put(experience_url+'/lesson',json={'id':'a'*64,'accepted':True},headers={'X-Test-User':'other'}).status_code,404)
                self.assertEqual(client.put(experience_url+'/lesson',json={'id':'a'*64,'accepted':True},headers={'X-Test-User':'owner'}).status_code,409)
                with patch('studio.docker_runtime.request_stop',return_value={'requested':True}) as stop:
                    stop_url='/api/threads/conversation/studio-jobs/artcraft-job-123456abcdef/stop'
                    self.assertEqual(client.post(stop_url).status_code,401)
                    self.assertEqual(client.post(stop_url,headers={'X-Test-User':'other'}).status_code,404)
                    self.assertEqual(client.post(stop_url,headers={'X-Test-User':'owner'}).status_code,200)
                    stop.assert_called_once()
                direction_url = '/api/threads/conversation/studio-direction'
                direction = {'visual_approach': 'vector', 'instructions': 'Disegni modificabili'}
                self.assertEqual(client.put(direction_url,json=direction).status_code,401)
                self.assertEqual(client.put(direction_url,json=direction,headers={'X-Test-User':'other'}).status_code,404)
                self.assertEqual(client.put(direction_url,json=direction,headers={'X-Test-User':'no-permission'}).status_code,403)
                self.assertEqual(client.put(direction_url,json=direction,headers={'X-Test-User':'owner'}).status_code,200)
                self.assertEqual(client.get(url,headers={'X-Test-User':'owner'}).json()['project']['user_direction']['visual_approach'],'vector')
                self.assertEqual(client.put(direction_url,json={'visual_approach':'invalid'},headers={'X-Test-User':'owner'}).status_code,422)
                accept_url = '/api/threads/conversation/studio-delivery/accept'
                data = {'delivery_id': 'nonexistent'}
                self.assertEqual(client.post(accept_url, json=data).status_code, 401)
                self.assertEqual(client.post(accept_url, json=data, headers={'X-Test-User': 'other'}).status_code, 404)
                self.assertEqual(client.post(accept_url, json=data, headers={'X-Test-User': 'no-permission'}).status_code, 403)
                self.assertEqual(client.post(accept_url, json=data, headers={'X-Test-User': 'owner'}).status_code, 409)
