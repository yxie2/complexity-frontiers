"""Exact finite arithmetic checks for the Gram estimates.

Enumerate small finite rings, compare Smith image lengths with kernels,
check the hollow Schur pivot, and verify exact one-variable Gauss norms.
"""
from collections import Counter
from fractions import Fraction
from itertools import product,combinations
from math import isqrt,comb
from pathlib import Path
from random import Random
import hashlib,json,time

HERE=Path(__file__).resolve().parent

def valuation(a,p,L):
    if not a:return L
    v=0
    while a%p==0:a//=p;v+=1
    return min(v,L)

def image_length(A,p,L):
    modulus=p**L; A=[[v%modulus for v in row] for row in A];n=len(A);total=0
    while n:
        v,i,j=min((valuation(A[i][j],p,L),i,j) for i in range(n) for j in range(n))
        if v==L:break
        A[0],A[i]=A[i],A[0]
        for row in A:row[0],row[j]=row[j],row[0]
        scale=p**v;inv=pow(A[0][0]//scale,-1,modulus//scale)
        for i in range(1,n):
            multiplier=(A[i][0]//scale)*inv%(modulus//scale)
            for j in range(1,n):A[i][j]=(A[i][j]-multiplier*A[0][j])%modulus
        A=[row[1:] for row in A[1:]];n-=1;total+=L-v
    return total

def matrices(n,modulus,hollow):
    pairs=list(combinations(range(n),2)) if hollow else [(i,j) for i in range(n) for j in range(i,n)]
    for entries in product(range(modulus),repeat=len(pairs)):
        A=[[0]*n for _ in range(n)]
        for (i,j),v in zip(pairs,entries):A[i][j]=A[j][i]=v
        yield A

def schur_hollow(A,modulus):
    a=A[0][1];inv=pow(a,-1,modulus);n=len(A)
    return [[(A[i][j]-inv*(A[i][0]*A[1][j]+A[i][1]*A[0][j]))%modulus for j in range(2,n)] for i in range(2,n)]

def floor_radical(b,a):
    lo,hi=-b,b
    while lo<hi:
        mid=(lo+hi+1)//2;t=b-2*mid
        if t>=0 and t*t>=a:lo=mid
        else:hi=mid-1
    return lo

def prime_threshold(h):
    return min(2*floor_radical(2*h+1,8*h+1)+2,2*floor_radical(2*h+1,8*h-7)+1)

def threshold(h):
    r=max(2,(isqrt(1+8*h)-1)//2)
    if r*(r+1)<2*h:r+=1
    r=min(r,h)
    return Fraction(2*h-r+1)-Fraction(2*h,r),r

def check_thresholds():
    maximum=20000;bad=set()
    for k in range(4,isqrt(2*maximum)+4):bad.update(range(comb(k,2)+2,min(maximum,k*k//2)+1))
    examples=[]
    for h in range(2,maximum+1):
        F,r=threshold(h);rat=F.numerator//F.denominator+1;prime=prime_threshold(h)
        assert rat==prime+(h in bad),(h,F,rat,prime)
        assert rat>=h
        if h<=600:assert F==max(Fraction(2*h-a+1)-Fraction(2*h,a) for a in range(2,h+1))
        # When the last bad integral dimension is already prime, the
        # maximal-isotropic first-jet excess is nonnegative.
        M=rat-1
        if M>=prime:
            q=M//2;k=h-q;e=comb(h,2);N=M*h-e
            stratum=q*h+q*(q+1)//2
            delta=comb(k,2)-q
            assert M%2==1 and 0<stratum<N and stratum+delta>=N
            assert stratum+delta-N==k*k-2*h
        if h<=30:examples.append(dict(h=h,F=str(F),maximizer=r,prime_threshold=prime,rational_threshold=rat))
    # Check the proposed lct minimization and its isotropic witness.
    checks=0
    for h in range(2,151):
        e=comb(h,2)
        for M in range(1,2*h+4):
            value=min([Fraction(e)]+[Fraction(comb(k+1,2))+Fraction(M*(h-k),2) for k in range(h-1)])
            q=M//2
            explicit=Fraction(e)
            if q<=h-2:
                tau=Fraction(q*h-comb(q,2)) if M%2==0 else Fraction((2*q+1)*h-q*q,2)
                explicit=min(explicit,tau)
                if tau<e:
                    k=h-q;delta=comb(k,2)-q;b=e-delta
                    if M%2==0:
                        assert tau==M*h-(q*h+comb(q,2))
                    else:
                        stratum=q*h+comb(q+1,2)
                        assert 2*tau==2*M*h-(stratum+M*h-b)
            assert value==explicit,(h,M,value,explicit)
            checks+=1
    return dict(maximum_h=maximum,lct_pairs=checks,examples=examples)

def check_necessity(maximum=600):
    """Compare the direct parity obstruction with F(h), without prime thresholds."""
    pairs=0;even_obstructions=0;odd_obstructions=0;boundary=[]
    for h in range(2,maximum+1):
        F=max(Fraction(2*h-r+1)-Fraction(2*h,r) for r in range(2,h+1))
        assert F<=2*h-3
        for M in range(h,2*h-2):
            q=M//2;r=h-q;e=comb(h,2);N=M*h;n=N-e
            assert q<=h-2
            tau2=2*q*h-q*(q-1) if M%2==0 else M*h-q*q
            assert (tau2<=2*e)==(M<=F),(h,M,F,tau2)
            stratum=q*h+q*(q-1)//2 if M%2==0 else q*h+q*(q+1)//2
            delta=comb(r,2)-q
            if M%2==0:
                assert 2*(stratum-n)==2*e-tau2
                if M<=F:
                    assert stratum>=n
                    even_obstructions+=1
            else:
                assert stratum+n+delta-2*n==2*e-tau2
                if M<=F:
                    assert stratum+n+delta>=2*n
                    odd_obstructions+=1
            if M==F and len(boundary)<12:
                boundary.append(dict(h=h,M=M,dimension=n,stratum_dimension=stratum,
                                     first_jet_lower_bound=stratum+n+delta if M%2 else None))
            pairs+=1
    return dict(maximum_h=maximum,pairs=pairs,even_obstructions=even_obstructions,
                odd_obstructions=odd_obstructions,boundary_examples=boundary,
                prime_threshold_formula_used=False)

def check_products_gauss():
    records=[]
    for p,L in [(3,1),(3,2),(3,3),(3,4),(5,1),(5,2),(5,3),(7,2)]:
        modulus=p**L;counts=Counter((a*b)%modulus for a in range(modulus) for b in range(modulus))
        assert max(counts.values())<=(L+1)*modulus
        for a in [0,1,2,p,p**(L-1)]:
            a%=modulus;values=Counter(a*x*x%modulus for x in range(modulus));norm=[0]*modulus
            for u,c in values.items():
                for v,d in values.items():norm[(u-v)%modulus]+=c*d
            expected=p**(L+valuation(a,p,L));norm[0]-=expected
            period=p**(L-1)
            # A polynomial of degree <p^L vanishes at a primitive p^L
            # root iff these coefficient columns are constant.
            assert all(len({norm[r+j*period] for j in range(p)})==1 for r in range(period))
        records.append(dict(p=p,length=L,product_max=max(counts.values()),product_bound=(L+1)*modulus,gauss_coefficients_checked=5))
    return records

def check_matrices():
    rng=Random(270927);records=[];kernel_checks=0;pivot_checks=0
    for n,p,L in [(2,3,3),(3,3,2),(3,5,1),(4,3,1),(4,3,2)]:
        modulus=p**L;hist=Counter();unit_hist=Counter();count=0
        for A in matrices(n,modulus,True):
            rho=image_length(A,p,L);hist[rho]+=1;count+=1
            if any(a%p for row in A for a in row):unit_hist[rho]+=1
            if A[0][1]%p:
                S=schur_hollow(A,modulus)
                assert rho==2*L+image_length(S,p,L)
                assert all((S[j][j]+2*A[j+2][0]*A[j+2][1]*pow(A[0][1],-1,modulus))%modulus==0 for j in range(n-2))
                pivot_checks+=1
            if count<=5 or (n<=3 and rng.randrange(50)==0):
                kernel=sum(all(sum(A[i][j]*v[j] for j in range(n))%modulus==0 for i in range(n)) for v in product(range(modulus),repeat=n))
                assert kernel*p**rho==modulus**n
                kernel_checks+=1
        # Verify the actual hollow unit mass bound against an independently
        # enumerated symmetric residual, for integral s=1,2,3.
        k=n-2;symmetric=Counter(image_length(S,p,L) for S in matrices(k,modulus,False)) if k else Counter({0:1})
        masses=[]
        for s in (1,2,3):
            actual=sum(Fraction(c,p**(s*r)) for r,c in unit_hist.items())
            residual=sum(Fraction(c,p**(s*r)) for r,c in symmetric.items())
            bound=comb(n,2)*(L+1)**k*Fraction(p)**((n-1-2*s)*L)*residual
            assert actual<=bound
            masses.append(dict(s=s,actual=str(actual),pivot_bound=str(bound)))
        records.append(dict(h=n,p=p,length=L,matrices=count,image_length_histogram=dict(sorted(hist.items())),unit_mass_checks=masses))
        print(json.dumps(dict(completed_h=n,p=p,length=L,matrices=count)),flush=True)
    return dict(records=records,kernel_checks=kernel_checks,hollow_pivot_checks=pivot_checks)

def main():
    start=time.monotonic()
    result=dict(thresholds=check_thresholds(),necessity=check_necessity(),
                products_and_gauss=check_products_gauss(),matrices=check_matrices())
    result.update(status='PASS',seconds=time.monotonic()-start,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      scope='Exact threshold arithmetic, scalar identities, and finite-ring matrix counts.')
    (HERE/'gram_fourier_arithmetic_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'],kernel_checks=result['matrices']['kernel_checks'],pivot_checks=result['matrices']['hollow_pivot_checks'])))

if __name__=='__main__':main()
