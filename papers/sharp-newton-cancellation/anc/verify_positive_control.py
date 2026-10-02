"""Evaluate the certificate rules on a real equality example, using Fractions."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from collections import defaultdict
from hashlib import sha256
from datetime import datetime,timezone
import json
from certificate_system import make_system,GRID,PAIRS
from verify_sharp_six import RuleAudit,verify_tree
HERE=Path(__file__).resolve().parent

def val(x):return (abs(x)&-abs(x)).bit_length()-1

def main():
    source=HERE/'sharpness_witness.json'
    data=json.loads(source.read_bytes());inputs=[{int(e):int(c) for e,c in row} for row in data['inputs']]
    A=sorted(set().union(*(set(p) for p in inputs)));v=[tuple(p.get(e,0) for p in inputs) for e in A]
    norm=lambda c:c[0]*c[1]+c[2]*c[2]
    cross=lambda c,d:c[0]*d[1]+c[1]*d[0]+2*c[2]*d[2]
    a=next(i for i,c in enumerate(v) if norm(c));d=val(norm(v[a]));primary=(1,3);tilt=-25
    groups=defaultdict(list)
    for e in PAIRS:groups[sum(A[i] for i in e)].append(e)
    gs=sorted(tuple(g) for g in groups.values());case={'anchor':a,'primary':primary,'groups':gs,'unmarked_indices':[]}
    output=defaultdict(int)
    for i,c in enumerate(v):output[2*A[i]]+=norm(c)
    for i,j in PAIRS:output[A[i]+A[j]]+=cross(v[i],v[j])
    heights={e:val(c)-d+tilt*(e-2*A[a]) for e,c in output.items() if c}
    exps=sorted(heights);slopes=[F(heights[y]-heights[x],y-x) for x,y in zip(exps,exps[1:])]
    assert len(slopes)==11 and all(x<y for x,y in zip(slopes,slopes[1:]))
    def boundary(x):
        if x<exps[0]:return heights[exps[0]]+(x-exps[0])*min(slopes[0]-1,F(-1))
        if x>exps[-1]:return heights[exps[-1]]+(x-exps[-1])*max(slopes[-1]+1,F(1))
        j=next(j for j in range(len(exps)-1) if exps[j]<=x<=exps[j+1])
        return heights[exps[j]]+(x-exps[j])*slopes[j]
    values={'epsilon':1}|{'A%d'%i:x for i,x in enumerate(A)}
    values.update({'w%d%d'%e:val(cross(v[e[0]],v[e[1]]))-d+tilt*(sum(A[i] for i in e)-2*A[a]) for e in PAIRS})
    values.update({'h%d%d'%e:boundary(sum(A[i] for i in e)) for e in GRID})
    values.update({'H%d'%r:heights[sum(A[i] for i in g[0])] for r,g in enumerate(gs)})
    def holds(c):
        z=sum(factor*values[name] for name,factor in c['form'].items())
        return z==0 if c['kind']=='eq' else z>0 if c['strict'] else z>=0
    axioms,clauses=make_system(case,True);audit=RuleAudit(case)
    for c in axioms:audit.axiom(c);assert holds(c),c
    for c in clauses:audit.clause(c);assert any(all(holds(v) for v in option) for option in c['options']),c
    # Negative controls ensure the exact contradiction checker rejects empty,
    # wrong-sign, and false arithmetic certificates.
    negative=[({'multipliers':[]},[]),({'multipliers':[[0,1]]},[{'kind':'ge','strict':True,'form':{'x':1}}]),
              ({'multipliers':[[0,-1],[1,-1]]},[{'kind':'ge','strict':True,'form':{'x':1}},{'kind':'ge','strict':True,'form':{'x':-1}}])]
    for proof,rows in negative:
        rejected=False
        try:verify_tree(proof,rows,[])
        except AssertionError:rejected=True
        assert rejected
    out={'at':datetime.now(timezone.utc).isoformat(),'status':'PASS','axioms':len(axioms),'clauses':len(clauses),
         'negative_controls_rejected':len(negative),'witness_sha256':sha256(source.read_bytes()).hexdigest(),
         'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'Exact positive control for all rule families on an eleven-edge formula; negative controls for arithmetic rejection. Universal rule validity relies on the written proof.'}
    (HERE/'CERTIFICATE_POSITIVE_CONTROL.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
