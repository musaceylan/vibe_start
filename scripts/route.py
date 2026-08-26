#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--task',required=True); a=p.parse_args(); t=a.task.lower(); profile='minimal'
for n,pat in [('frontend',r'frontend|react|next\.js|landing|ui\b|ux\b|css|animation|framer|gsap|webgl'),('ai-ml',r'\brag\b|llm|model|embedding|mlops|inference|fine.?tun'),('cpp',r'c\+\+|cmake|embedded|automotive|clang'),('security',r'auth|security|secret|permission|vulnerab|threat'),('backend',r'backend|api|database|queue|microservice')]:
    if re.search(pat,t): profile=n; break
root=Path(__file__).resolve().parents[1]; b=json.loads((root/'manifests/bundles.json').read_text())['bundles'][profile]
print(json.dumps({'profile':profile,'capabilities':b,'instruction':'load only these; escalate context gradually'},indent=2))
