"""Exact coefficient and polynomial-identity checks for the manuscript."""
from collections import Counter
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial, isqrt
from pathlib import Path
from time import monotonic
import json

class Poly:
    def __init__(self,value):self.data=value if isinstance(value,dict) else ({(0,0):value} if value else {})
    def __add__(self,other):
        other=other if isinstance(other,Poly) else Poly(other);out=Counter(self.data)
        for a,c in other.data.items():out[a]+=c
        return Poly({a:c for a,c in out.items() if c})
    __radd__=__add__
    def __neg__(self):return Poly({a:-c for a,c in self.data.items()})
    def __sub__(self,other):return self+-other if isinstance(other,Poly) else self+(-other)
    def __rsub__(self,other):return -self+other
    def __mul__(self,other):
        other=other if isinstance(other,Poly) else Poly(other);out=Counter()
        for a,c in self.data.items():
            for b,d in other.data.items():out[tuple(x+y for x,y in zip(a,b))]+=c*d
        return Poly({a:c for a,c in out.items() if c})
    __rmul__=__mul__
    def __pow__(self,n):
        out=Poly(1)
        for _ in range(n):out=out*self
        return out


def P(n,k):return 4*k**3+(6-18*n)*k**2+(26*n**2-15*n)*k+10*n**2-12*n**3
def f(n,k):return comb(n,k)**2*comb(2*k,k)*comb(2*n-2*k,n-k) if 0<=k<=n else 0
def g(n,k):return comb(n+k,3*k)*comb(2*k,k)**2*comb(3*k,k)*4**(n-2*k) if 0<=2*k<=n else 0
def r(n,k):return F(k**3*P(n,k),n**2*(2*n-2*k-1))
def s(n,k):return F(-12*(3*n-2)*k**4,(n+k)*(n+k-1))


def quartic():
    out=Counter()
    for sigma in permutations(range(4)):
        if any(i==j for i,j in enumerate(sigma)):continue
        sign=(-1)**sum(sigma[i]>sigma[j] for i in range(4) for j in range(i+1,4))
        state={(0,0,0,0):sign}
        for i,j in enumerate(sigma):
            terms=[k for k in range(4) if k not in (i,j)];next=Counter()
            for e,c in state.items():
                for k in terms:
                    f=list(e);f[k]+=1;next[tuple(f)]+=c
            state=next
        out.update(state)
    return {e:c for e,c in out.items() if c}


def coefficient(D,p):
    units=[1<<(8*i) for i in range(4)]
    terms=[(sum(k*u for k,u in zip(e,units)),c%p) for e,c in D.items() if c%p]
    state={0:1};peak=0
    for k in range(1,p):
        next={};lo=max(0,2*k-(p-1))
        for e,c in state.items():
            for f,v in terms:
                g=e+f
                if any(not lo<=((g>>(8*j))&255)<=p-1 for j in range(4)):continue
                next[g]=(next.get(g,0)+c*v)%p
        state={e:c for e,c in next.items() if c};peak=max(peak,len(state))
    target=sum((p-1)*u for u in units);assert set(state).issubset({target})
    return state.get(target,0),peak


def count(p):
    start=monotonic()
    points=[(1,a,b) for a in range(p) for b in range(p)]+[(0,1,a) for a in range(p)]+[(0,0,1)]
    m=len(points);lookup={v:i for i,v in enumerate(points)};inverse=[0]+[pow(a,-1,p) for a in range(1,p)]
    def normalize(v):
        a=next((x for x in v if x),0)
        return tuple(x*inverse[a]%p for x in v) if a else None
    masks=[]
    for a,b,c in points:
        mask=0
        for j,(x,y,z) in enumerate(points):
            if (a*x+b*y+c*z)%p:mask|=1<<j
        masks.append(mask)
    T=[[0]*m for _ in range(m)]
    for i,(a,b,c) in enumerate(points):
        for j in range(i,m):
            x,y,z=points[j]
            v=normalize(((b*z+c*y)%p,(a*z+c*x)%p,(a*y+b*x)%p))
            T[i][j]=T[j][i]=masks[lookup[v]] if v is not None else 0
    total=0;triples=0
    for a in range(m):
        Ta=T[a]
        for b in range(a,m):
            mask_ab=Ta[b];Tb=T[b]
            for c in range(b,m):
                if not (mask_ab>>c)&1:continue
                triples+=1
                common=mask_ab&Ta[c]&Tb[c]
                if a==b==c:w_dist,w_same=4,1
                elif a==b:w_dist,w_same=12,6
                elif b==c:w_dist,w_same=12,4
                else:w_dist,w_same=24,12
                total+=(common>>(c+1)).bit_count()*w_dist+((common>>c)&1)*w_same
    return {'prime':p,'projective_columns':m,'ordered_good_column_tuples':total,
            'coefficient':total%p,'good_sorted_triples':triples,'seconds':monotonic()-start}


