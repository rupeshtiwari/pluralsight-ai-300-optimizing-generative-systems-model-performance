"""Effective runtime version checks; a dependency's presence is not a frozen version."""
import sys
from importlib.metadata import version, PackageNotFoundError
from .core import ROOT, require
PYTHON_VERSION='3.12.16'
TRAIN={'torch':'2.14.1+cpu','transformers':'5.20.2','peft':'0.21.2','accelerate':'1.15.0','sentence-transformers':'6.2.0','mlflow-skinny':'3.15.0','azureml-mlflow':'1.62.0.post6','azure-identity':'1.26.0'}
SERVE={'torch':'2.14.1+cpu','transformers':'5.20.2','peft':'0.21.2','accelerate':'1.15.0','azureml-inference-server-http':'1.5.1'}
def require_versions(expected,allow_client_cpu_suffix=False):
    observed_python='.'.join(map(str,sys.version_info[:3])); require(observed_python==PYTHON_VERSION,f'Expected Python {PYTHON_VERSION}, observed {observed_python}. Install the approved patch version; offline checks remain available.')
    observed={}
    for name,pin in expected.items():
        try: actual=version(name)
        except PackageNotFoundError: actual='MISSING'
        allowed={pin}
        if allow_client_cpu_suffix and name=='torch': allowed.add(pin+'+cpu')
        require(actual in allowed,f'Expected {name}=={pin}, observed {actual}; install the pinned environment and run pip check.')
        observed[name]=actual
    return {'python':observed_python,'packages':observed}
def client_versions():
    pins={line.split('==')[0]:line.split('==')[1] for line in (ROOT/'requirements-client.txt').read_text().splitlines() if '==' in line and not line.startswith('#')}
    return require_versions(pins,allow_client_cpu_suffix=True)
