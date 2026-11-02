"""Exercise state tests use source snapshots and no Azure services."""
import ast
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai300 import cli, exercises
from ai300.core import Hold, ROOT

spec = importlib.util.spec_from_file_location('branch_builder', ROOT / 'scripts/exercise_branches.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ExerciseBranchesTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / 'course-contract.json').read_text())
        self.source = (ROOT / 'ai300/demos.py').read_text()

    def test_every_demo_has_distinct_named_before_and_after(self):
        for d in self.contract['demos']:
            self.assertEqual(d['before_branch'], d['stem'] + '-before')
            self.assertEqual(d['after_branch'], d['stem'] + '-after')
            self.assertEqual(d['start_branch'], d['before_branch'])
            builder.definition(self.source, d['starter_function'])

    def test_starter_omits_only_its_selected_function(self):
        for d in self.contract['demos']:
            source, digest = builder.starter_source(self.source, d)
            node, text = builder.definition(source, d['starter_function'])
            self.assertIn('STARTER: ', text)
            # Executing the stub must stop without constructing a cloud adapter.
            ns = {'Hold': Hold}
            exec(compile(ast.Module(body=[node], type_ignores=[]), '<starter>', 'exec'), ns)
            with self.assertRaisesRegex(Hold, 'STARTER: '):
                ns[d['starter_function']](object(), 1)
            self.assertEqual(len(digest), 64)
            if d['stem'] == 'm3-demo4':
                self.assertEqual(d['starter_function'], '_canary_step')
                self.assertEqual(builder.definition(source, 'canary_rollback')[1],
                                 builder.definition(self.source, 'canary_rollback')[1])
                self.assertEqual(builder.definition(source, 'set_traffic')[1],
                                 builder.definition(self.source, 'set_traffic')[1])

    def test_each_starter_preserves_other_demos_and_prerequisites(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'ai300').mkdir()
            (root / 'course-contract.json').write_text(json.dumps(self.contract))
            for d in self.contract['demos']:
                (root / 'ai300/demos.py').write_text(builder.starter_source(self.source, d)[0])
                for other in self.contract['demos']:
                    status = exercises.exercise_status(other['stem'], root)
                    # On a published starter this test's source already has that one gap.
                    existing = exercises.exercise_status(other['stem'])['source_state']
                    expected = 'STARTER' if other['stem'] == d['stem'] else existing
                    self.assertEqual(status['source_state'], expected)

    def test_guard_blocks_before_config_or_initialization(self):
        with patch.object(sys, 'argv', ['ai300.cli', '--demo', 'm1-demo1', 'up']), \
             patch.object(cli, 'require_implementation', side_effect=Hold('STARTER: unfinished')), \
             patch.object(cli, 'check_config') as config, patch.object(cli, 'Run') as run:
            self.assertEqual(cli.main(), 2)
            config.assert_not_called(); run.assert_not_called()

    def test_offline_check_reports_source_state_without_credentials(self):
        with patch.object(sys, 'argv', ['ai300.cli', '--demo', 'm1-demo1', 'check', '--offline']), \
             patch.object(cli, 'check_config') as config, \
             patch.object(cli, 'require_implementation') as guard:
            self.assertEqual(cli.main(), 0)
            config.assert_not_called(); guard.assert_not_called()

    def test_cleanup_remains_available_with_unfinished_source(self):
        with tempfile.TemporaryDirectory() as temp:
            run = type('RunDouble', (), {'path': Path(temp)})()
            with patch.object(sys, 'argv', ['ai300.cli', '--demo', 'm1-demo1', 'down']), \
                 patch.object(cli, 'require_implementation') as guard, \
                 patch.object(cli, 'check_config') as config, \
                 patch.object(cli, 'Run', return_value=run), \
                 patch.object(cli, 'cleanup', return_value={'cleanup': 'OFFLINE DOUBLE'}):
                self.assertEqual(cli.main(), 0)
                guard.assert_not_called(); config.assert_not_called()


if __name__ == '__main__':
    unittest.main()
