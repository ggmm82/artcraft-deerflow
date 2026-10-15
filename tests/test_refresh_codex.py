import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from studio.refresh_codex import refresh


class RefreshTests(unittest.TestCase):
    def test_native_refresh_requests_account_only_and_never_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / 'codex'
            binary.write_text('#!' + sys.executable + '\n' + '''
import json,sys
assert sys.argv[1:] == ['app-server']
first=json.loads(sys.stdin.readline())
assert first['method']=='initialize'
print(json.dumps({'id':first['id'],'result':{}}),flush=True)
assert json.loads(sys.stdin.readline())['method']=='initialized'
request=json.loads(sys.stdin.readline())
assert request['method']=='account/read' and request['params']=={'refreshToken':True}
print(json.dumps({'id':request['id'],'result':{'account':{'type':'chatgpt'}}}),flush=True)
sys.stdin.read()
''')
            binary.chmod(0o755)
            with patch.dict(os.environ, {'PATH': directory + os.pathsep + os.environ['PATH']}):
                refresh()


if __name__ == '__main__':
    unittest.main()
