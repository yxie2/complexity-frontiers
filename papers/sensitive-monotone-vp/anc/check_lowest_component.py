"""Check sharing-preserving least-component extraction by exact expansion."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import random
import time

ROOT = Path(__file__).resolve().parent
SEED = 202609151245
ZERO = (0,0,0,0)


def add(a,b):
    c=dict(a)
    for e,x in b.items():
        c[e]=c.get(e,F(0))+x
    return {e:x for e,x in c.items() if x}


def mul(a,b):
    c={}
    for e,x in a.items():
        for f,y in b.items():
            g=tuple(u+v for u,v in zip(e,f))
            c[g]=c.get(g,F(0))+x*y
    return {e:x for e,x in c.items() if x}


def expand(nodes):
    values=[]
    for node in nodes:
        if node[0]=='v':
            e=list(ZERO);e[node[1]]=1
            values.append({tuple(e):F(1)})
        elif node[0]=='c':
            values.append({ZERO:node[1]} if node[1] else {})
        else:
            op=add if node[0]=='+' else mul
            values.append(op(values[node[1]],values[node[2]]))
    return values


def extract(nodes):
    # Degree metadata is computed from the DAG, not from expanded polynomials.
    output=[('c',F(0))]
    mapping=[];degrees=[]
    for node in nodes:
        op=node[0]
        if op in ('v','c'):
            if op=='c' and node[1]==0:
                mapping.append(0);degrees.append(None)
            else:
                mapping.append(len(output));output.append(node)
                degrees.append(1 if op=='v' else 0)
            continue
        left,right=node[1:]
        dl,dr=degrees[left],degrees[right]
        if op=='*' and (dl is None or dr is None):
            mapping.append(0);degrees.append(None)
        elif op=='+' and (dl is None or dr is None):
            chosen=right if dl is None else left
            mapping.append(mapping[chosen]);degrees.append(degrees[chosen])
        elif op=='+' and dl!=dr:
            chosen=left if dl<dr else right
            mapping.append(mapping[chosen]);degrees.append(degrees[chosen])
        else:
            mapping.append(len(output))
            output.append((op,mapping[left],mapping[right]))
            degrees.append(dl if op=='+' else dl+dr)
    assert sum(n[0] in ('+','*') for n in output)<=sum(n[0] in ('+','*') for n in nodes)
    return output,mapping,degrees


def main():
    start=time.monotonic();rng=random.Random(SEED)
    checked=shared_products=0
    for trial in range(400):
        nodes=[('v',j) for j in range(4)]+[('c',x) for x in (F(0),F(1,3),F(1),F(2))]
        maxdeg=[1]*4+[0]*4
        for i in range(24):
            l=rng.randrange(len(nodes))
            r=l if rng.randrange(4)==0 else rng.randrange(len(nodes))
            op='*' if rng.randrange(2)==0 and maxdeg[l]+maxdeg[r]<=7 else '+'
            nodes.append((op,l,r))
            maxdeg.append(maxdeg[l]+maxdeg[r] if op=='*' else max(maxdeg[l],maxdeg[r]))
            shared_products+=int(op=='*' and l==r)
        original=expand(nodes)
        extracted,mapping,degrees=extract(nodes)
        values=expand(extracted)
        for i,p in enumerate(original):
            d=min((sum(e) for e in p),default=None)
            low={e:x for e,x in p.items() if sum(e)==d}
            assert degrees[i]==d
            assert values[mapping[i]]==low
            checked+=1

    # A large formal-degree fixture with repeated shared squaring.
    nodes=[('v',0),('*',0,0),('+',0,1)]
    for _ in range(6):
        j=len(nodes)-1;nodes.append(('*',j,j))
    original=expand(nodes)[-1]
    extracted,mapping,degrees=extract(nodes)
    low=expand(extracted)[mapping[-1]]
    assert degrees[-1]==64 and low=={(64,0,0,0):F(1)}
    assert max(sum(e) for e in original)==128

    # The cube need not force the original output to be multilinear.
    grid=0
    for i in range(11):
        for j in range(11):
            x,y=F(i,10),F(j,10)
            target=x*y;approx=target+target**2
            assert target/2<=approx<=2*target
            grid+=1
    assert F(1,10)**4 < F(1,10)**2/2
    result={
        'status':'PASS','checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'seed':SEED,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'manuscript_sha256':hashlib.sha256((ROOT.parent/'main.tex').read_bytes()).hexdigest(),
        'circuits':400,'gate_components_checked':checked,
        'random_self_shared_products':shared_products,
        'large_degree_fixture':{'least_degree':64,'maximum_degree':128},
        'nonmultilinear_cube_example_grid_points':grid,
        'incorrect_highest_component_approximation_rejected':True,
        'elapsed_seconds':time.monotonic()-start,
        'scope':'Exact finite circuit expansions check the extraction and sharing accounting. The continuum scaling and asymptotic lower bound are analytic proofs in the manuscript.'
    }
    (ROOT/'LOWEST_COMPONENT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
