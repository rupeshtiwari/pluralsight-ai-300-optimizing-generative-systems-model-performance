"""Recognize intentionally unfinished demo source before any live action."""
import ast
import json
from .core import ROOT, Hold


def starter_function(demo, contract=None):
    contract = contract or json.loads((ROOT / 'course-contract.json').read_text())
    item = next(d for d in contract['demos'] if d['stem'] == demo)
    return item.get('starter_function', item['implementation'].split(':')[1])


def exercise_status(demo, root=ROOT):
    contract = json.loads((root / 'course-contract.json').read_text())
    name = starter_function(demo, contract)
    tree = ast.parse((root / 'ai300/demos.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    unfinished = any(isinstance(n, ast.Constant) and isinstance(n.value, str)
                     and n.value.startswith('STARTER: ') for n in ast.walk(node))
    return {'demo': demo, 'source_state': 'STARTER' if unfinished else 'IMPLEMENTED',
            'file': 'ai300/demos.py', 'function': name,
            'runtime': 'NOT RUN'}


def require_implementation(demo):
    status = exercise_status(demo)
    if status['source_state'] == 'STARTER':
        raise Hold(f"STARTER: Complete {status['file']}:{status['function']} before live actions. "
                   f"See docs/exercise-branches.md or compare origin/{demo}-after. Cleanup remains available.")
