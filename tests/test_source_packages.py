import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from studio import source_packages as packages
from studio.deliveries import build_delivery, read_review


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def film(self, ref='Media/movie.mp4', clips=None):
        return {'format': 'filmcraft.project', 'project': {'items': {
            '1': {'kind': {'Media': {'media': {'File': {'path': ref}}}}},
            '2': {'kind': {'Sequence': {'video_tracks': [{'items': [{'item': 1}] if clips is None else clips}]}}}}}}

    def archive(self, files):
        path = self.root / 'sources.zip'
        with zipfile.ZipFile(path, 'w') as z:
            for name, data in files.items():
                z.writestr(name, data)
        return path

    def test_real_missing_dependency_rejected_even_when_manifest_claims_success(self):
        archive = self.archive({'project.fcproj': json.dumps(self.film()), 'unrelated.mp4': 'some bytes'})
        with self.assertRaisesRegex(ValueError, 'Dipendenza mancante'):
            packages.verify_archive(archive)

    def test_empty_timeline_absolute_paths_and_unprepared_relative_projects_rejected(self):
        for value, expected in [(self.film(clips=[]), 'vuota'), (self.film('/mnt/user-data/outputs/movie.mp4'), 'assoluto'),
                                (self.film(), 'preparato')]:
            archive = self.archive({'project.fcproj': json.dumps(value), 'Media/movie.mp4': 'movie'})
            with self.assertRaisesRegex(ValueError, expected):
                packages.verify_archive(archive)

    def test_preparation_is_local_and_originals_stay_portable(self):
        archive = self.archive({'project.fcproj': json.dumps(self.film()), 'Media/movie.mp4': 'movie',
                               'PREPARA_SORGENTI.py': Path(packages.__file__).read_text()})
        self.assertEqual(packages.verify_archive(archive)['status'], 'passed')
        moved = self.root / 'a different folder'; moved.mkdir()
        packages.extract(archive, moved)
        original = (moved / 'project.fcproj').read_bytes()
        local, = packages.prepare(moved)
        ref = list(packages.references(json.loads(local.read_text())))[0][2]
        self.assertEqual(ref, str(moved / 'Media/movie.mp4'))
        self.assertEqual((moved / 'project.fcproj').read_bytes(), original)
        shutil.move(moved, self.root / 'moved-again')
        local, = packages.prepare(self.root / 'moved-again')
        self.assertIn('moved-again/Media/movie.mp4', local.read_text())

    def test_nested_broken_colleague_and_path_escape_are_rejected(self):
        effect = {'items': {'1': {'kind': {'type': 'Comp', 'layers': [{}]}},
                            '2': {'kind': {'type': 'Footage', 'path': 'missing-texture.png'}}}}
        nested = self.archive({'robot.ecproj': json.dumps(effect)}).read_bytes()
        archive = self.archive({'EffectCraft/sources.zip': nested})
        with self.assertRaisesRegex(ValueError, 'missing-texture'):
            packages.verify_archive(archive)
        archive = self.archive({'../escape.txt': 'bad'})
        with self.assertRaisesRegex(ValueError, 'non sicuro'):
            packages.verify_archive(archive)

    def test_runtime_does_not_accept_false_reopen_claim(self):
        archive = self.archive({'project.fcproj': json.dumps(self.film())})
        item = {'path': str(archive), 'role': 'source_archive', 'reopen': {'status': 'passed'}}
        handoff = {'task': 'Final delivery', 'delivery': {'source_status': 'included', 'source_note': 'all media included', 'files': [item]}, 'checks': []}
        result = build_delivery(handoff, self.root, native=False)
        self.assertEqual(result['technical_status'], 'needs_revision')
        self.assertIn('Dipendenza mancante', result['issues'][0])
        self.assertTrue((self.root / 'delivery-manifest.json').is_file())

    def test_review_binds_real_product_and_text_model_cannot_claim_sensory_evaluation(self):
        product = self.root / 'video.mp4'; product.write_text('fixture')
        folder = self.root / 'review'; folder.mkdir()
        report = folder / 'quality-review.json'
        report.write_text(json.dumps({'product_path': str(product), 'criteria': [
            {'criterion': 'Good pose', 'method': 'visual', 'status': 'passed', 'evidence': 'I saw it'}]}))
        handoff = {'source_files': [str(product)], 'output_files': [str(report)]}
        review = read_review(handoff, folder, self.root, 'deepseek')
        self.assertEqual(review['status'], 'needs_review')
        self.assertEqual(review['criteria'][0]['status'], 'not_run')
        self.assertEqual(review['sha256'], packages.digest(product))
        handoff['source_files'] = []
        with self.assertRaisesRegex(ValueError, 'source_files'):
            read_review(handoff, folder, self.root, 'codex')


if __name__ == '__main__':
    unittest.main()
