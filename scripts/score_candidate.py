#!/usr/bin/env python3
import json,sys
x=json.load(open(sys.argv[1])); w={'quality':16,'maintenance':13,'security':14,'license':10,'documentation':8,'adoption':5,'uniqueness':9,'agentCompatibility':8,'installationSimplicity':4,'contextEfficiency':6,'determinism':4,'portability':3}; score=sum(float(x.get(k,0))/10*v for k,v in w.items()); print(json.dumps({'score':round(score,1),'decision':'candidate' if score>=75 else 'reference-or-reject'},indent=2))
