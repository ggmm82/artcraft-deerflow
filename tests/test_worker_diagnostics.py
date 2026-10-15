from types import SimpleNamespace
import json
import unittest
from studio.run_agent import command, worker_error


class WorkerDiagnosticsTests(unittest.TestCase):
    def test_codex_prompt_uses_stdin_and_errors_are_structured(self):
        prompt = 'Contesto privato\n' * 20000
        args = command('codex', 'gpt-6.1-sol', prompt, '/tmp/final')
        self.assertNotIn(prompt, args)
        self.assertEqual(args[-1], '-')
        self.assertIn('--json', args)
        events = [{'type': 'item.completed', 'item': {'text': prompt}},
                  {'type': 'turn.failed', 'error': {'message': 'Model is not supported'}}]
        result = SimpleNamespace(stdout='\n'.join(map(json.dumps, events)), stderr=prompt)
        self.assertEqual(worker_error('codex', result), 'Model is not supported')

    def test_stderr_diagnostic_keeps_cause_instead_of_tail_of_prompt(self):
        result = SimpleNamespace(stdout='', stderr='Error: invalid model\n' + 'Private context\n' * 1000)
        self.assertEqual(worker_error('codex', result), 'Error: invalid model')
