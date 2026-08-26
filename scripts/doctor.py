#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
r=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]); errors=[]
for p in (r/'manifests').glob('*.json'):
    try: json.loads(p.read_text())
    except Exception as e: errors.append(f'{p}: {e}')
m=json.loads((r/'manifests/repositories.lock.json').read_text())
for x in m['repositories']:
    if x.get('install') and not re.fullmatch(r'[0-9a-f]{40}',x.get('commit') or ''): errors.append('unpinned '+x['repository'])
for p in r.rglob('*'):
    if p.is_file() and '.git/' not in str(p) and p.stat().st_size<2000000:
        s=p.read_text(errors='ignore')
        if re.search(r'(?i)(api[_-]?key|password|token)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}',s): errors.append('possible secret '+str(p.relative_to(r)))
if errors: print('FAIL\n'+'\n'.join(errors)); raise SystemExit(1)
print('OK: JSON valid; installable repos pinned; no obvious embedded secrets')
