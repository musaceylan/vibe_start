#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$ROOT" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
lock=json.loads((root/'manifests/repositories.lock.json').read_text())
policy=json.loads((root/'manifests/curation-policy.json').read_text())
review_statuses={'candidate','benchmark-candidate','experimental','optional'}
review=[]
for repo in lock['repositories']:
    if repo.get('status') in review_statuses:
        review.append({
            'repository':repo['repository'],
            'status':repo.get('status'),
            'loadPolicy':repo.get('loadPolicy'),
            'install':bool(repo.get('install')),
        })
proposal={
    'mode':'review-only',
    'autoPromotion':policy['autoPromotion'],
    'gates':[gate['id'] for gate in policy['gates']],
    'reviewQueue':review,
    'instruction':'Research current upstream state, fill every required gate, benchmark behavior-changing candidates, then request human approval. Never mutate pins or activate candidates automatically.'
}
print(json.dumps(proposal,indent=2))
PY
