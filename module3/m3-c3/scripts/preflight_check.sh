#!/usr/bin/env bash
# Same engine from a checkout, Git worktree or extracted source archive.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Wrapper location is stable even when the archive has no Git history.
repo_root="$(cd -- "$script_dir/../../.." && pwd)"
if [[ ! -f "$repo_root/course-contract.json" || ! -d "$repo_root/ai300" ]]; then
  echo "Missing learner source root beside this wrapper; extract the complete source tree." >&2
  exit 2
fi
cd "$repo_root"
exec "${PYTHON:-python3}" -m ai300.cli --demo m3-demo2 check "$@"
