#!/usr/bin/env python3
import pathlib,json,sys
p=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); (p/'.vibe').mkdir(exist_ok=True); files={x.name for x in p.iterdir()}; lang=[]
for f,n in [('package.json','javascript/typescript'),('pyproject.toml','python'),('Cargo.toml','rust'),('go.mod','go'),('CMakeLists.txt','c/c++')]:
    if f in files: lang.append(n)
(p/'.vibe/project.json').write_text(json.dumps({'languages':lang,'profile':'minimal'},indent=2)+'\n')
if not (p/'AGENTS.md').exists(): (p/'AGENTS.md').write_text('# Project agent context\n\nUse global `vibe_start`; keep project-specific conventions here.\n')
