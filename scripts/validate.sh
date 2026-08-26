#!/usr/bin/env bash
set -euo pipefail
"$(dirname "$0")/doctor.sh"
python3 "$(dirname "$0")/route.py" --task "fix a backend API bug" >/dev/null
echo validation-OK
