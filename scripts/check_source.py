"""Run full solution checks or explicitly limited starter checks without Azure."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai300.exercises import exercise_status


def main():
    def run(*args):
        subprocess.run([sys.executable, *args], cwd=ROOT, check=True, timeout=120)
    contract = json.loads((ROOT / 'course-contract.json').read_text())
    starters = [d['stem'] for d in contract['demos']
                if exercise_status(d['stem'])['source_state'] == 'STARTER']
    state_path = ROOT / 'exercise-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    if starters and (not state or starters != [state.get('demo')]):
        raise ValueError('Starter source must match exactly one declared exercise state')
    run('-m', 'compileall', '-q', 'ai300', 'jobs', 'serving', 'scripts')
    run('scripts/check_contract.py')
    run('scripts/check_all.py')
    if starters:
        run('-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_exercise_branches.py', '-v')
        print('PASS: starter structure and fail-closed guard; completed-solution tests NOT RUN. '
              'Implement the declared function, then rerun this command.')
    else:
        run('-m', 'unittest', 'discover', '-s', 'tests', '-v')
        print('PASS: completed-source offline checks. Azure runtime NOT RUN.')


if __name__ == '__main__':
    main()
