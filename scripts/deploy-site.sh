#!/usr/bin/env bash
set -euo pipefail

archive="${1:?Usage: deploy-site.sh <archive.tar.gz> <commit-run-attempt>}"
release="${2:?Set a commit-run-attempt release identifier}"
: "${SITE_SSH_CONFIG:?Set the SSH configuration file}"
if [[ ! "$release" =~ ^[0-9a-f]{40}-[0-9]+-[0-9]+$ ]] || [[ ! -f "$archive" ]]; then
  printf 'Invalid archive or release identifier.\n' >&2
  exit 1
fi
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checksum="$(python3 - "$archive" <<'PY'
import hashlib, sys
from pathlib import Path
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"

ssh -F "$SITE_SSH_CONFIG" site-deploy \
  'umask 022; mkdir -p /srv/contexta/site/incoming'
scp -F "$SITE_SSH_CONFIG" "$archive" \
  "site-deploy:/srv/contexta/site/incoming/$release.tar.gz"
ssh -F "$SITE_SSH_CONFIG" site-deploy \
  "python3 - '$release' '$checksum'" < "$script_dir/activate-site.py"
