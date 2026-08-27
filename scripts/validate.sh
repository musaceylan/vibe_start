#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/scripts/doctor.sh"

python3 -m py_compile "$ROOT"/scripts/*.py
for file in "$ROOT"/scripts/*.sh "$ROOT/install.sh" "$ROOT/vibe"; do
  bash -n "$file"
done

python3 - "$ROOT" <<'PY'
import json, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
fixtures = json.loads((root/'tests/router-fixtures.json').read_text())['cases']
for case in fixtures:
    raw = subprocess.check_output([
        sys.executable, str(root/'scripts/route.py'), '--task', case['task']
    ], text=True)
    result = json.loads(raw)
    if result['profile'] != case['profile']:
        raise SystemExit(f"route profile mismatch for {case['task']!r}: {result['profile']} != {case['profile']}")
    missing_caps = sorted(set(case.get('capabilities', [])) - set(result.get('capabilities', [])))
    if missing_caps:
        raise SystemExit(f"route missing capabilities for {case['task']!r}: {missing_caps}")
    actual_specialists = {s['name'] for s in result.get('specialists', [])}
    missing_specialists = sorted(set(case.get('specialists', [])) - actual_specialists)
    if missing_specialists:
        raise SystemExit(f"route missing specialists for {case['task']!r}: {missing_specialists}")
print(f"router fixtures OK: {len(fixtures)}")
PY

"$ROOT/install.sh" --dry-run --profile safe >/dev/null
"$ROOT/install.sh" --dry-run --profile frontend >/dev/null

echo validation-OK
