"""Exercise real LangChain tool wrappers in the pinned Gateway image."""
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    from studio.tools import studio_delegate, studio_plan
except ImportError:
    if os.getenv('STUDIO_REQUIRE_GATEWAY_TESTS') == '1':
        raise
    studio_delegate = None


@unittest.skipIf(studio_delegate is None, 'Requires the pinned Gateway tool runtime')
class AdaptiveToolTests(unittest.TestCase):
    def test_tool_memory_is_compact_and_delivery_requirements_reach_the_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request-one')]})
            folder = root / 'outputs/filmcraft/fixture'; folder.mkdir(parents=True)
            movie = folder / 'final.mp4'; movie.write_text('fixture media path')
            reply = {'ok': True, 'response': 'private verbose worker context' * 10000,
                'output_dir': '/mnt/user-data/outputs/filmcraft/fixture',
                'product_verified': True, 'verified_products': ['/mnt/user-data/outputs/filmcraft/fixture/final.mp4'],
                'handoff': {'output_files': ['/mnt/user-data/outputs/filmcraft/fixture/final.mp4'], 'source_files': [],
                    'checks': [{'name': 'Media effettivi', 'status': 'passed', 'evidence': 'fixture'}],
                    'warnings': [], 'delivery': {'source_status': 'included', 'files': [
                        {'path': '/mnt/user-data/outputs/filmcraft/fixture/final.mp4', 'role': 'export', 'format': 'MP4',
                         'open_with': 'Player video', 'editability': 'Video esportato'}]}}}
            with patch('studio.tools.workspace_for', return_value=root), \
                 patch('studio.state.team', return_value={'engine': 'deepseek', 'model': 'fixture'}), \
                 patch('studio.tools.delegate', return_value=json.dumps(reply)) as worker:
                studio_plan.func(runtime=runtime, brief='Robot con musica', project_type='animated_video')
                compact = studio_delegate.func(agent='filmcraft', task='Integra il risultato completo', runtime=runtime, purpose='delivery')
                self.assertLess(len(compact), 5000)
                self.assertNotIn('private verbose', compact)
                self.assertTrue(json.loads(compact)['ok'])
                self.assertEqual(worker.call_args.kwargs['requirements'], {'video': True, 'audio': True})
                self.assertEqual(worker.call_args.kwargs['purpose'], 'delivery')
                with self.assertRaisesRegex(ValueError, 'sorgenti incompleti'):
                    studio_plan.func(runtime=runtime, status='ready',
                        product_path='/mnt/user-data/outputs/filmcraft/fixture/final.mp4', summary='Video pronto')

    def test_one_user_turn_cannot_loop_on_quota_but_an_explicit_continue_can_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request-one')]})
            with patch('studio.tools.workspace_for', return_value=Path(directory)), \
                 patch('studio.state.team', return_value={'engine': 'gemini', 'model': 'fixture'}), \
                 patch('studio.tools.delegate', return_value=json.dumps({'ok': False, 'error': 'Individual quota reached'})) as worker:
                for _ in range(2):
                    studio_delegate.func(agent='effectcraft', task='Correggi la posa', runtime=runtime, step_id='motion')
                self.assertEqual(worker.call_count, 1)
                runtime.state['messages'].append(SimpleNamespace(type='human', id='explicit-continue'))
                studio_delegate.func(agent='effectcraft', task='Riprendi la posa', runtime=runtime, step_id='motion')
                self.assertEqual(worker.call_count, 2)
