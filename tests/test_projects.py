"""Team orchestration: dependency gates, genuine file links and bounded recovery."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from studio import projects


VIDEO = [
    {'id': 'visual', 'agent': 'photocraft', 'goal': 'Texture e parti separate', 'depends_on': []},
    {'id': 'motion', 'agent': 'effectcraft', 'goal': 'Anima gli asset del robot', 'depends_on': ['visual']},
    {'id': 'audio', 'agent': 'soundcraft', 'goal': 'Mix e sessione per la danza', 'depends_on': ['motion']},
    {'id': 'final', 'agent': 'filmcraft', 'goal': 'Montaggio audiovisivo e sorgenti', 'depends_on': ['motion', 'audio']},
]


def result(agent, inputs=(), ok=True):
    path = '/mnt/user-data/outputs/' + agent + '/fixture/source.native'
    return {'ok': ok, 'output_dir': str(Path(path).parent), 'handoff': {
        'source_files': list(inputs), 'output_files': [path],
        'checks': [{'name': 'Import, export e riapertura', 'status': 'passed', 'evidence': 'fixture'}],
        'delivery': {'source_status': 'included', 'files': [
            {'path': path, 'reopen': {'status': 'passed'}}]}}}


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name) / 'conversation'
        self.root.mkdir()

    def tearDown(self):
        self.directory.cleanup()

    def plan(self):
        return projects.create_plan(self.root, 'Robot che balla la Macarena', VIDEO, 'animated_video')

    def run_step(self, sid, response, capture=None):
        step = next(s for s in VIDEO if s['id'] == sid)
        def invoke(task, started=None):
            if capture is not None:
                capture.append(task)
            if started:
                started(response.get('output_dir', '/mnt/user-data/outputs/fixture/saved'))
            return json.dumps(response)
        return json.loads(projects.execute_step(self.root, step['agent'], 'Esegui fase', sid, invoke))

    def test_video_requires_real_team_but_all_catalog_roles_are_available(self):
        with self.assertRaisesRegex(ValueError, 'pianifica'):
            projects.create_plan(self.root, 'Robot animato', [VIDEO[1] | {'depends_on': []}], 'animated_video')
        all_roles = projects.applications()
        self.assertEqual(len(all_roles), 13)
        steps = [{'id': 'phase' + str(i), 'agent': app['id'], 'goal': app['role'],
                  'depends_on': ['phase' + str(i - 1)] if i else []} for i, app in enumerate(all_roles)]
        plan = projects.create_plan(self.root, 'Progetto con tutti i ruoli pertinenti', steps)
        self.assertEqual({s['agent'] for s in plan['steps']}, {app['id'] for app in all_roles})

    def test_new_catalog_specialist_needs_no_project_engine_or_model_setting(self):
        with patch.object(projects, 'applications', return_value=projects.applications() + [{'id': 'newcraft'}]):
            plan = projects.create_plan(self.root, 'Nuovo strumento', [
                {'id': 'new', 'agent': 'newcraft', 'goal': 'Nuovo prodotto', 'depends_on': []}])
        self.assertEqual(plan['steps'][0]['agent'], 'newcraft')

    def test_explicit_silent_video_omission_and_dag_validation(self):
        silent = copy.deepcopy(VIDEO)
        silent = [s for s in silent if s['id'] != 'audio']
        silent[-1]['depends_on'] = ['motion']
        plan = projects.create_plan(self.root, 'Robot senza audio', silent, 'animated_video',
                                    {'soundcraft': 'L’utente richiede esplicitamente un video muto'})
        self.assertEqual(len(plan['steps']), 3)
        with tempfile.TemporaryDirectory() as tmp:
            bad = copy.deepcopy(VIDEO)
            bad[-1]['depends_on'] = ['motion']
            with self.assertRaisesRegex(ValueError, 'tutte le fasi'):
                projects.create_plan(tmp, 'Video', bad, 'animated_video')
            bad[0]['depends_on'] = ['final']
            with self.assertRaisesRegex(ValueError, 'precedenti'):
                projects.create_plan(tmp, 'Video', bad)

    def test_dependent_work_cannot_start_early_or_bypass_assignment(self):
        self.plan()
        invoke = lambda *args: self.fail('A blocked phase must not start a worker')
        with self.assertRaisesRegex(ValueError, 'dipendenze'):
            projects.execute_step(self.root, 'filmcraft', 'Produce all alone', 'final', invoke)
        for agent, sid in [('effectcraft', ''), ('effectcraft', 'visual')]:
            with self.assertRaisesRegex(ValueError, 'step_id'):
                projects.execute_step(self.root, agent, 'Bypass', sid, invoke)

    def test_pipeline_records_handoffs_and_rejects_decorative_delegation(self):
        self.plan()
        photo = result('photocraft')
        self.assertTrue(self.run_step('visual', photo)['ok'])
        disconnected = self.run_step('motion', result('effectcraft'))
        self.assertFalse(disconnected['ok'])
        self.assertIn('visual', disconnected['error'])
        captured = []
        motion = result('effectcraft', photo['handoff']['output_files'])
        self.assertTrue(self.run_step('motion', motion, captured)['ok'])
        self.assertIn(photo['handoff']['output_files'][0], captured[0])
        self.assertIn('Ripresa del tentativo precedente', captured[0])
        audio = result('soundcraft', motion['handoff']['output_files'])
        self.assertTrue(self.run_step('audio', audio)['ok'])
        final = result('filmcraft', motion['handoff']['output_files'] + audio['handoff']['output_files'])
        self.assertTrue(self.run_step('final', final)['ok'])
        self.assertTrue(all(s['status'] == 'completed' for s in projects.read_project(self.root)['steps']))
        # Revisions invalidate downstream validation but retain saved work.
        revised = projects.revise_step(self.root, 'motion', 'Il movimento deve rispettare le pose richieste')
        self.assertEqual([s['status'] for s in revised['steps']],
                         ['completed', 'needs_revision', 'needs_revision', 'needs_revision'])
        self.assertEqual(len(revised['steps'][-1]['attempts']), 1)

    def test_failed_checks_block_downstream_and_retries_are_bounded(self):
        self.plan()
        failure = result('photocraft')
        failure['handoff']['checks'][0]['status'] = 'not_run'
        for _ in range(3):
            reply = self.run_step('visual', failure)
            self.assertFalse(reply['ok'])
        self.assertEqual(reply['project']['attempt'], 3)
        with self.assertRaisesRegex(ValueError, 'Tre tentativi'):
            self.run_step('visual', result('photocraft'))
        with self.assertRaisesRegex(ValueError, 'piano aperto'):
            self.plan()

    def test_timeout_continuation_reuses_saved_directory_without_fake_completion(self):
        self.plan()
        saved = '/mnt/user-data/outputs/photocraft/artcraft-job-123456abcdef'
        reply = self.run_step('visual', {'ok': False, 'partial': True, 'output_dir': saved, 'error': 'Tempo esaurito'})
        self.assertEqual(reply['project']['status'], 'needs_revision')
        captured = []
        self.run_step('visual', result('photocraft'), captured)
        self.assertIn(saved, captured[0])
        self.assertIn('checkpoint.json', captured[0])

    def test_restart_recovers_interrupted_phase_and_preserves_saved_path(self):
        self.plan()
        def lost_gateway(task, started):
            started('/mnt/user-data/outputs/photocraft/saved')
            raise KeyboardInterrupt()  # Process dies before the result is committed.
        with self.assertRaises(KeyboardInterrupt):
            projects.execute_step(self.root, 'photocraft', 'Create', 'visual', lost_gateway)
        with patch.object(projects, 'GATEWAY_SESSION', 'new-process'):
            plan = projects.read_project(self.root)
        self.assertEqual(plan['steps'][0]['status'], 'needs_revision')
        self.assertEqual(plan['steps'][0]['attempts'][0]['output_dir'], '/mnt/user-data/outputs/photocraft/saved')
        self.assertNotIn('gateway_session', json.dumps(plan))

    def test_project_is_conversation_scoped_and_simple_work_holds_no_lock(self):
        self.plan()
        branch = self.root.parent / 'branched'
        shutil.copytree(self.root, branch)
        self.assertIsNone(projects.read_project(branch))
        with self.assertRaisesRegex(ValueError, 'piano'):
            projects.execute_step(branch, 'photocraft', 'Create', 'visual', lambda *a: '')
        simple = self.root.parent / 'simple'
        def invoke(task):
            self.assertIsNone(projects.read_project(simple))
            return 'done'
        self.assertEqual(projects.execute_step(simple, 'cadcraft', 'Quote', '', invoke), 'done')
        other = self.root.parent / 'outside'
        other.mkdir()
        (other / '.studio-project').symlink_to(self.root / '.studio-project', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Percorso'):
            projects.read_project(other)

    def test_abandoned_project_can_be_archived_for_unrelated_new_work_without_data_loss(self):
        self.plan()
        self.run_step('visual', result('photocraft'))
        archive = projects.archive_plan(self.root, 'L’utente abbandona il video e chiede un report')
        self.assertTrue(archive['files_preserved'])
        self.assertIsNone(projects.read_project(self.root))
        saved = json.loads((self.root / '.studio-project' / (archive['id'] + '.json')).read_text())
        self.assertEqual(saved['steps'][0]['status'], 'completed')
        self.assertTrue(saved['steps'][0]['attempts'][0]['output_files'])
        self.plan()

    def test_untrusted_project_metadata_cannot_choose_an_external_archive_path(self):
        self.plan()
        path = self.root / '.studio-project/project.json'
        value = json.loads(path.read_text())
        value['id'] = '../../outside'
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'Identificatore'):
            projects.archive_plan(self.root, 'Archive')
        self.assertFalse((self.root.parent / 'outside.json').exists())


if __name__ == '__main__':
    unittest.main()
