import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from studio import progress
from studio.cli_runner import run_cli


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.job = {'agent': 'gridcraft', 'engine': 'codex', 'model': 'fixture',
                    'run_id': 'artcraft-job-123456abcdef'}
        self.output = self.root / 'outputs/gridcraft' / self.job['run_id']
        self.output.mkdir(parents=True)
        self.reporter = progress.Reporter(self.output, self.job)

    def test_heartbeat_is_not_faked_work_and_files_are_observed(self):
        before = progress.read_status(self.reporter.path)['last_activity_at']
        with patch.object(progress, 'utcnow', return_value='2026-10-16T09:10:00+00:00'):
            self.reporter.pulse()
        value = progress.read_status(self.reporter.path)
        self.assertEqual(value['last_activity_at'], before)
        self.assertEqual(value['heartbeat_at'], '2026-10-16T09:10:00+00:00')
        (self.output / 'report.xlsx').write_bytes(b'fixture')
        (self.output / 'work').mkdir()
        (self.output / 'work/private.txt').write_text('private command output')
        (self.output / 'external').symlink_to('/etc/passwd')
        self.reporter.pulse()
        public = progress.list_jobs(self.root)[0]
        self.assertEqual(public['files'], [{'name': 'report.xlsx', 'size': 7}])
        self.assertNotEqual(public['last_activity_at'], before)

    def test_durable_history_is_bounded_and_contains_no_cli_secrets(self):
        for index in range(75):
            self.reporter.emit('creating', 'Passaggio ' + str(index))
        self.reporter.emit('checking', 'token=fixture-secret sk-test-secret-value-123')
        value = progress.list_jobs(self.root)[0]
        self.assertEqual(len(value['events']), 60)
        self.assertNotIn('fixture-secret', json.dumps(value))
        self.assertNotIn('sk-test', json.dumps(value))
        # A fresh reader after page/process reload sees exactly the same history.
        self.assertEqual(progress.list_jobs(self.root), [value])
        self.assertEqual(self.reporter.path.stat().st_mode & 0o777, 0o600)

    def test_observes_real_codex_and_antigravity_envelopes_without_reasoning(self):
        self.reporter.cli_event('codex', {'type': 'item.started', 'item': {
            'type': 'command_execution', 'command': 'craft cadcraft batch --api-key secret-value'}})
        self.assertIn('Cadcraft', progress.read_status(self.reporter.path)['summary'])
        self.reporter.cli_event('gemini', {'event': 'step_update', 'step_update': {
            'step_index': 4, 'state': 'ACTIVE', 'step_type': 'tool',
            'tool_info': {'parameters': {'command': 'craft gridcraft help'}, 'output': 'private transcript'}}})
        self.assertIn('Gridcraft', progress.read_status(self.reporter.path)['summary'])
        activity = progress.read_status(self.reporter.path)['last_activity_at']
        with patch.object(progress, 'utcnow', return_value='2099-01-01T00:00:00+00:00'):
            self.reporter.cli_event('gemini', {'event': 'step_update', 'step_update': {
                'step_index': 4, 'state': 'ACTIVE', 'step_type': 'tool', 'duration_seconds': 180}})
        self.assertEqual(progress.read_status(self.reporter.path)['last_activity_at'], activity)
        self.reporter.cli_event('gemini', {'event': 'step_update', 'step_update': {
            'step_index': 5, 'state': 'ACTIVE', 'step_type': 'agent_response',
            'text_delta': 'private hidden reasoning'}})
        public = json.dumps(progress.list_jobs(self.root))
        for secret in ('secret-value', 'private transcript', 'private hidden reasoning'):
            self.assertNotIn(secret, public)

    def test_other_workspaces_and_symlinked_metadata_are_not_followed(self):
        self.assertEqual(progress.list_jobs(self.root / 'another-user'), [])
        outside = self.root / 'other'; outside.mkdir()
        (outside / '.studio-jobs').symlink_to(self.root / '.studio-jobs', target_is_directory=True)
        self.assertEqual(progress.list_jobs(outside), [])
        with self.assertRaises(ValueError):
            progress.job_path(self.root, '../credentials')

    def test_cli_events_arrive_before_process_finishes_and_deadline_kills_it(self):
        marker = self.root / 'seen'
        code = '''import json,pathlib,time,sys
print(json.dumps({'type':'turn.started'}),flush=True)
marker=pathlib.Path(sys.argv[1]);deadline=time.monotonic()+3
while not marker.exists() and time.monotonic()<deadline:time.sleep(.01)
assert marker.exists(), 'No live event observed before completion'
print(json.dumps({'type':'turn.completed'}),flush=True)
'''
        events = []
        def observe(event):
            events.append(event)
            marker.write_text('observed while running')
        result = run_cli([sys.executable, '-c', code, str(marker)], cwd=self.root,
                         input='fixture', env=None, timeout=5, on_event=observe)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(events), 2)
        with self.assertRaises(subprocess.TimeoutExpired):
            run_cli([sys.executable, '-c', 'import time;time.sleep(20)'], cwd=self.root,
                    input='', env=None, timeout=0.1, on_event=observe)

    def test_background_worker_clock_and_terminal_status_survive_close(self):
        self.reporter.start(1500)
        try:
            self.reporter.emit('exporting', 'Esportazione XLSX e anteprima')
            self.reporter.emit('completed')
            finish = progress.read_status(self.reporter.path)['finished_at']
        finally:
            self.reporter.close()
        value = progress.list_jobs(self.root)[0]
        self.assertEqual(value['finished_at'], finish)
        self.assertEqual(value['phase'], 'completed')
        self.assertTrue(value['deadline_at'])


if __name__ == '__main__':
    unittest.main()
