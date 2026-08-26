#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; DEST="${VIBE_HOME:-$HOME/.vibe}/repos"; mkdir -p "$DEST"
python3 - "$ROOT/manifests/repositories.lock.json" "$DEST" <<'PY_INNER'
import json,subprocess,sys,pathlib
m=json.load(open(sys.argv[1])); dest=pathlib.Path(sys.argv[2])
for r in m['repositories']:
    if not r.get('install'): continue
    sha=r.get('commit')
    if not sha or len(sha)!=40: raise SystemExit('unpinned: '+r['repository'])
    name=r['repository'].split('/',1)[1]; d=dest/name
    if not d.exists(): subprocess.run(['git','clone','--filter=blob:none','--no-checkout','https://github.com/'+r['repository']+'.git',str(d)],check=True)
    subprocess.run(['git','-C',str(d),'fetch','--quiet','origin',sha],check=True)
    subprocess.run(['git','-C',str(d),'checkout','--detach',sha],check=True)
PY_INNER
