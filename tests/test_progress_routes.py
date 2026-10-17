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
            paths = SimpleNamespace(sandbox_user_data_dir=lambda thread, user_id: root / user_id / thread)
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
                accept_url = '/api/threads/conversation/studio-delivery/accept'
                data = {'delivery_id': 'nonexistent'}
                self.assertEqual(client.post(accept_url, json=data).status_code, 401)
                self.assertEqual(client.post(accept_url, json=data, headers={'X-Test-User': 'other'}).status_code, 404)
                self.assertEqual(client.post(accept_url, json=data, headers={'X-Test-User': 'no-permission'}).status_code, 403)
                self.assertEqual(client.post(accept_url, json=data, headers={'X-Test-User': 'owner'}).status_code, 409)
