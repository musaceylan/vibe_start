#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/doctor.py" "$(cd "$(dirname "$0")/.." && pwd)"
