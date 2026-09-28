"""Direct Gram-fiber counts and exact finite Fourier inversion.

Both Z/p^L and F_p[t]/t^L are covered. Direct counts use only vector dot
products and intersections of bit sets; the Fourier side uses independently
implemented elimination and cyclotomic reduction.
"""
from collections import Counter
from fractions import Fraction
from itertools import product, combinations
from pathlib import Path
import hashlib, json, time

HERE = Path(__file__).resolve().parent

class Ring:
    def __init__(self, p, length, kind):
        self.p, self.length, self.kind = p, length, kind
        self.n = p ** length
        self.digits = [tuple((a // p**i) % p for i in range(length)) for a in range(self.n)]
        def add(a, b):
            if kind == 'integer': return (a+b) % self.n
            return sum(((x+y) % p)*p**i for i,(x,y) in enumerate(zip(self.digits[a],self.digits[b])))
        def mul(a, b):
            if kind == 'integer': return a*b % self.n
            x,y=self.digits[a],self.digits[b]
            return sum((sum(x[j]*y[i-j] for j in range(i+1)) % p)*p**i for i in range(length))
        self.add=[[add(a,b) for b in range(self.n)] for a in range(self.n)]
        self.mul=[[mul(a,b) for b in range(self.n)] for a in range(self.n)]
        self.neg=[next(b for b in range(self.n) if self.add[a][b]==0) for a in range(self.n)]
        self.inv={a:next(b for b in range(self.n) if self.mul[a][b]==1) for a in range(self.n) if a%p}
        self.val=[next((i for i,d in enumerate(ds) if d),length) for ds in self.digits]
        self.char_mod=self.n if kind=='integer' else p

    def dot(self, x, y):
        out=0
        for a,b in zip(x,y): out=self.add[out][self.mul[a][b]]
        return out

    def char_exponent(self, a):
        return a if self.kind=='integer' else self.digits[a][-1]

    def image_length(self, matrix):
        A=[row[:] for row in matrix]; out=0
        while A:
            n=len(A)
            v,i,j=min((self.val[A[i][j]],i,j) for i in range(n) for j in range(n))
            if v==self.length: break
            A[0],A[i]=A[i],A[0]
            for row in A: row[0],row[j]=row[j],row[0]
            pivot_unit=A[0][0]//self.p**v
            for i in range(1,n):
                multiple=self.mul[A[i][0]//self.p**v][self.inv[pivot_unit]]
                for j in range(1,n):
                    A[i][j]=self.add[A[i][j]][self.neg[self.mul[multiple][A[0][j]]]]
            A=[row[1:] for row in A[1:]]
            out+=self.length-v
        return out

def direct_counts(ring, M, h, targets):
    vectors=list(product(range(ring.n),repeat=M)); n=len(vectors)
    masks=[[0]*ring.n for _ in vectors]
    for i,x in enumerate(vectors):
        for j,y in enumerate(vectors): masks[i][ring.dot(x,y)] |= 1<<j
    all_mask=(1<<n)-1; pairs=list(combinations(range(h),2))
    results=[]
    for target in targets:
        constraints=dict(zip(pairs,target))
        def count(chosen):
            k=len(chosen); allowed=all_mask
            for i,index in enumerate(chosen): allowed &= masks[index][constraints[i,k]]
            if k==h-1: return allowed.bit_count()
            total=0
            while allowed:
                low=allowed & -allowed; allowed ^= low
                total+=count(chosen+[low.bit_length()-1])
            return total
        results.append(count([]))
    return results

def fourier_counts(ring, M, h, targets):
    assert M%2==0
    pairs=list(combinations(range(h),2)); e=len(pairs)
    coefficients=[[Fraction(0) for _ in range(ring.char_mod)] for _ in targets]
    histogram=Counter()
    # Even M eliminates the determinant character of the scalar Gauss sums.
    minus_one_character=1 if ring.p%4==1 else -1
    for entries in product(range(ring.n),repeat=e):
        A=[[0]*h for _ in range(h)]
        for (i,j),a in zip(pairs,entries): A[i][j]=A[j][i]=a
        rho=ring.image_length(A); histogram[rho]+=1
        weight=Fraction(minus_one_character**((M//2)*rho),ring.p**((M//2)*rho))
        for target, coeff in zip(targets,coefficients):
            exponent=ring.char_exponent(ring.neg[ring.dot(entries,target)])
            coeff[exponent]+=weight
    out=[]
    for coeff in coefficients:
        period=ring.char_mod//ring.p
        # Reduce modulo Phi_(p^a)(z)=sum_j z^(j*p^(a-1)).
        for i in range(period):
            top=coeff[i+(ring.p-1)*period]
            for j in range(ring.p-1): coeff[i+j*period]-=top
        reduced=coeff[:(ring.p-1)*period]
        assert all(x==0 for x in reduced[1:]), reduced
        result=reduced[0]*ring.p**(ring.length*(M*h-e))
        assert result.denominator==1
        out.append(int(result))
    return out,dict(sorted(histogram.items()))

def main():
    start=time.monotonic(); records=[]
    cases=[(3,1,'integer',4,4),(5,1,'integer',2,4),
           (3,2,'integer',2,3),(3,2,'polynomial',2,3),
           (3,2,'integer',4,3),(3,2,'polynomial',4,3)]
    for p,L,kind,M,h in cases:
        ring=Ring(p,L,kind); e=h*(h-1)//2
        targets=[[0]*e,[1]*e,[(i+1)%ring.n for i in range(e)]]
        if L>1: targets.append([p]*e)
        direct=direct_counts(ring,M,h,targets)
        predicted,hist=fourier_counts(ring,M,h,targets)
        assert direct==predicted,(p,L,kind,M,h,direct,predicted)
        rec=dict(p=p,length=L,ring=kind,M=M,h=h,targets=targets,
                 direct_counts=direct,fourier_counts=predicted,image_length_histogram=hist)
        records.append(rec)
        print(json.dumps(rec),flush=True)
    result=dict(status='PASS',records=records,seconds=time.monotonic()-start,
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Direct enumeration and Fourier counts for the prescribed finite-ring fibers.')
    (HERE/'direct_gram_count_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'])),flush=True)

if __name__=='__main__': main()
