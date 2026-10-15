import json
import tempfile
import unittest
from pathlib import Path

from studio.handoff import validate_handoff


class HandoffFixture(unittest.TestCase):
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


class HandoffTests(HandoffFixture):
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


class DeliveryTests(HandoffFixture):
    def metadata(self, path=None, role='editable_source'):
        return {'path': str(path or self.file), 'role': role, 'format': 'DXF',
                'open_with': 'CADCraft', 'editability': 'Polilinee e layer',
                'reopen': {'status': 'passed', 'evidence': 'cadcraft-cli run: riaperto e modificato'},
                'limitations': []}

    def delivery(self, files=None, status='included'):
        self.value['delivery'] = {'source_status': status, 'source_note': 'Sorgente del risultato',
                                  'files': files if files is not None else [self.metadata()]}

    def test_new_worker_requires_metadata_but_legacy_reading_still_works(self):
        self.validate()
        with self.assertRaisesRegex(ValueError, 'delivery'):
            validate_handoff(self.output, self.workspace, require_delivery=True)
        self.delivery()
        self.assertEqual(self.validate()['delivery']['source_status'], 'included')

    def test_glb_export_and_input_dxf_do_not_count_as_delivered_source(self):
        glb = self.output / 'robot.glb'
        glb.write_bytes(b'glTF export fixture')
        self.value['output_files'] = [str(glb)]
        self.value['source_files'] = [str(self.source)]
        export = self.metadata(glb, role='export')
        export.update(format='GLB', open_with='GLB viewer', editability='Mesh di scambio; compatibilità CADCraft non verificata')
        self.delivery([export])
        with self.assertRaisesRegex(ValueError, 'sorgenti consegnati'):
            self.validate()
        # A source actually delivered, separately from its export, satisfies the contract.
        self.value['output_files'].append(str(self.file))
        self.value['delivery']['files'].append(self.metadata())
        self.assertEqual(len(self.validate()['delivery']['files']), 2)

    def test_sources_must_be_downloadable_not_only_inputs_or_previews(self):
        self.delivery([self.metadata(self.source)])
        with self.assertRaisesRegex(ValueError, 'già elencato'):
            self.validate()
        self.value['previews'] = [str(self.file)]
        self.value['output_files'] = [str(self.output / 'final.pdf')]
        (self.output / 'final.pdf').write_bytes(b'export')
        self.delivery([self.metadata(), self.metadata(self.output / 'final.pdf', 'export')])
        with self.assertRaisesRegex(ValueError, 'scaricabile'):
            self.validate()

    def test_every_output_requires_unique_metadata_and_opening_instructions(self):
        self.delivery()
        self.value['delivery']['files'] *= 2
        with self.assertRaisesRegex(ValueError, 'unico'):
            self.validate()
        self.delivery([self.metadata(role='export')])
        other = self.output / 'native.dxf'
        other.write_text('native fixture')
        self.value['output_files'].append(str(other))
        with self.assertRaisesRegex(ValueError, 'mancano metadati'):
            self.validate()
        self.value['output_files'].pop()
        self.delivery()
        self.value['delivery']['files'][0]['open_with'] = ' '
        with self.assertRaisesRegex(ValueError, 'open_with'):
            self.validate()

    def test_missing_sources_are_explicit_partial_delivery_not_silent_success(self):
        self.delivery([self.metadata(role='export')], status='unavailable')
        with self.assertRaisesRegex(ValueError, 'warnings'):
            self.validate()
        self.value['warnings'] = ['Sorgente equivalente non disponibile: consegna parziale']
        self.assertEqual(self.validate()['delivery']['source_status'], 'unavailable')
        self.value['delivery']['source_status'] = 'not_applicable'
        with self.assertRaisesRegex(ValueError, 'prodotto esportato'):
            self.validate()

    def test_unverified_source_keeps_failure_and_requires_limit_and_warning(self):
        self.delivery()
        item = self.value['delivery']['files'][0]
        item['reopen'] = {'status': 'failed', 'evidence': 'Importazione fallita nella release installata'}
        with self.assertRaisesRegex(ValueError, 'limite esplicito'):
            self.validate()
        item['limitations'] = ['Apribilità non confermata; non presentare come compatibile']
        with self.assertRaisesRegex(ValueError, 'warnings'):
            self.validate()
        self.value['warnings'] = ['Riapertura fallita: revisione necessaria']
        self.assertEqual(self.validate()['delivery']['files'][0]['reopen']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
