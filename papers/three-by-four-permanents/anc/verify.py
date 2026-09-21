"""Run exact checks of the identities used in the three-by-four paper."""
from verification_support import Poly, P, f, g, r, s, quartic, coefficient, count
from fractions import Fraction
from math import comb, factorial, isqrt
from pathlib import Path
import json

def domb(n):
    return sum(comb(n,k)**2*comb(2*k,k)*comb(2*n-2*k,n-k) for k in range(n+1))

def constant_term(n):
    total=0
    for a in range(n+1):
        for b in range(n-a+1):
            for c in range(n-a-b+1):
                d=n-a-b-c
                total+=(factorial(n)//(factorial(a)*factorial(b)*factorial(c)*factorial(d)))**2
    return total

def verify_telescopers():
    n=Poly({(1,0):1}); k=Poly({(0,1):1}); h=n-k
    B=2*(2*n-1)*(5*n*(n-1)+2)
    left=2*(2*k+1)*h**3*P(n,k+1)-2*k**3*(2*h-3)*P(n,k)
    right=2*n**5*(2*h-1)*(2*h-3)-B*h**3*(2*h-3)+32*(n-1)*h**3*(h-1)**3
    assert (left-right).data=={}
    h=n-2*k; C=-12*(3*n-2)
    left=C*((n+k-1)*(2*k+1)*h*(h-1)-8*k**4)
    right=8*n**3*(n+k)*(n+k-1)-2*B*h*(n+k-1)+32*(n-1)**3*h*(h-1)
    assert (left-right).data=={}
    checks=0
    for n in range(2,61):
        B=2*(2*n-1)*(5*n*(n-1)+2)
        for term, cert, limit in [(f,r,n),(g,s,n//2)]:
            assert cert(n,0)*term(n,0)==cert(n,limit+1)*term(n,limit+1)==0
            for k in range(limit+1):
                assert n**3*term(n,k)-B*term(n-1,k)+64*(n-1)**3*term(n-2,k)==cert(n,k+1)*term(n,k+1)-cert(n,k)*term(n,k)
                checks+=1
        assert sum(f(n,k) for k in range(n+1))==sum(g(n,k) for k in range(n//2+1))
    assert f(0,0)==g(0,0)==1
    assert sum(f(1,k) for k in range(2))==g(1,0)==4
    return {'polynomial_identities':2,'summand_checks':checks,'maximum_degree':60}

def main():
    D=quartic()
    expected={}
    for i in range(4):
        for j in range(4):
            if i==j: continue
            e=[1]*4; e[i]=2; e[j]=0
            expected[tuple(e)]=-4
    assert D==expected
    assert all(constant_term(n)==domb(n) for n in range(13))
    values=[domb(n) for n in range(200)]
    residues=[]
    for p in range(3,200,2):
        if any(p%d==0 for d in range(2,isqrt(p)+1)): continue
        observed=sum(values[n]*pow(4,-n,p) for n in range(p))%p
        predicted=comb((p-1)//2,(p-1)//6)**2%p if p%6==1 else 0
        assert observed==predicted
        if p<=19:
            direct,peak=coefficient(D,p)
            assert direct==observed
        residues.append({'prime':p,'coefficient':observed})
    projective=[]
    for p in (3,5,7,11,13,17,19):
        result=count(p)
        predicted=comb((p-1)//2,(p-1)//6)**2%p if p%6==1 else 0
        assert result['coefficient']==predicted
        result.pop('seconds')
        projective.append(result)
    result={'status':'PASS','quartic_integer_identity':True,
        'constant_term_degrees':list(range(13)),
        'telescoping_checks':verify_telescopers(),
        'prime_coefficient_checks':residues,
        'independent_projective_column_counts':projective,
        'scope':'Exact finite coefficient controls and two complete polynomial-identity expansions. Geometric and general proof steps remain in the manuscript.'}
    Path(__file__).with_name('verification_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS:',len(residues),'prime residues;',result['telescoping_checks'],';',len(projective),'projective counts')

if __name__=='__main__':
    if not __debug__: raise RuntimeError('Run without -O.')
    main()
