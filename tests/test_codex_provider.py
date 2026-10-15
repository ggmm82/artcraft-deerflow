"""Run against the real pinned DeerFlow provider in the gateway image."""
import importlib.util
from types import SimpleNamespace
import unittest
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec('deerflow'), 'Requires pinned gateway dependencies')
class CodexProviderTests(unittest.TestCase):
    def test_existing_model_uses_rotated_account_credentials_on_next_request(self):
        from studio.codex_provider import StudioCodexChatModel, CodexChatModel
        first = SimpleNamespace(access_token='fixture-old-bearer', account_id='old-account')
        rotated = SimpleNamespace(access_token='fixture-new-bearer', account_id='new-account')
        with patch.object(StudioCodexChatModel, '_load_codex_auth', return_value=first):
            model = StudioCodexChatModel(model='gpt-5.4')
        with patch.object(StudioCodexChatModel, '_load_codex_auth', return_value=rotated), \
             patch('studio.codex_provider.request_codex', return_value={'ok': True}) as request:
            model._stream_response({'Authorization': 'Bearer fixture-old-bearer'}, {'tools': []})
        headers, payload = request.call_args.args
        self.assertEqual(headers['Authorization'], 'Bearer fixture-new-bearer')
        self.assertEqual(headers['ChatGPT-Account-ID'], 'new-account')
        self.assertEqual(payload['tool_choice'], 'auto')
        self.assertIn('reasoning.encrypted_content', payload['include'])

    def test_provider_errors_do_not_reflect_current_bearer(self):
        import httpx
        from studio.codex_provider import StudioCodexChatModel, CodexChatModel
        credential = SimpleNamespace(access_token='fixture-private-bearer', account_id='fixture-account')
        response = httpx.Response(401, text='Rejected fixture-private-bearer',
                                  request=httpx.Request('POST', 'https://example.invalid'))
        failure = httpx.HTTPStatusError('Unauthorized', request=response.request, response=response)
        with patch.object(StudioCodexChatModel, '_load_codex_auth', return_value=credential):
            model = StudioCodexChatModel(model='gpt-5.4')
            with patch('studio.codex_provider.request_codex', side_effect=failure), \
                 patch('studio.docker_runtime.refresh_codex_credentials'):
                with self.assertRaisesRegex(RuntimeError, r'HTTP 401.*\[REDACTED\]') as caught:
                    model._stream_response({}, {})
        self.assertNotIn(credential.access_token, str(caught.exception))

    def test_unauthorized_request_refreshes_cli_account_and_retries_once(self):
        import httpx
        from studio.codex_provider import StudioCodexChatModel, CodexChatModel
        first = SimpleNamespace(access_token='fixture-expired', account_id='account')
        renewed = SimpleNamespace(access_token='fixture-renewed', account_id='account')
        response = httpx.Response(401, request=httpx.Request('POST', 'https://example.invalid'))
        failure = httpx.HTTPStatusError('Expired', request=response.request, response=response)
        with patch.object(StudioCodexChatModel, '_load_codex_auth', return_value=first):
            model = StudioCodexChatModel(model='gpt-5.4')
        with patch.object(StudioCodexChatModel, '_load_codex_auth', side_effect=[first, renewed]), \
             patch('studio.codex_provider.request_codex', side_effect=[failure, {'ok': True}]) as api, \
             patch('studio.docker_runtime.refresh_codex_credentials') as refresh:
            self.assertEqual(model._stream_response({}, {}), {'ok': True})
        refresh.assert_called_once()
        self.assertEqual(api.call_args_list[1].args[0]['Authorization'], 'Bearer fixture-renewed')


if __name__ == '__main__':
    unittest.main()
