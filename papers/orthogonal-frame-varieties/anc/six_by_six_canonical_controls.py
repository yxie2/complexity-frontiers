"""Exact controls for the 330-generator proof; no ideal-generation inference."""
from pathlib import Path
from fractions import Fraction
from math import comb, factorial
import hashlib, json, time
import sympy as s

HERE=Path(__file__).resolve().parent
start=time.monotonic()

def partitions3(m):
    for a in range(m,-1,-1):
        for b in range(min(a,m-a),-1,-1):
            c=m-a-b
            if 0<=c<=b: yield (a,b,c)

def weyl(part,n):
    part=tuple(part)+(0,)*(n-len(part))
    d=Fraction(1)
    for i in range(n):
        for j in range(i+1,n):d*=Fraction(part[i]-part[j]+j-i,j-i)
    assert d.denominator==1
    return int(d)

def coeff(num,m):
    return sum(a*comb(m-j+20,20) for j,a in enumerate(num) if m>=j)

hilbert=[]
for m in range(31):
    a=sum(weyl(l,6)*weyl((m,)+l,4) for l in partitions3(m))
    w=sum(weyl(l,6)*weyl((m+8,)+l,4) for l in partitions3(m))
    assert a==coeff([1,15,99,165],m)
    assert w==coeff([165,99,15,1],m)
    hilbert.append(dict(m=m,ring=a,canonical_degree=m+18,canonical=w))

aa=s.symbols('a1:4');tt=s.symbols('t1:4')
def cross(v):
    a,b,c=v
    return s.Matrix([[0,-c,b],[c,0,-a],[-b,a,0]])
A,T=cross(aa),cross(tt)
dot=sum(x*y for x,y in zip(aa,tt))
assert A*T==s.Matrix(tt)*s.Matrix(aa).T-dot*s.eye(3)
assert s.expand((s.eye(3)+A*T).det()-(1-dot)**2)==0
assert (A+T).det()==0
terms=[]
for n in range(9):
    for a in range(n+1):
        for b in range(n-a+1):
            c=n-a-b
            v=(-1)**n*factorial(8)//(factorial(8-n)*factorial(a)*factorial(b)*factorial(c))
            assert v
            terms.append(dict(alpha=[a,b,c],coefficient=v))
assert len(terms)==165

strata=[]
for t in range(7):
    for r in range((6-t)//2+1):
        d=6*t-t*(t-1)//2+r*(12-2*t-r)-r*(r+1)//2
        strata.append(dict(nonisotropic_columns=t,isotropic_rank=r,dimension=d,codimension=21-d))

num=[comb(15,j) for j in range(16)]
for j,v in enumerate([165,99,15,1]):num[12+j]-=2*v
assert sum(num)==32208
out=dict(status='passed',producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         hilbert_controls=hilbert,independence_coefficients=terms,
         strata=strata,principal_hilbert_numerator=num,principal_degree=sum(num),
         seconds=time.monotonic()-start,
         scope='Symbolic cross-product identities, coefficient independence constants, and 31 finite Weyl-dimension checks. Generation uses the separate canonical-module proof.')
(HERE/'six_by_six_canonical_controls.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=out['status'],coefficient_count=len(terms),hilbert_degrees=len(hilbert),degree=out['principal_degree'],seconds=out['seconds'],producer_sha256=out['producer_sha256']),indent=2))
