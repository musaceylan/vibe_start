#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${VIBE_HOME:-$HOME/.vibe}/repos"
PROFILE="safe"
while (($#)); do
  case "$1" in
    --profile) PROFILE="${2:?missing profile}"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
case "$PROFILE" in safe|minimal|frontend|backend|ai-ml|cpp|security|full) ;; *) echo "bad profile: $PROFILE" >&2; exit 2;; esac
mkdir -p "$DEST"
python3 - "$ROOT/manifests/repositories.lock.json" "$DEST" "$PROFILE" <<'PY_INNER'
import json, pathlib, re, subprocess, sys
manifest = json.load(open(sys.argv[1], encoding='utf-8'))
dest = pathlib.Path(sys.argv[2])
profile = sys.argv[3]
selected = []
for repo in manifest['repositories']:
    if not repo.get('install'):
        continue
    profiles = repo.get('installProfiles')
    if not profiles:
        raise SystemExit('installable repository missing installProfiles: ' + repo['repository'])
    if profile != 'full' and profile not in profiles:
        continue
    sha = repo.get('commit') or ''
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise SystemExit('unpinned: ' + repo['repository'])
    selected.append(repo)

for repo in selected:
    repository = repo['repository']
    sha = repo['commit']
    owner, name = repository.split('/', 1)
    # owner__repo prevents collisions such as anthropics/skills vs mattpocock/skills.
    directory = dest / f'{owner}__{name}'
    if not directory.exists():
        subprocess.run([
            'git', 'clone', '--filter=blob:none', '--no-checkout',
            'https://github.com/' + repository + '.git', str(directory)
        ], check=True)
    if not (directory / '.git').exists():
        raise SystemExit('not a git repository: ' + str(directory))
    subprocess.run(['git', '-C', str(directory), 'fetch', '--quiet', 'origin', sha], check=True)
    subprocess.run(['git', '-C', str(directory), 'checkout', '--detach', '--quiet', sha], check=True)
    print(f'installed {repository}@{sha[:12]} -> {directory}')
print(f'profile={profile} installed={len(selected)}')
PY_INNER
