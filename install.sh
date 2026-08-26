#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; PROFILE=safe; DRY=0
while (($#)); do case "$1" in --dry-run) DRY=1;; --profile) PROFILE="${2:?}"; shift;; *) echo "unknown arg: $1" >&2; exit 2;; esac; shift; done
case "$PROFILE" in safe|full|minimal|frontend|backend|ai-ml|cpp|security) ;; *) echo bad-profile >&2; exit 2;; esac
DEST="${VIBE_HOME:-$HOME/.vibe}"; echo "vibe_start -> $DEST (profile=$PROFILE dry_run=$DRY)"; ((DRY)) && exit 0
mkdir -p "$DEST"; cp -f "$ROOT/AGENTS.md" "$DEST/AGENTS.md"; cp -f "$ROOT/START_HERE.md" "$DEST/START_HERE.md"; "$ROOT/scripts/install-repositories.sh"; "$ROOT/scripts/doctor.sh"
