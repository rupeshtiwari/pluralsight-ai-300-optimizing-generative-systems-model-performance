#!/usr/bin/env bash
# Same engine from any nested checkout or Git worktree.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$script_dir" rev-parse --show-toplevel)"
cd "$repo_root"
exec "${PYTHON:-python3}" -m ai300.cli --demo m2-demo2 step "$@"
