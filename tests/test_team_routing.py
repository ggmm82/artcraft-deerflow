import unittest
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from studio.team_routing import TeamRoutingMiddleware


class TeamRoutingTests(unittest.TestCase):
    def test_saved_legacy_selection_cannot_split_coordinator_and_workers(self):
        app = FastAPI()
        @app.post('/api/threads/{thread}/runs/stream')
        async def run(thread: str, request: Request):
            return await request.json()
        app.add_middleware(TeamRoutingMiddleware)
        with TestClient(app) as client:
            body = {'input': {'messages': ['original']}, 'context': {'model_name': 'legacy-deepseek', 'thinking_enabled': True},
                    'config': {'recursion_limit': 100, 'configurable': {'model_name': 'another-model'}}}
            result = client.post('/api/threads/test/runs/stream', json=body).json()
        self.assertEqual(result['context']['model_name'], 'studio-codex')
        self.assertEqual(result['config']['configurable']['model_name'], 'studio-codex')
        self.assertEqual(result['input'], body['input'])
        self.assertTrue(result['context']['thinking_enabled'])
        self.assertEqual(result['config']['recursion_limit'], 100)

    def test_catalog_preserves_authorization_and_usage_without_alternative_models(self):
        app = FastAPI()
        @app.get('/api/models')
        def models(denied: bool = False):
            if denied:
                raise HTTPException(401, 'Login required')
            return {'models': [{'name': 'studio-codex'}, {'name': 'legacy'}], 'token_usage': {'enabled': True}}
        app.add_middleware(TeamRoutingMiddleware)
        with TestClient(app) as client:
            response = client.get('/api/models')
            self.assertEqual(response.json(), {'models': [{'name': 'studio-codex'}], 'token_usage': {'enabled': True}})
            self.assertEqual(int(response.headers['content-length']), len(response.content))
            self.assertEqual(client.get('/api/models?denied=true').status_code, 401)
