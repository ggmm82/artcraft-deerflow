from pathlib import Path
import tempfile
import unittest
import zipfile
from studio.component_sources import inspect_components


class ComponentSourcesTests(unittest.TestCase):
    def test_editable_parent_does_not_hide_audio_without_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);video=root/'master.mp4';video.write_bytes(b'fixture')
            archive=root/'sources.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('main.ecproj','native fixture');z.writestr('Audio/mix.wav','wave fixture')
                z.writestr('Audio/generate.py','print("recipe fixture; never executed")')
            files=[{'path':str(video),'role':'export'},
                   {'path':str(archive),'role':'source_archive','verification':{'status':'passed'}}]
            def ref(member):return {'path':str(archive),'member':member}
            parent={'name':'Animation','tool':'effectcraft','artifacts':[{'path':str(video)}],'sources':[ref('main.ecproj')]}
            handoff={'delivery':{'components':[parent]}}
            result=inspect_components(handoff,files,required=True)
            self.assertEqual(result['status'],'incomplete');self.assertIn('mix.wav',str(result['issues']))
            audio={'name':'Effects','tool':'soundcraft','artifacts':[ref('Audio/mix.wav')],'sources':[ref('main.ecproj')]}
            handoff['delivery']['components'].append(audio)
            self.assertIn('.scraft',str(inspect_components(handoff,files)['issues']))
            audio.update(tool='code',sources=[ref('Audio/mix.wav')])
            self.assertIn('appiattiti',str(inspect_components(handoff,files)['issues']))
            audio['sources']=[ref('Audio/generate.py')]
            self.assertEqual(inspect_components(handoff,files)['status'],'documented')
            audio['sources']=[ref('../missing.py')]
            self.assertEqual(inspect_components(handoff,files)['status'],'incomplete')

    def test_provided_original_requires_the_uploaded_input_and_identical_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);upload=root/'uploads/original.wav';upload.parent.mkdir();upload.write_bytes(b'original wave')
            final=root/'mix.wav';final.write_bytes(upload.read_bytes());r={'path':str(final)}
            handoff={'source_files':[str(upload)],'delivery':{'components':[
                {'name':'Original recording','tool':'provided','artifacts':[r],'sources':[r],'provided_inputs':[str(upload)]}]}}
            files=[{'path':str(final),'role':'export'}]
            self.assertEqual(inspect_components(handoff,files,workspace=root)['status'],'documented')
            final.write_bytes(b'a different mix')
            self.assertEqual(inspect_components(handoff,files,workspace=root)['status'],'incomplete')
            handoff['source_files']=[]
            self.assertEqual(inspect_components(handoff,files,workspace=root)['status'],'incomplete')

    def test_frame_sequence_can_reference_a_verified_directory_without_enumerating_every_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);archive=root/'sources.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('main.ecproj','native fixture')
                for i in range(1000):z.writestr(f'frames/{i:04d}.png','frame fixture')
            files=[{'path':str(archive),'role':'source_archive','verification':{'status':'passed'}}]
            component={'name':'Frame sequence','tool':'effectcraft',
                'artifacts':[{'path':str(archive),'member':'frames/'}],
                'sources':[{'path':str(archive),'member':'main.ecproj'}]}
            handoff={'delivery':{'components':[component]}}
            self.assertEqual(inspect_components(handoff,files)['status'],'documented')
            component['sources']=[{'path':str(archive),'member':'frames/'}]
            self.assertEqual(inspect_components(handoff,files)['status'],'incomplete')
            component['artifacts']=[{'path':str(archive),'member':'missing/'}]
            self.assertEqual(inspect_components(handoff,files)['status'],'incomplete')

    def test_missing_inventory_is_explicit_for_new_deliveries_and_compatible_with_legacy(self):
        self.assertEqual(inspect_components({},[],required=True)['status'],'not_recorded')
        self.assertTrue(inspect_components({},[],required=True)['issues'])
        self.assertFalse(inspect_components({},[])['issues'])
