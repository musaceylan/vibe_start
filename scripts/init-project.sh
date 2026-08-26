#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/init-project.py" "${1:-.}"
