"""Run all eleven credential-free preflights through the real CLI; never cloud proof."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
contract=json.loads((root/'course-contract.json').read_text())
for demo in contract['demos']:
    subprocess.run([sys.executable,'-m','ai300.cli','--demo',demo['stem'],'check','--offline'],cwd=root,check=True,timeout=30)
print('PASS: all eleven offline preflights. Azure runtime NOT RUN.')
