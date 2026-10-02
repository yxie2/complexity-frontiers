"""Independent exact controls for the polar/matching composition.

These checks support algebraic identities and parameter arithmetic only.
They do not establish the asymptotic theorem or certify novelty.
"""
from pathlib import Path
from itertools import combinations, permutations
from math import factorial,comb,prod
import random,json,hashlib,time
import sympy as sp

ROOT=Path(__file__).resolve().parent


def permanent_mod(A,p):
    n=len(A)
    if not n:return 1
    assert all(len(row)==n for row in A)
    sums=[0]*n;previous=0;answer=0
    for number in range(1,1<<n):
        gray=number^(number>>1);changed=gray^previous
        column=changed.bit_length()-1
        direction=1 if gray&changed else -1
        for i in range(n):sums[i]=(sums[i]+direction*A[i][column])%p
        term=prod(sums)%p
        answer+=(1 if (n-gray.bit_count())%2==0 else -1)*term
        previous=gray
    return answer%p


def matching_mod(X,d,p):
    t=len(X);s=len(X[0])
    return sum(prod(X[i][a] for i,a in zip(I,js))
               for I in combinations(range(t),d)
               for J in combinations(range(s),d)
               for js in permutations(J))%p


def selector_checks():
    p=1009;generator=int(sp.primitive_root(p));rng=random.Random(260915)
    cases=[];minor_checks=0;full_checks=0
    for b,t,d,s in [(1,6,3,5),(2,3,2,3),(3,3,2,3),
                     (3,4,3,4),(2,5,4,5),(3,4,4,4),(2,6,6,6)]:
        r=b*t;zeta=pow(generator,(p-1)//d,p)
        assert pow(zeta,d,p)==1 and all(pow(zeta,j,p)!=1 for j in range(1,d))
        columns=[]
        for h in range(b):
            for _ in range(t-d):columns.append([int(i//t==h) for i in range(r)])
        for h in range(1,b):
            for j in range(d):
                columns.append([(1 if i//t<h else 2*pow(zeta,j,p) if i//t==h else 0)%p for i in range(r)])
        U=[[column[i] for column in columns] for i in range(r)]
        assert len(columns)==r-d
        theta=(-1)**(d+1)*2**d
        weights=[theta**(b-1)]+[theta**(b-h)*(1+theta)**(h-2) for h in range(2,b+1)]
        assert all(w%p for w in weights)
        factor=factorial(t-d)*factorial(t)**(b-1)
        for I in combinations(range(r),d):
            omitted=set(I);used=[i for i in range(r) if i not in omitted]
            value=permanent_mod([U[i] for i in used],p)
            blocks={i//t for i in I}
            expected=0 if len(blocks)>1 else factor*weights[next(iter(blocks))]%p
            assert value==expected,(b,t,d,I,value,expected)
            minor_checks+=1
        for trial in range(2):
            X=[[rng.randrange(p) for _ in range(s)] for _ in range(r)]
            B=[X[i]+U[i] for i in range(r)]+[[1]*s+[0]*(r-d) for _ in range(s-d)]
            lhs=permanent_mod(B,p)
            rhs=sum(weights[h]*matching_mod(X[h*t:(h+1)*t],d,p) for h in range(b))
            rhs=rhs*factor*factorial(s-d)%p
            assert lhs==rhs,(b,t,d,s,trial,lhs,rhs)
            full_checks+=1
        cases.append({'b':b,'t':t,'d':d,'s':s,'permanent_order':r+s-d})
    return {'prime':p,'all_minor_checks':minor_checks,'full_matrix_checks':full_checks,'cases':cases}


def partitions(items):
    if not items:
        yield []
        return
    first,*rest=items
    for part in partitions(rest):
        yield [(first,)]+part
        for j in range(len(part)):
            yield part[:j]+[(first,)+part[j]]+part[j+1:]


def moment_checks():
    rng=random.Random(260916);p=1009;checks=0;leading=[]
    for q in range(2,6):
        parts=list(partitions(list(range(q))))
        coefficient=sum((-1)**len(part)*prod((-1)**(len(B)-1)*factorial(len(B)-1) for B in part) for part in parts)
        assert coefficient==(-1)**q*factorial(q)
        leading.append({'q':q,'partitions':len(parts),'leading_coefficient':coefficient})
        t=q+1;s=q+2
        X=[[rng.randrange(p) for _ in range(s)] for _ in range(t)]
        moments={B:sum(prod(X[i][a] for i in B) for a in range(s))%p
                 for k in range(1,q+1) for B in combinations(range(t),k)}
        for i in range(t):
            for a in range(s):
                value=0
                for I in combinations([j for j in range(t) if j!=i],q):
                    for part in parts:
                        term=1
                        for block in part:
                            B=tuple(sorted(I[j] for j in block))
                            mu=(-1)**(len(B)-1)*factorial(len(B)-1)
                            term*=mu*(moments[B]-prod(X[j][a] for j in B))
                        value+=term
                Y=[[X[j][c] for c in range(s) if c!=a] for j in range(t) if j!=i]
                assert value%p==matching_mod(Y,q,p)
                checks+=1
    return {'partition_gradient_checks':checks,'leading_terms':leading}


def binomial(n,k):return comb(n,k) if 0<=k<=n else 0


def bezout(m,k):
    return sum(binomial(m,a)*binomial(m-1,k-1-a)*binomial(k-2,a-1) for a in range(1,k))


def polar_checks():
    H,U,V=sp.symbols('H U V');brackets=0;envelopes=0
    for m in range(1,8):
        for k in range(3,8):
            poly=sp.Poly(H*(H+U)**m*(H+V)**(m-1)*(U+V)**(k-2),H,U,V)
            assert poly.coeff_monomial(H**k*U**(m-1)*V**(m-1))==bezout(m,k)
            brackets+=1
    for m in range(1,101):
        for k in range(3,42):
            assert bezout(m,k)<=2**(k-2)*binomial(2*m-1,k-1)
            envelopes+=1
    assert bezout(2,4)==2 # det_2 is a smooth quadric in four variables.
    assert bezout(3,4)>=3*2**2
    assert bezout(3,9)==0 # Full det_3 is singular; smoothness cannot be dropped.
    return {'symbolic_brackets':brackets,'envelope_checks':envelopes,
            'det2_control':{'k':4,'d':2,'m':2,'polar_points':2,'bezout':2},
            'det3_full_smoothness_negative_control':True}


def parameter_checks():
    checks=0;examples=[]
    for L in range(16,4097):
        for n in sorted({1<<L,(1<<L)+1,(1<<L)+(1<<(L-1)),(1<<(L+1))-2,(1<<(L+1))-1}):
            actual=n.bit_length()-1
            t=actual//2;d=actual//4;s=n//2;b=(n-s+d)//t;r=b*t
            K=b*(s*(t-d+2)-2**t+1);k=n*n//16
            assert r+s-d<=n and 3<=d<=min(t,s)
            assert 2**t<=2*s and 8*r>=3*n and 3*s>=n
            assert 16*K>=n*n and K>=k and 32*(k-1)>=n*n
            assert 8*(d-1)>=actual+1
            checks+=1
            if L in (16,20,32) and n==1<<L:
                examples.append({'n':n,'t':t,'d':d,'s':s,'b':b,'K':K,'k':k})
    return {'integer_boundary_cases':checks,'maximum_log2_scale':4096,'examples':examples}


def schur_check():
    a,b,c,d,p,q,r,s,z=sp.symbols('a b c d p q r s z')
    B=sp.Matrix([[a,b],[c,d]]);column=sp.Matrix([p,q]);row=sp.Matrix([[r,s]])
    M=B.row_join(column).col_join(sp.Matrix([[r,s,z]]))
    left=(-row*B.inv()).row_join(sp.ones(1,1))
    right=(-B.inv()*column).col_join(sp.ones(1,1))
    g=z-(row*B.inv()*column)[0]
    assert all(sp.simplify(v)==0 for v in left*M-sp.Matrix([[0,0,g]]))
    assert all(sp.simplify(v)==0 for v in M*right-sp.Matrix([0,0,g]))
    zvalue=(row*B.inv()*column)[0]
    assert all(sp.simplify(v.subs(z,zvalue))==0 for v in M.adjugate()-B.det()*right*left)
    return {'generic_3_by_3_schur_identity':True,'adjugate_kernel_pairing':True}


def main():
    start=time.monotonic()
    result={'scope':'Finite exact controls, not a proof or novelty certification.',
            'selector':selector_checks(),'moments':moment_checks(),
            'polar':polar_checks(),'parameters':parameter_checks(),'schur':schur_check(),
            'status':'passed','seconds':time.monotonic()-start}
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT/'CHECK_POLAR_COMPOSITION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
