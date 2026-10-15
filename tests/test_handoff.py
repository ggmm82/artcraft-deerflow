import json
import tempfile
import unittest
from pathlib import Path

from studio.handoff import validate_handoff


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.output = self.workspace / 'outputs' / 'run'
        self.output.mkdir(parents=True)
        self.source = self.workspace / 'input.txt'
        self.source.write_text('input')
        self.file = self.output / 'report.txt'
        self.file.write_text('report')
        self.value = {'task': 'Analisi', 'source_files': [str(self.source)],
                      'output_files': [str(self.file)], 'previews': [],
                      'checks': [{'name': 'Contenuto', 'status': 'passed', 'evidence': 'Riletto report.txt'}],
                      'warnings': []}

    def tearDown(self):
        self.temp.cleanup()

    def validate(self):
        (self.output / 'handoff.json').write_text(json.dumps(self.value))
        return validate_handoff(self.output, self.workspace)

    def test_valid_report_preserves_quality_failures(self):
        self.value['checks'][0]['status'] = 'failed'
        self.assertEqual(self.validate()['checks'][0]['status'], 'failed')

    def test_missing_or_empty_output_is_rejected(self):
        self.file.unlink()
        with self.assertRaisesRegex(ValueError, 'mancante o vuoto'):
            self.validate()
        self.file.touch()
        with self.assertRaisesRegex(ValueError, 'mancante o vuoto'):
            self.validate()

    def test_empty_input_is_allowed(self):
        self.source.write_text('')
        self.assertEqual(self.validate()['source_files'], [str(self.source)])

    def test_output_cannot_be_an_input_or_escape_via_symlink(self):
        for filename in (str(self.source), 'report.txt'):
            self.value['output_files'] = [filename]
            with self.assertRaisesRegex(ValueError, 'percorso esterno'):
                self.validate()
        self.file.unlink()
        self.file.symlink_to(self.source)
        self.value['output_files'] = [str(self.file)]
        with self.assertRaisesRegex(ValueError, 'percorso esterno'):
            self.validate()

    def test_checks_require_status_and_evidence(self):
        for value in ([], ['ok'], [{'name': 'Contenuto', 'status': 'passed'}]):
            self.value['checks'] = value
            with self.assertRaises(ValueError):
                self.validate()

    def test_manifest_cannot_be_external_symlink(self):
        external = self.workspace / 'manifest.json'
        external.write_text(json.dumps(self.value))
        (self.output / 'handoff.json').symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'esterno'):
            validate_handoff(self.output, self.workspace)


if __name__ == '__main__':
    unittest.main()
