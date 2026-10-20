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
    def setUp(self):
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        fixture = patch('studio.tools.experience_root', return_value=Path(directory.name) / 'library')
        fixture.start(); self.addCleanup(fixture.stop)

    def test_failed_sample_replans_and_new_method_reaches_worker(self):
        from studio.projects import read_project
        from studio.project_skills import read_document
        from studio.run_agent import verify_project_context
        from test_project_skills import role
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            proof = root / 'sample-review.json'; proof.write_text('{"defect":"observed"}')
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request',
                content='Create the complete result; choose the method yourself')]})
            failed = {'ok': True, 'quality_review': {'status': 'needs_revision', 'product_path': str(proof)},
                      'handoff': {'output_files': [str(proof)], 'checks': []}}
            with patch('studio.tools.workspace_for', return_value=root), \
                 patch('studio.state.team', return_value={'engine': 'codex', 'model': 'shared-fixture'}), \
                 patch('studio.tools.delegate', return_value=json.dumps(failed)) as worker:
                studio_plan.func(runtime=runtime, brief='Complete product', roles_json=json.dumps([role()]),
                    outcome_json=json.dumps({'result': 'Complete product', 'format': 'Editable document',
                        'assumptions': ['Method chosen by the team']}))
                studio_delegate.func(agent='workspace', role_id='design', task='Review sample', purpose='review', runtime=runtime)
                response = json.loads(studio_plan.func(runtime=runtime, status='blocked'))['project']
                self.assertEqual(response['status'], 'review')
                self.assertEqual(response['method_recovery']['code'], 'method_selection_required')
                strategy = {'method': 'Different construction', 'reason': 'Addresses the observed limitation', 'state': 'selected',
                    'alternatives': [{'method': 'Prior construction', 'reason': 'Sample insufficient', 'tools': [],
                                      'status': 'tested', 'evidence_paths': ['/mnt/user-data/sample-review.json']}]}
                studio_plan.func(runtime=runtime, status='working', strategy_json=json.dumps(strategy))
                current = read_project(root)
                self.assertEqual(current['strategy']['request_hash'], current['acceptance']['hash'])
                worker.return_value = json.dumps({'ok': True})
                studio_delegate.func(agent='workspace', role_id='design', task='Try the new method', runtime=runtime)
                self.assertIn('Scelte provvisorie', worker.call_args.args[1])
                compiled = worker.call_args.kwargs['role']
                memory = json.loads(read_document(root, compiled['memory']))
                self.assertEqual(memory['method_selection'], current['strategy']['record'])
                verify_project_context({'role': compiled}, root)
                saved = root / Path(memory['method_selection']['path']).relative_to('/mnt/user-data')
                saved.write_text('Changed method after compilation')
                with self.assertRaisesRegex(ValueError, 'modificato'):
                    verify_project_context({'role': compiled}, root)

    def test_contract_uses_gateway_user_input_instead_of_synthetic_agent_message(self):
        from studio.projects import read_project
        with tempfile.TemporaryDirectory() as directory:
            runtime = SimpleNamespace(context={'is_subagent': True}, config={'configurable': {'artcraft_user_messages': ['Actual user reference']}},
                state={'messages': [SimpleNamespace(type='human', id='synthetic', content='An easier substitute requested by planner')]})
            with patch('studio.tools.workspace_for', return_value=Path(directory)):
                studio_plan.func(runtime=runtime, brief='Coordinator interpretation')
                self.assertEqual(read_project(Path(directory))['acceptance']['user_requests'], ['Actual user reference'])

    def test_dynamic_role_reaches_worker_with_original_brief_and_shared_profile(self):
        from studio.project_skills import load_compiled, read_document
        from studio.projects import read_project
        from test_project_skills import role
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = 'Problema nuovo: ' + 'vincolo specifico ' * 600 + ' Fine: iniziare solo con una proposta.'
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request', content=original)]})
            with patch('studio.tools.workspace_for', return_value=root), \
                 patch('studio.state.team', return_value={'engine': 'deepseek', 'model': 'shared-fixture'}), \
                 patch('studio.tools.delegate', return_value=json.dumps({'ok': True, 'handoff': {'checks': []}})) as worker:
                studio_plan.func(runtime=runtime, brief='Proposta iniziale', outcome_json=json.dumps({'result': 'Proposta iniziale', 'format': 'Documento testuale modificabile'}), roles_json=json.dumps([role()]),
                    memory_json=json.dumps({'decisione': 'Prima la proposta'}),
                    steps_json=json.dumps([{'id': 'prepare', 'agent': 'workspace', 'role_id': 'design', 'goal': 'Proposta verificabile'}]))
                studio_delegate.func(agent='workspace', task='Preparare la proposta', step_id='prepare', runtime=runtime)
                args = worker.call_args
                compiled = args.kwargs['role']
                self.assertEqual(compiled['id'], 'design')
                self.assertIn('Confrontare alternative', load_compiled(root, compiled))
                self.assertEqual(read_document(root, args.kwargs['acceptance']['request_documents'][0]), original)
                self.assertEqual(compiled['request_hash'], args.kwargs['acceptance']['hash'])
                self.assertEqual(read_project(root)['steps'][0]['role_title'], compiled['title'])
                # Changing a real requirement compiles a new version, preserving the old file.
                runtime.state['messages'].append(SimpleNamespace(type='human', id='clarification', content='Confronta due alternative'))
                studio_delegate.func(agent='workspace', task='Aggiornare la proposta', step_id='prepare', runtime=runtime)
                updated = worker.call_args.kwargs['role']
                self.assertNotEqual(updated['version'], compiled['version'])
                self.assertIn('Missione', load_compiled(root, compiled))
                self.assertEqual(worker.call_count, 2)
                other = role(); other.update(id='verify', title='Responsabile delle verifiche')
                studio_plan.func(runtime=runtime, roles_json=json.dumps([role(), other]),
                    steps_json=json.dumps([{'id': 'prepare', 'agent': 'workspace', 'role_id': 'verify', 'goal': 'Verificare alternative'}]))
                studio_delegate.func(agent='workspace', task='Controllare la proposta', step_id='prepare', runtime=runtime)
                self.assertEqual(worker.call_args.kwargs['role']['id'], 'verify')
                self.assertEqual(read_project(root)['steps'][0]['role_title'], other['title'])

    def test_briefing_blocks_worker_until_material_choices_are_resolved(self):
        from studio.projects import read_project
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='initial', content='Crea il progetto')]})
            with patch('studio.tools.workspace_for', return_value=root), \
                 patch('studio.state.team', return_value={'engine': 'deepseek', 'model': 'fixture'}), \
                 patch('studio.tools.delegate', return_value=json.dumps({'ok': True, 'handoff': {'checks': []}})) as worker:
                response = json.loads(studio_delegate.func(agent='wordcraft', task='Avvia tutto', runtime=runtime))
                self.assertTrue(response['needs_briefing'])
                self.assertFalse(worker.called)
                self.assertEqual(read_project(root)['status'], 'clarifying')
                studio_plan.func(runtime=runtime, outcome_json=json.dumps({'result': 'Prodotto richiesto', 'questions': ['Quale forma deve avere la consegna?']}))
                response = json.loads(studio_delegate.func(agent='wordcraft', task='Avvia comunque', runtime=runtime))
                self.assertTrue(response['needs_briefing'])
                self.assertFalse(worker.called)
                runtime.state['messages'].append(SimpleNamespace(type='human', id='answer', content='Documento impaginato e sorgente modificabile'))
                studio_plan.func(runtime=runtime, outcome_json=json.dumps({'result': 'Prodotto richiesto', 'format': 'Documento impaginato con sorgente modificabile', 'questions': []}))
                response = json.loads(studio_delegate.func(agent='wordcraft', task='Prepara la prima versione', runtime=runtime))
                self.assertTrue(response['ok'])
                self.assertEqual(worker.call_count, 1)
                self.assertIn('Documento impaginato con sorgente modificabile', worker.call_args.args[1])
                self.assertFalse(read_project(root)['orientation']['needs_briefing'])

    def test_tool_memory_is_compact_and_delivery_requirements_reach_the_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request-one', content='Crea un robot con musica')]})
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
                studio_plan.func(runtime=runtime, brief='Robot con musica', project_type='animated_video', outcome_json=json.dumps({'result': 'Video con musica', 'format': 'MP4 con progetto modificabile'}))
                compact = studio_delegate.func(agent='filmcraft', task='Integra il risultato completo', runtime=runtime, purpose='delivery')
                self.assertLess(len(compact), 5000)
                self.assertNotIn('private verbose', compact)
                self.assertTrue(json.loads(compact)['ok'])
                self.assertEqual(worker.call_args.kwargs['requirements'], {'video': True, 'audio': True})
                self.assertEqual(worker.call_args.kwargs['purpose'], 'delivery')
                with self.assertRaisesRegex(ValueError, 'sorgenti incompleti'):
                    studio_plan.func(runtime=runtime, status='ready',
                        product_path='/mnt/user-data/outputs/filmcraft/fixture/final.mp4', summary='Video pronto')

    def test_large_handoff_keeps_early_failure_visible_in_actual_tool_wrapper(self):
        from studio.project_skills import read_document
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request', content='Specific requested product')]})
            checks = [{'name': 'Critical mismatch', 'status': 'failed', 'evidence': 'Actual constraint not met'}] + [
                {'name': 'Passing check ' + str(i), 'status': 'passed', 'evidence': 'Fixture evidence'} for i in range(20)]
            result = {'ok': True, 'handoff': {'checks': checks, 'delivery': {'source_status': 'included', 'files': [
                {'path': '/mnt/user-data/outputs/wordcraft/item-' + str(i) + '.txt', 'role': 'editable_source',
                 'open_with': 'Long native opening instructions ' * 100, 'reopen': {'status': 'passed', 'evidence': 'Evidence ' * 100}}
                for i in range(20)]}}}
            with patch('studio.tools.workspace_for', return_value=root), patch('studio.state.team', return_value={'engine': 'codex', 'model': 'shared'}), patch('studio.tools.delegate', return_value=json.dumps(result)):
                studio_plan.func(runtime=runtime, brief='Requested result', outcome_json=json.dumps({'result': 'Actual product', 'format': 'Editable document'}))
                text = studio_delegate.func(agent='wordcraft', task='Produce', runtime=runtime)
            compact = json.loads(text)
            self.assertLessEqual(len(text), 8000)
            self.assertEqual(compact['decision'], 'needs_revision')
            self.assertEqual(compact['check_counts']['failed'], 1)
            self.assertEqual(compact['check_counts']['passed'], 20)
            self.assertIn('Critical mismatch', text)
            full = json.loads(read_document(root, {'path': compact['details_path'], 'sha256': compact['details_sha256']}))
            self.assertEqual(full['outputs'][0]['reopen']['status'], 'passed')

    def test_one_user_turn_cannot_loop_on_quota_but_an_explicit_continue_can_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = SimpleNamespace(state={'messages': [SimpleNamespace(type='human', id='request-one')]})
            with patch('studio.tools.workspace_for', return_value=Path(directory)), \
                 patch('studio.state.team', return_value={'engine': 'gemini', 'model': 'fixture'}), \
                 patch('studio.tools.delegate', return_value=json.dumps({'ok': False, 'error': 'Individual quota reached'})) as worker:
                studio_plan.func(runtime=runtime, brief='Correggi la posa', outcome_json=json.dumps({'result': 'Posa corretta', 'format': 'Progetto modificabile e anteprima'}))
                for _ in range(2):
                    studio_delegate.func(agent='effectcraft', task='Correggi la posa', runtime=runtime, step_id='motion')
                self.assertEqual(worker.call_count, 1)
                runtime.state['messages'].append(SimpleNamespace(type='human', id='explicit-continue'))
                studio_delegate.func(agent='effectcraft', task='Riprendi la posa', runtime=runtime, step_id='motion')
                self.assertEqual(worker.call_count, 2)
