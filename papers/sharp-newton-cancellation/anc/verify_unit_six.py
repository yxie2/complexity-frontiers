"""Solver-free coverage and proof check for the six-support U<=10 bound."""
from pathlib import Path
from itertools import combinations
from collections import defaultdict
from hashlib import sha256
from datetime import datetime,timezone
import json
from certificate_system import make_system
from verify_sharp_six import RuleAudit,verify_tree,case_key
HERE=Path(__file__).resolve().parent

def main():
    needed={};supports=[]
    # V<=11 and eleven unit edges force the output span to be eleven.
    # A_5-A_0<=8 because A_4-A_1>=3 for six distinct integer exponents.
    for tail in combinations(range(1,9),5):
        A=(0,)+tail;groups=defaultdict(list)
        for e in combinations(range(6),2):groups[A[e[0]]+A[e[1]]].append(e)
        if sorted(groups)!=list(range(min(groups),min(groups)+12)):continue
        supports.append(A);gs=sorted(tuple(g) for g in groups.values())
        for a in [1,2]:
            for primary in combinations(range(6),2):
                if sum(A[i] for i in primary)==2*A[a]:
                    case={'anchor':a,'primary':primary,'groups':gs,'unmarked_indices':[]}
                    needed[(A,a,primary)]=case_key(case)
    assert len(supports)==4 and len(needed)==10
    path=HERE/'UNIT_SIX_PROOFS.json';manifest=json.loads(path.read_bytes());seen=set();nodes=leaves=0
    for row in manifest['rows']:
        key=(tuple(row['support']),row['anchor'],tuple(row['primary']));assert key in needed and key not in seen;seen.add(key)
        raw=(HERE/row['proof']).read_bytes();assert sha256(raw).hexdigest()==row['sha256'];data=json.loads(raw)
        assert row['status']==data['status']=='certified' and case_key(data['case'])==needed[key]
        assert data['system_sha256']==sha256((HERE/'certificate_system.py').read_bytes()).hexdigest()
        axioms,clauses=make_system(data['case'],data['barycenter']);audit=RuleAudit(data['case'])
        for c in axioms:audit.axiom(c)
        for c in clauses:audit.clause(c)
        n,l=verify_tree(data['proof'],axioms,clauses);assert n==data['nodes'] and l==data['leaves'];nodes+=n;leaves+=l
    assert seen==set(needed)
    out={'at':datetime.now(timezone.utc).isoformat(),'status':'PASS','supports':supports,'primary_cases':len(needed),
         'proof_nodes':nodes,'farkas_leaves':leaves,'bound':'n=6,k=1 implies U<=10',
         'hashes':{p.name:sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),path,HERE/'verify_sharp_six.py',HERE/'certificate_system.py']},
         'scope':'Exact certificate verification; reduction uses the separately proved V<=11 theorem and preservation of unit edges under generic perturbation.'}
    (HERE/'UNIT_SIX_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out),flush=True)

if __name__=='__main__':main()
