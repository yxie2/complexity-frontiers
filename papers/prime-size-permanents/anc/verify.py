"""Exact finite checks of the algebraic identities, not dimension proofs."""
from collections import Counter
from itertools import permutations, product
from pathlib import Path
import hashlib, json, random

def coefficient_and_orbits(p):
    choices=[list(permutations([a for a in range(p) if a!=j]))
             for j in range(p) for h in range(p-1)]
    balanced=set()
    for family in product(*choices):
        exponents=[[0]*p for _ in range(p-1)]
        for sigma in family:
            for i,a in enumerate(sigma):exponents[i][a]+=1
        if all(v==p-1 for row in exponents for v in row):balanced.add(family)
    def translate(family):
        return tuple(tuple((a+1)%p for a in family[((j-1)%p)*(p-1)+h])
                     for j in range(p) for h in range(p-1))
    pending=set(balanced);orbits=[]
    while pending:
        first=min(pending);orbit=[];term=first
        while term not in orbit:
            assert term in balanced
            orbit.append(term);term=translate(term)
        assert term==first and len(orbit) in (1,p)
        pending.difference_update(orbit);orbits.append(len(orbit))
    factorial=1
    for a in range(1,p):factorial*=a
    assert orbits.count(1)==factorial**(p-1)
    assert len(balanced)%p==1
    return {'prime':p,'coefficient':len(balanced),
            'fixed_families':orbits.count(1),'orbit_sizes':dict(Counter(orbits))}

def rank_mod(rows,p):
    if not rows:return 0
    a=[row[:] for row in rows];r=0
    for col in range(len(a[0])):
        pivot=next((j for j in range(r,len(a)) if a[j][col]%p),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r]
        inv=pow(a[r][col]%p,-1,p);a[r]=[(x*inv)%p for x in a[r]]
        for j in range(len(a)):
            if j==r:continue
            v=a[j][col]%p;a[j]=[(x-v*y)%p for x,y in zip(a[j],a[r])]
        r+=1
        if r==len(a):break
    return r

def det_mod(a,p):
    n=len(a);out=0
    for sigma in permutations(range(n)):
        v=(-1)**sum(sigma[i]>sigma[j] for i in range(n) for j in range(i+1,n))
        for i,j in enumerate(sigma):v*=a[i][j]
        out+=v
    return out%p

def top_product(a,p):
    r=len(a);terms={(0,)*r:1}
    for row in a:
        for _ in range(p-1):
            nxt={}
            for mon,c in terms.items():
                for j,v in enumerate(row):
                    if not v or mon[j]+1>=p:continue
                    e=list(mon);e[j]+=1;e=tuple(e)
                    nxt[e]=(nxt.get(e,0)+c*v)%p
            terms={m:c for m,c in nxt.items() if c}
    return terms

def generator_changes():
    rng=random.Random(20260917);checks=[]
    for p in [2,3,5,7]:
        for r in [1,2,3,4]:
            for trial in range(8):
                a=[[rng.randrange(p) for _ in range(r)] for _ in range(r)]
                determinant=det_mod(a,p)
                target=pow(determinant,p-1,p)
                expected={(p-1,)*r:target} if target else {}
                assert top_product(a,p)==expected
                checks.append({'p':p,'r':r,'trial':trial,'invertible':bool(determinant)})
    return checks

def permanent(a,p):
    n=len(a);out=0
    for sigma in permutations(range(n)):
        v=1
        for i,j in enumerate(sigma):v*=a[i][j]
        out+=v
    return out%p

def small_fibers(p):
    n=p;counts=Counter();critical_count=0;base_count=0
    for entries in product(range(p),repeat=(p-1)*p):
        x=[list(entries[i*p:(i+1)*p]) for i in range(p-1)]
        ps=[permanent([[x[i][a] for a in range(p) if a!=j]
                       for i in range(p-1)],p) for j in range(p)]
        jac=[]
        for j in range(p):
            row=[]
            for i in range(p-1):
                for a in range(p):
                    row.append(0 if a==j else permanent(
                        [[x[k][b] for b in range(p) if b not in (a,j)]
                         for k in range(p-1) if k!=i],p))
            jac.append(row)
        rho=rank_mod(jac,p);actual=0
        for y in product(range(p),repeat=p):
            prediction=not any(ps) and all(sum(jac[j][i]*y[j] for j in range(p))%p==0
                                           for i in range((p-1)*p))
            a=x+[list(y)]
            direct=all(permanent([[a[k][b] for b in range(p) if b!=j]
                                  for k in range(p) if k!=i],p)==0
                       for i in range(p) for j in range(p))
            assert prediction==direct
            actual+=direct
        expected=0 if any(ps) else p**(p-rho)
        assert actual==expected
        if not any(ps):
            base_count+=1;counts[rho]+=1;critical_count+=actual
    return {'prime':p,'base_matrices_examined':p**((p-1)*p),
            'square_matrices_examined':p**(p*p),'base_points':base_count,
            'base_jacobian_rank_counts':dict(counts),'critical_points':critical_count,
            'warning':'These are finite-field counts, not geometric dimension calculations.'}


def fixed_point_checks():
    from math import factorial, isqrt
    cases=[]
    for p in range(2,200):
        if any(p%d==0 for d in range(2,isqrt(p)+1)): continue
        matrix_count=pow(p-1,p-1,p)
        family_count=pow(factorial(p-1),p-1,p)
        assert matrix_count==family_count==1
        cases.append({'prime':p,'fixed_matrix_residue':matrix_count,
                      'fixed_family_residue':family_count})
    return cases

def border_cofactor_checks():
    """Compare full integer monomial expansions, retaining border variables."""
    checks=[]
    for n in range(3,8):
        selected=0
        for i in range(1,n):
            for j in range(1,n):
                rows=[u for u in range(n) if u!=i]
                cols=[v for v in range(n) if v!=j]
                # Independent definition: all matchings of the complementary matrix.
                direct=Counter(tuple(sorted(zip(rows,sigma)))
                               for sigma in permutations(cols))
                bottom=[u for u in rows if u>0]
                right=[v for v in cols if v>0]
                expanded=Counter()
                leading=Counter()
                for sigma in permutations(right):
                    mon=tuple(sorted([(0,0),*zip(bottom,sigma)]))
                    expanded[mon]+=1
                    leading[mon]+=1
                for u in bottom:
                    for v in right:
                        remaining_rows=[r for r in bottom if r!=u]
                        remaining_cols=[s for s in right if s!=v]
                        for sigma in permutations(remaining_cols):
                            mon=tuple(sorted([(u,0),(0,v),*zip(remaining_rows,sigma)]))
                            expanded[mon]+=1
                assert direct==expanded
                degrees=Counter()
                observed_top=Counter()
                for mon,multiplicity in direct.items():
                    degree=sum(r>0 and s>0 for r,s in mon)
                    assert degree==(n-2 if (0,0) in mon else n-3)
                    degrees[degree]+=multiplicity
                    if degree==n-2:observed_top[mon]=multiplicity
                assert observed_top==leading
                selected+=1
        checks.append({'size':n,'selected_cofactors':selected,
                       'terms_per_cofactor_by_Y_degree':dict(sorted(degrees.items())),
                       'complete_expansion_equal':True,'leading_forms_equal':True})
    return checks

def main():
    results={'coefficient_orbit_checks':[coefficient_and_orbits(p) for p in [2,3]],
             'generator_change_checks':generator_changes(),
             'critical_fiber_checks':[small_fibers(p) for p in [2,3]],
             'fixed_point_checks':fixed_point_checks(),
             'border_cofactor_checks':border_cofactor_checks(),
             'scope':'Finite implementation checks only. All-prime claims and characteristic-zero deductions depend on the written proofs and cited theorems.'}
    results['canonical_sha256']=hashlib.sha256(json.dumps(results,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    Path(__file__).with_name('verification_results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'coefficients':results['coefficient_orbit_checks'],
        'generator_cases':len(results['generator_change_checks']),
        'border_cofactors':sum(c['selected_cofactors'] for c in results['border_cofactor_checks']),
        'fiber_counts':results['critical_fiber_checks'],'canonical_sha256':results['canonical_sha256']}))
if __name__=='__main__':
    if not __debug__: raise RuntimeError('Run without -O.')
    main()
