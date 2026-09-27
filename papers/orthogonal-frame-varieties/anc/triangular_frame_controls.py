"""Exact finite controls for Gale equations and the depth/normality family."""
from pathlib import Path
from math import comb, isqrt
from fractions import Fraction
from itertools import combinations
import hashlib,json,random,time

HERE=Path(__file__).resolve().parent;start=time.monotonic();rng=random.Random(2609260837)
p=1009

def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def tr(A):return [list(v) for v in zip(*A)]
def mul(A,B):
    Bt=tr(B)
    return [[sum(x*y for x,y in zip(a,b))%p for b in Bt] for a in A]
def det(A):
    A=[row[:] for row in A];d=1;n=len(A)
    for i in range(n):
        j=next((j for j in range(i,n) if A[j][i]%p),None)
        if j is None:return 0
        if j!=i:A[i],A[j]=A[j],A[i];d=-d
        v=A[i][i]%p;d=d*v%p;iv=pow(v,-1,p)
        for r in range(i+1,n):
            c=A[r][i]*iv%p
            for s in range(i+1,n):A[r][s]=(A[r][s]-c*A[i][s])%p
    return d%p
def inv(A):
    n=len(A);R=[row[:]+e for row,e in zip(A,eye(n))]
    for i in range(n):
        j=next(j for j in range(i,n) if R[j][i]%p)
        R[i],R[j]=R[j],R[i];v=pow(R[i][i]%p,-1,p)
        R[i]=[x*v%p for x in R[i]]
        for j in range(n):
            if i!=j:
                c=R[j][i]
                R[j]=[(x-c*y)%p for x,y in zip(R[j],R[i])]
    return [r[n:] for r in R]
def rref(A):
    A=[row[:] for row in A];piv=[];r=0
    for c in range(len(A[0])):
        j=next((j for j in range(r,len(A)) if A[j][c]%p),None)
        if j is None:continue
        A[r],A[j]=A[j],A[r];v=pow(A[r][c]%p,-1,p)
        A[r]=[x*v%p for x in A[r]]
        for j in range(len(A)):
            if j!=r:
                v=A[j][c]
                A[j]=[(x-v*y)%p for x,y in zip(A[j],A[r])]
        piv.append(c);r+=1
        if r==len(A):break
    return A,piv
def kernel1(A):
    R,piv=rref(A);n=len(A[0]);assert len(piv)==n-1
    c=next(c for c in range(n) if c not in piv);v=[0]*n;v[c]=1
    for i,j in enumerate(piv):v[j]=-R[i][c]%p
    return v
def E(Y):
    return [[row[i]*row[j]%p for row in Y] for i,j in combinations(range(len(Y[0])),2)]
def gale(Z,k):
    q=comb(k,2);A=[r[:q] for r in Z];d=det(A)
    if not d:raise ValueError('chart singular')
    Y=mul(inv(A),[r[q:] for r in Z])
    return pow(d,k+1,p)*det(E(Y))%p
def sign(perm):return -1 if sum(perm[i]>perm[j] for i in range(len(perm)) for j in range(i+1,len(perm)))%2 else 1

families=[];stratum_count=0
for k in range(3,31):
    q=comb(k,2);h=q+k;M=2*q;N=M*h-comb(h,2)
    assert 8*h+1==(2*k+1)**2
    # Published inequalities characterize the thresholds according to parity.
    # At even M: CI iff M>=2h+1-sqrt(8h+1), prime iff strict.
    assert M==2*h+1-isqrt(8*h+1)
    # At odd M+1 strict primality inequality, and M-1 fails CI.
    assert (2*h-(M+1))**2<8*h-7
    assert (2*h-(M-1))**2>8*h-7
    low=[]
    for t in range(h+1):
        for r in range(min(h-t,(M-t)//2)+1):
            D=M*t-t*(t-1)//2+r*(M+h-2*t-r)-r*(r+1)//2
            x=q-r;c=(2*k*x+t*t-4*t*x-t+3*x*x-x)//2
            assert c==N-D;stratum_count+=1
            if c<=1:low.append([t,r,c])
    expected=[[0,q,0],[h-1,1,1],[h,0,0]] if k>=4 else [[0,3,0],[2,2,1],[4,1,1],[5,0,1],[6,0,0]]
    assert low==expected
    b=Fraction(1)
    if k<=8:
        for i in range(1,q+1):
            for j in range(i+1,q+1):b*=Fraction(2*(k+1)+2*q-i-j,2*q-i-j)
        assert b.denominator==1
    families.append(dict(k=k,q=q,h=h,M=M,dimension=N,new_degree=q*(k+1),
                         new_generators=2*int(b) if k<=8 else None,low_codimension_strata=low))

gale_checks=[];boundary=[]
for k in range(3,9):
    q=comb(k,2);h=q+k;M=2*q
    Y=[]
    for i,j in combinations(range(k),2):
        row=[0]*k;row[i]=row[j]=1;Y.append(row)
    Z=[e+y for e,y in zip(eye(q),Y)]
    assert gale(Z,k)==1
    chart_cases=[]
    while len(chart_cases)<5:
        Z=[[rng.randrange(p) for j in range(h)] for i in range(q)]
        if not det([r[:q] for r in Z]):continue
        g=gale(Z,k);perm=list(range(h));rng.shuffle(perm)
        Zp=[[r[j] for j in perm] for r in Z]
        if not det([r[:q] for r in Zp]):continue
        assert gale(Zp,k)==g*sign(perm)**k%p
        chart_cases.append(dict(value=g,permuted_value=gale(Zp,k),parity=sign(perm)))
    # A rational Cayley construction reduced modulo p gives orthogonal frames.
    B=eye(M)[q:]+eye(M)[:q]
    while True:
        H=[[0]*M for _ in range(M)]
        for i,j in combinations(range(M),2):H[i][j]=rng.randrange(p);H[j][i]=-H[i][j]%p
        A=mul(B,H);minus=[[(int(i==j)-A[i][j])%p for j in range(M)] for i in range(M)]
        if not det(minus):continue
        plus=[[(int(i==j)+A[i][j])%p for j in range(M)] for i in range(M)]
        O=mul(inv(minus),plus)
        V0=[]
        for i in range(M):
            V0.append([int(i%q==j%q)*(1 if i<q or j<q else -1)%p for j in range(M)])
        V=[r[:h] for r in mul(O,V0)]
        D=mul(tr(V),mul(B,V))
        assert all(D[i][j]==0 for i in range(h) for j in range(h) if i!=j)
        assert all(D[i][i] for i in range(h))
        if det([r[:q] for r in V[:q]]):break
    assert gale(V[:q],k)==0
    gale_checks.append(dict(k=k,nonmembership_value=1,chart_changes=chart_cases,orthogonal_frame_equation_zero=True))
    # q points on the hollow quadric sum_(i<j) yi*yj=0.
    for attempt in range(100):
        Y=[]
        while len(Y)<q:
            row=[rng.randrange(1,p) for _ in range(k-1)];den=sum(row)%p
            if not den:continue
            row.append(-sum(row[i]*row[j] for i,j in combinations(range(k-1),2))*pow(den,-1,p)%p)
            assert sum(row[i]*row[j] for i,j in combinations(range(k),2))%p==0
            Y.append(row)
        E0=E(Y);_,piv=rref(E0)
        if len(piv)!=q-1:continue
        lam=kernel1(E0)
        mu=[sum(lam[r]*Y[r][j]**2 for r in range(q))%p for j in range(k)]
        if all(lam) and all(mu):break
    else:raise AssertionError('no boundary witness')
    boundary.append(dict(k=k,Y=Y,kernel=lam,norms=mu,rank=q-1,attempts=attempt+1))

out=dict(status='passed',prime=p,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         families=families,stratum_count=stratum_count,gale_checks=gale_checks,boundary_witnesses=boundary,
         seconds=time.monotonic()-start,
         scope='Exact arithmetic over integers/rationals for thresholds, Weyl products and dimensions; exact GF(1009) controls for Gale chart signs, vanishing on orthogonal frames and generic boundary conditions. All-size ideal and normality statements use the written proofs.')
(HERE/'triangular_frame_controls.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=out['status'],families=len(families),strata=stratum_count,gale_sizes=len(gale_checks),boundary_sizes=len(boundary),seconds=out['seconds'],producer_sha256=out['producer_sha256']),indent=2))
