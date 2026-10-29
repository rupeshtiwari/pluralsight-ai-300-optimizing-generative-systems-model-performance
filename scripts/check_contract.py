"""Public-safe static contract checks. Not target-machine or cloud acceptance."""
import ast, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from ai300.core import validate_splits
from ai300.demos import HANDLERS
c=json.loads((ROOT/'course-contract.json').read_text()); assert len(c['demos'])==11
assert len(c['objectives'])+sum(len(t['children']) for t in c['objectives'])==10
assert set(HANDLERS)=={d['stem'] for d in c['demos']}
for d in c['demos']:
    assert len(d['steps'])==(4 if d['stem']=='m3-demo4' else 3)
    for path in d['commands'].values(): assert (ROOT/path).is_file(),path
    text=(ROOT/d['folder']/'README.md').read_text(); assert text.count('```')%2==0
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if '://' not in target and not target.startswith('#'): assert (ROOT/d['folder']/target.split('#')[0]).exists(),target
    for step in d['steps']: assert f"lab-step.sh {step['n']}" in text
for folder in ('ai300','jobs','serving'):
    for file in (ROOT/folder).glob('*.py'): ast.parse(file.read_text())
print(json.dumps({'check':'OFFLINE_STATIC_CONTRACT','demos':11,'objectives':10,'data':validate_splits(),'azure_runtime':'NOT RUN'},indent=2))
