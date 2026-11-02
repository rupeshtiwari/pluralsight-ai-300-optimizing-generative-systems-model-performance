"""Build honest per-demo source starters. Does not contact Azure or change Git refs."""
import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai300.exercises import starter_function


def definition(source, name):
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = source.splitlines(keepends=True)
    return node, ''.join(lines[node.lineno - 1:node.end_lineno])


def starter_source(source, demo):
    name = demo['starter_function']
    node, answer = definition(source, name)
    instructions = '\n'.join('    # Step ' + str(s['n']) + ': ' + s['title'] for s in demo['steps'])
    stub = (f'def {name}(run,n):\n'
            f'    """Implement {demo["title"]} using the numbered learner steps."""\n'
            f'{instructions}\n'
            f'    raise Hold("STARTER: Implement {name}; compare origin/{demo["after_branch"]}.")\n')
    lines = source.splitlines(keepends=True)
    result = ''.join(lines[:node.lineno - 1]) + stub + ''.join(lines[node.end_lineno:])
    # Every other function/import/dispatch and every safety helper must remain identical.
    before = ast.parse(source); after = ast.parse(result)
    for tree in (before, after):
        tree.body = [n for n in tree.body if not isinstance(n, ast.FunctionDef) or n.name != name]
    if ast.dump(before) != ast.dump(after):
        raise ValueError('Starter changed code outside the selected function')
    return result, hashlib.sha256(answer.encode()).hexdigest()


def write_starter(root, demo_id, reference):
    contract = json.loads((root / 'course-contract.json').read_text())
    demo = next(d for d in contract['demos'] if d['stem'] == demo_id)
    path = root / 'ai300/demos.py'
    source, answer_hash = starter_source(path.read_text(), demo)
    path.write_text(source)
    state = {'state': 'STARTER', 'demo': demo_id, 'before_branch': demo['before_branch'],
             'after_branch': demo['after_branch'], 'reference_main': reference,
             'source_file': 'ai300/demos.py', 'omitted_function': demo['starter_function'],
             'completed_function_sha256': answer_hash,
             'prerequisites': demo['prerequisite_demos'],
             'runtime': 'NOT RUN'}
    (root / 'exercise-state.json').write_text(json.dumps(state, indent=2) + '\n')
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', required=True)
    parser.add_argument('--output', type=Path, required=True,
                        help='New, empty destination outside the source checkout')
    parser.add_argument('--reference', required=True, help='Exact reviewed main commit SHA')
    args = parser.parse_args()
    output = args.output.resolve()
    if ROOT == output or ROOT in output.parents or output.exists():
        parser.error('Choose a new destination outside this source checkout')
    if len(args.reference) != 40 or any(c not in '0123456789abcdef' for c in args.reference):
        parser.error('--reference must be a full 40-character commit SHA')
    contract = json.loads((ROOT / 'course-contract.json').read_text())
    if args.demo not in {d['stem'] for d in contract['demos']}:
        parser.error('Unknown demo')
    # Export the exact reviewed commit, never local secrets, evidence or uncommitted edits.
    import io
    import subprocess
    import tarfile
    archive = subprocess.check_output(['git', '-C', str(ROOT), 'archive', '--format=tar',
                                       args.reference], timeout=30)
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe source path')
            dst = output / relative
            if member.isdir():
                dst.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(bundle.extractfile(member).read())
                dst.chmod(0o755 if member.mode & 0o111 else 0o644)
            else:
                raise ValueError('Expected a regular source file: ' + member.name)
    print(json.dumps(write_starter(output, args.demo, args.reference), indent=2))


if __name__ == '__main__':
    main()
