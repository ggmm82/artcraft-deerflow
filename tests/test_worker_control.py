import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from studio import docker_runtime, progress
from studio.work_results import failure_info


class WorkerControlTests(unittest.TestCase):
    def test_stop_is_scoped_to_installation_and_conversation_and_keeps_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'state';state.mkdir();(state/'installation-id').write_text('this-installation')
            workspace=root/'conversation';job='artcraft-job-123456abcdef'
            path=progress.create_job(workspace,job,'workspace','codex','fixture')
            progress.update(path,'waiting_model')
            saved=workspace/'partial.txt';saved.write_text('keep')
            info={'Config':{'Labels':{'org.artcraft.studio.installation':'this-installation',
                                      'org.artcraft.studio.workspace':progress.workspace_key(workspace)}},'State':{'Running':True}}
            with patch.object(docker_runtime,'STATE',state),patch.object(docker_runtime,'docker',return_value=json.dumps(info)) as docker:
                self.assertTrue(docker_runtime.request_stop(workspace,job)['requested'])
                self.assertEqual(docker.call_args.args,('stop','--time','10',job))
            self.assertTrue(progress.read_status(path)['cancel_requested'])
            self.assertEqual(saved.read_text(),'keep')
            info['Config']['Labels']['org.artcraft.studio.workspace']='another-conversation'
            with patch.object(docker_runtime,'STATE',state),patch.object(docker_runtime,'docker',return_value=json.dumps(info)) as docker:
                with self.assertRaises(ValueError):docker_runtime.request_stop(workspace,job)
                self.assertEqual(docker.call_count,1)
            self.assertFalse(failure_info('Interruzione della fase richiesta dall’utente')['retryable'])
            with self.assertRaises(ValueError):docker_runtime.request_stop(workspace,'../another-job')
