"""Run genuine offline wrappers without Git metadata, including nested working dirs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from ai300.core import ROOT


class SourceArchiveWrapperTests(unittest.TestCase):
    def test_all_eleven_preflights_run_from_an_extracted_tree(self):
        contract=json.loads((ROOT/'course-contract.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'extracted source'; target.mkdir()
            for name in ('ai300','configs','data','jobs','serving'):
                shutil.copytree(ROOT/name,target/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            for name in ('course-contract.json','config.example.json','requirements-client.txt'):
                shutil.copy2(ROOT/name,target/name)
            for demo in contract['demos']:
                scripts=Path(demo['folder'])/'scripts'
                shutil.copytree(ROOT/scripts,target/scripts)
                result=subprocess.run(['bash',str(target/scripts/'preflight_check.sh'),'--offline'],cwd=target/scripts,env={**os.environ,'PYTHON':sys.executable},capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,(demo['stem'],result.stdout,result.stderr))
                self.assertIn('OFFLINE',result.stdout)
            self.assertFalse((target/'.git').exists())

    def test_incomplete_archive_fails_before_launching_python(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); scripts=root/'module1/m1-c2/scripts';scripts.mkdir(parents=True)
            shutil.copy2(ROOT/'module1/m1-c2/scripts/preflight_check.sh',scripts/'preflight_check.sh')
            result=subprocess.run(['bash',str(scripts/'preflight_check.sh'),'--offline'],cwd=root,env={**os.environ,'PYTHON':'this-must-never-be-executed'},capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2)
            self.assertIn('extract the complete source tree',result.stderr)

if __name__=='__main__':unittest.main()
