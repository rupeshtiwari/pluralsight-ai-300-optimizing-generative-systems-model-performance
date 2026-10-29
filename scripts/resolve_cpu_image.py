"""Resolve Microsoft's documented CPU image tag to a digest; no Docker or Azure writes."""
import argparse, json, re, urllib.request
p=argparse.ArgumentParser(); p.add_argument('--tag',default='latest'); args=p.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_.-]+',args.tag): raise SystemExit('Invalid image tag')
repository='azureml/openmpi4.1.0-ubuntu22.04'
url=f'https://mcr.microsoft.com/v2/{repository}/manifests/{args.tag}'
request=urllib.request.Request(url,headers={'Accept':'application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.list.v2+json'})
with urllib.request.urlopen(request,timeout=30) as response:
    manifest=response.read(); digest=response.headers.get('Docker-Content-Digest','')
if not re.fullmatch(r'sha256:[0-9a-f]{64}',digest): raise SystemExit('Registry did not return an immutable digest; inspect MCR response.')
print(f'mcr.microsoft.com/{repository}@{digest}')
