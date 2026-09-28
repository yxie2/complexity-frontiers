"""First-jet counts in odd ambient dimensions.

The geometric route lists ordinary orthogonal frames over F_p and sums
the cardinalities of their tangent spaces. The Fourier route enumerates
hollow matrices over F_p[t]/t^2, using symmetric congruence diagonalization
and exact quadratic Gauss signs. No floating point arithmetic is used.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib, json, time
from check_direct_gram_counts import Ring

HERE=Path(__file__).resolve().parent

def field_rank(matrix,p):
    A=[row[:] for row in matrix]; r=0
    for col in range(len(A[0]) if A else 0):
        pivot=next((i for i in range(r,len(A)) if A[i][col]%p),None)
        if pivot is None: continue
        A[r],A[pivot]=A[pivot],A[r]
        inv=pow(A[r][col],-1,p)
        A[r]=[a*inv%p for a in A[r]]
        for i in range(r+1,len(A)):
            c=A[i][col]
            if c: A[i]=[(a-c*b)%p for a,b in zip(A[i],A[r])]
        r+=1
        if r==len(A): break
    return r

def geometric_count(p,M,h):
    vectors=list(product(range(p),repeat=M)); n=len(vectors)
    masks=[]
    for x in vectors:
        mask=0
        for j,y in enumerate(vectors):
            if sum(a*b for a,b in zip(x,y))%p==0: mask |= 1<<j
        masks.append(mask)
    pairs=list(combinations(range(h),2)); histogram=Counter()
    def visit(chosen):
        if len(chosen)==h:
            cols=[vectors[i] for i in chosen]; jac=[]
            for i,j in pairs:
                row=[0]*(M*h)
                for a in range(M):
                    row[M*i+a]=cols[j][a]
                    row[M*j+a]=cols[i][a]
                jac.append(row)
            histogram[field_rank(jac,p)]+=1
            return
        allowed=(1<<n)-1
        for i in chosen: allowed &= masks[i]
        while allowed:
            low=allowed&-allowed; allowed^=low
            visit(chosen+[low.bit_length()-1])
    visit([])
    jets=sum(count*p**(M*h-rank) for rank,count in histogram.items())
    return jets,dict(sorted(histogram.items()))

def symmetric_diagonal(A,ring):
    """Diagonal entries, retaining all valuation factors, by congruence."""
    A=[row[:] for row in A]; diag=[]
    while A:
        n=len(A); v=min(ring.val[a] for row in A for a in row)
        if v==ring.length: break
        i=next((i for i in range(n) if ring.val[A[i][i]]==v),None)
        if i is None:
            i,j=next((i,j) for i in range(n) for j in range(i+1,n) if ring.val[A[i][j]]==v)
            # Replace basis vector e_i by e_i+e_j.
            for row in range(n): A[row][i]=ring.add[A[row][i]][A[row][j]]
            for col in range(n): A[i][col]=ring.add[A[i][col]][A[j][col]]
            assert ring.val[A[i][i]]==v
        A[0],A[i]=A[i],A[0]
        for row in A: row[0],row[i]=row[i],row[0]
        pivot=A[0][0]; diag.append(pivot)
        divisor=ring.p**v; unit=pivot//divisor
        A=[[ring.add[A[i][j]][ring.neg[ring.mul[ring.mul[A[i][0]//divisor][ring.inv[unit]]][A[0][j]]]]
            for j in range(1,n)] for i in range(1,n)]
    return diag

def fourier_zero_count(p,M,h):
    assert M%2==1
    ring=Ring(p,2,'polynomial'); pairs=list(combinations(range(h),2))
    histogram=Counter(); odd_rho=0
    for entries in product(range(ring.n),repeat=len(pairs)):
        A=[[0]*h for _ in range(h)]
        for (i,j),a in zip(pairs,entries): A[i][j]=A[j][i]=a
        diagonal=symmetric_diagonal(A,ring)
        rho=sum(2-ring.val[a] for a in diagonal)
        if rho%2:
            # Scaling by a nonsquare pairs these terms with their negatives
            # for odd M; the target is zero. This is not used for nonzero targets.
            odd_rho+=1
            continue
        odd_units=[a//p for a in diagonal if ring.val[a]==1]
        sign=1
        if p%4==3: sign*=(-1)**(len(odd_units)//2)
        for a in odd_units:
            legendre=pow((a*pow(2,-1,p))%p,(p-1)//2,p)
            sign*=1 if legendre==1 else -1
        histogram[(rho,sign)]+=1
    normalized=sum(Fraction(sign*count,p**(M*rho//2)) for (rho,sign),count in histogram.items())
    value=normalized*Fraction(p)**(2*(M*h-len(pairs)))
    assert value.denominator==1
    return int(value),{str(key):value for key,value in sorted(histogram.items())},odd_rho

def main():
    start=time.monotonic(); records=[]
    for p,M,h in [(3,1,4),(3,3,3),(3,3,4),(5,3,3)]:
        geometric,ranks=geometric_count(p,M,h)
        fourier,hist,odd=fourier_zero_count(p,M,h)
        assert geometric==fourier,(p,M,h,geometric,fourier)
        rec=dict(p=p,M=M,h=h,direct_first_jet_count=geometric,
                 fourier_count=fourier,ordinary_jacobian_rank_histogram=ranks,
                 even_image_length_gauss_sign_histogram=hist,odd_image_length_terms_canceled=odd)
        records.append(rec);print(json.dumps(rec),flush=True)
    result=dict(status='PASS',records=records,seconds=time.monotonic()-start,
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='First-jet counts from Jacobian ranks and signed Fourier inversion.')
    (HERE/'odd_gram_first_jet_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'])),flush=True)

if __name__=='__main__': main()
