import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from studio import run_agent


class WorkerTests(unittest.TestCase):
    def test_cli_completion_requires_real_deliverables(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def worker_path(value):
                path = Path(value)
                if path.is_absolute() and not path.is_relative_to(root):
                    return root / str(path).lstrip('/')
                return path
            for name in ('credentials', 'tmp', 'mnt/skills/custom/artcraft-workspace'):
                (root / name).mkdir(parents=True)
            (root / 'mnt/skills/custom/artcraft-workspace/SKILL.md').write_text('Common procedure')
            jobfile = root / 'job.json'
            job = {'engine': 'codex', 'agent': 'gridcraft', 'run_id': 'success',
                   'skills': ['artcraft-workspace'], 'instructions': '', 'task': 'Analysis',
                   'timeout': 10, 'model': ''}
            # Real CLI subprocess fixture verifies cwd and env, then creates outputs.
            code = '''
import json, os, pathlib, sys
out = pathlib.Path(os.environ['ARTCRAFT_OUTPUT_DIR'])
assert pathlib.Path.cwd() == out
(out / 'report.txt').write_text('verified')
(out / 'handoff.json').write_text(json.dumps({
    'task': 'Analysis', 'source_files': [], 'output_files': [str(out / 'report.txt')],
    'delivery': {'source_status': 'not_applicable', 'source_note': 'Analysis report only', 'files': [{
        'path': str(out / 'report.txt'), 'role': 'report', 'format': 'TXT', 'open_with': 'Text editor',
        'editability': 'Report text', 'reopen': {'status': 'passed', 'evidence': 'Read report.txt'}, 'limitations': []}]},
    'checks': [{'name': 'Content', 'status': 'passed', 'evidence': 'Read report.txt'}], 'warnings': []}))
pathlib.Path(sys.argv[1]).write_text('Completed')
'''
            with patch.object(run_agent, 'Path', side_effect=worker_path), \
                 patch.object(sys, 'argv', ['run_agent.py', str(jobfile)]), \
                 patch.object(run_agent, 'command', side_effect=lambda engine, model, prompt, final: [sys.executable, '-c', code, str(final)]):
                jobfile.write_text(json.dumps(job))
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    self.assertEqual(run_agent.main(), 0)
                result = json.loads(stream.getvalue())
                self.assertTrue(result['ok'])
                self.assertTrue(Path(result['handoff']['output_files'][0]).is_file())
                self.assertTrue((root / 'root/.agents/skills/artcraft-workspace/SKILL.md').is_file())
                job['run_id'] = 'missing'
                jobfile.write_text(json.dumps(job))
                with patch.object(run_agent, 'command', return_value=[sys.executable, '-c', 'pass']):
                    with self.assertRaises(FileNotFoundError):
                        run_agent.main()


if __name__ == '__main__':
    unittest.main()
