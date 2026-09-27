"""Exact controls for equations of the orthogonal-basis component."""
from pathlib import Path
from itertools import combinations
import hashlib,json,random,time
import sympy as s

HERE=Path(__file__).resolve().parent;start=time.monotonic();rng=random.Random(2609260758)

def nu(Z):
    q,n=Z.shape
    pairs=[(i,i) for i in range(q)]+list(combinations(range(q),2))
    return s.Matrix(len(pairs),n,lambda r,j:Z[pairs[r][0],j]*Z[pairs[r][1],j])

controls=[]
for N in [6,8,9,10,11,12]:
    q=N//2;B=s.zeros(N);B[:q,q:2*q]=s.eye(q);B[q:2*q,:q]=s.eye(q)
    if N%2:B[-1,-1]=1
    Z=s.zeros(q,N)
    vectors=[s.eye(q)[:,i] for i in range(q)]+[s.eye(q)[:,i]+s.eye(q)[:,j] for i,j in combinations(range(q),2)]
    for j in range(N):Z[:,j]=vectors[j]
    V=s.zeros(N);V[:q,:]=Z
    assert V.T*B*V==s.zeros(N)
    W=nu(Z);minor=W[:N,:].det();assert minor==1
    controls.append(dict(N=N,q=q,gram_zero=True,veronese_minor=int(minor)))

# Exact rational orthogonal bases for the six-dimensional split form.
N=6;q=3;B=s.zeros(N);B[:q,q:]=s.eye(q);B[q:,:q]=s.eye(q)
V0=s.BlockMatrix([[s.eye(q),s.eye(q)],[s.eye(q),-s.eye(q)]]).as_explicit()
bases=[]
while len(bases)<12:
    K=s.zeros(N)
    for i,j in combinations(range(N),2):K[i,j]=rng.randrange(-2,3);K[j,i]=-K[i,j]
    A=B*K
    if (s.eye(N)-A).det()==0:continue
    O=(s.eye(N)-A).inv()*(s.eye(N)+A)
    assert O.T*B*O==B
    V=O*V0*s.diag(*[rng.choice([1,2,3]) for _ in range(N)])
    D=V.T*B*V
    assert D.is_diagonal() and D.det()!=0
    W=nu(V[:q,:]);inverse_norms=s.Matrix([1/D[i,i] for i in range(N)])
    assert W*inverse_norms==s.zeros(6,1)
    assert W.det()==0
    bases.append(dict(index=len(bases),kernel_verified=True,determinant_zero=True))

Z=s.Matrix([[1,0,0,1,1,0],[0,1,0,1,0,1],[0,0,1,0,1,1]])
V=Z.col_join(s.I*Z)
assert V.T*V==s.zeros(6)
pminus=nu(V[:3,:]-s.I*V[3:,:]).det()
pplus=nu(V[:3,:]+s.I*V[3:,:]).det()
assert pminus==4096 and pplus==0 and (pminus+pplus)/2==2048

out=dict(status='passed',isotropic_nonmembership_controls=controls,orthogonal_bases=bases,
         standard_form=dict(P_minus=int(pminus),P_plus=int(pplus),rational_equation_value=2048),
         seconds=time.monotonic()-start,
         producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         scope='Exact arithmetic controls; the proof on all orthogonal bases is the inverse-Gram identity.')
(HERE/'orthogonal_basis_veronese.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=out['status'],nonmembership_cases=len(controls),basis_cases=len(bases),standard_form=out['standard_form'],seconds=out['seconds'],producer_sha256=out['producer_sha256']),indent=2))
