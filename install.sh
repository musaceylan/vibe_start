#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE=safe
DRY=0
while (($#)); do
  case "$1" in
    --dry-run) DRY=1 ;;
    --profile) PROFILE="${2:?missing profile}"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
case "$PROFILE" in safe|full|minimal|frontend|backend|ai-ml|cpp|security) ;; *) echo bad-profile >&2; exit 2;; esac
DEST="${VIBE_HOME:-$HOME/.vibe}"
echo "vibe_start -> $DEST (profile=$PROFILE dry_run=$DRY)"
if ((DRY)); then
  python3 - "$ROOT/manifests/repositories.lock.json" "$PROFILE" <<'PY'
import json,sys
m=json.load(open(sys.argv[1])); p=sys.argv[2]
selected=[r['repository'] for r in m['repositories'] if r.get('install') and (p=='full' or p in r.get('installProfiles',[]))]
print('would install:')
for repo in selected: print(' -', repo)
PY
  exit 0
fi
mkdir -p "$DEST"
cp -f "$ROOT/AGENTS.md" "$DEST/AGENTS.md"
cp -f "$ROOT/START_HERE.md" "$DEST/START_HERE.md"
"$ROOT/scripts/install-repositories.sh" --profile "$PROFILE"
"$ROOT/scripts/doctor.sh"
