"""Exact polynomial and finite-field controls for the isotropic chart."""
from pathlib import Path
from itertools import combinations
import hashlib, json, random, time
import sympy as s

HERE=Path(__file__).resolve().parent
start=time.monotonic(); rng=random.Random(2609260747)

def symbolic(q,k,m):
    Y=s.Matrix(q,k,s.symbols(f'y0:{q*k}'))
    C=s.Matrix(m,q,s.symbols(f'c0:{m*q}'))
    Z=s.Matrix(m,k,s.symbols(f'z0:{m*k}'))
    lam=s.diag(*s.symbols(f'l0:{q}'))
    skew=s.zeros(q)
    for a,b in combinations(range(q),2):
        x=s.Symbol(f'a{a}_{b}');skew[a,b]=x;skew[b,a]=-x
    H=skew+(lam-C.T*C)/2
    W=Z+C*Y;T=-H.T*Y-C.T*W
    first=H+H.T+C.T*C
    cross=T+H.T*Y+C.T*W
    gram=Y.T*T+T.T*Y+W.T*W
    target=Z.T*Z-Y.T*lam*Y
    assert all(s.expand(x)==0 for x in first-lam)
    assert all(s.expand(x)==0 for x in cross)
    assert all(s.expand(x)==0 for x in gram-target)
    return dict(q=q,k=k,m=m,entries_checked=q*q+q*k+k*k)

checks=[symbolic(*t) for t in [(1,2,0),(1,3,1),(2,2,1),(2,3,2),(3,4,1),(4,4,1)]]

# A generic-rank witness works over every field, not just large primes.
rank_checks=[]
for k in range(2,12):
    edges=list(combinations(range(k),2));e=len(edges)
    for q in sorted(set([1,min(k,e),max(1,e-k+2),e])):
        Y=s.zeros(q,k)
        for r,(i,j) in enumerate(edges[:q]):Y[r,i]=Y[r,j]=1
        E=s.Matrix(e,q,lambda a,r:Y[r,edges[a][0]]*Y[r,edges[a][1]])
        assert E[:q,:]==s.eye(q)
        assert E[q:,:]==s.zeros(e-q,q)
        rank_checks.append(dict(k=k,q=q,unit_minor=True))

# Explicit singular rank-(h-2) point and its nondegenerate tangent plane.
V=s.zeros(5,4);V[:2,:2]=s.eye(2);V[:2,2:]=s.eye(2)
B=s.zeros(5);B[:2,2:4]=s.eye(2);B[2:4,:2]=s.eye(2);B[4,4]=1
u=s.Matrix([-1,0,1,0]);v=s.Matrix([0,-1,0,1]);K=u*v.T+v*u.T
assert V*K==s.zeros(5,4) and all(K[i,i]==0 for i in range(4))
J=s.zeros(6,20)
for r,(i,j) in enumerate(combinations(range(4),2)):
    for c in range(5):
        J[r,4*c+i]=(B*V[:,j])[c];J[r,4*c+j]=(B*V[:,i])[c]
assert J.rank()==5
a,b=s.symbols('a b');W=s.zeros(5,4);W[4,2]=a;W[4,3]=b
flat=s.Matrix([W[c,j] for c in range(5) for j in range(4)])
assert J*flat==s.zeros(6,1)
quad=sum(K[i,j]*(W[:,i].T*B*W[:,j])[0] for i,j in combinations(range(4),2))
assert s.expand(quad)==a*b

out=dict(status='passed',symbolic_chart_checks=checks,unit_rank_controls=rank_checks,
         local_rank_h_minus_2=dict(M=5,h=4,jacobian_rank=5,residual_tangent_quadratic=str(quad)),
         seconds=time.monotonic()-start,
         producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         scope='Exact chart identities, unit rank witnesses, and one tangent-plane control; the uniform proof is separate.')
(HERE/'orthogonal_transverse_chart.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=out['status'],symbolic_cases=len(checks),rank_cases=len(rank_checks),seconds=out['seconds'],producer_sha256=out['producer_sha256']),indent=2))
