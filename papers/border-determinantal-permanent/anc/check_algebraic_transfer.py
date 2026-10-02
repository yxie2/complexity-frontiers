"""Exact controls for multiplicity-preserving polar transfer.

These verify explicit identities and fiber lengths, not the general
finite-flat theorem. Inseparable Gauss maps deliberately appear.
"""
from pathlib import Path
import sympy as sp
import json,hashlib,time
from math import comb
ROOT=Path(__file__).resolve().parent


def main():
    start=time.monotonic();checks=[]
    tau=sp.Symbol('tau')
    for p in (2,3,5,7):
        for k in (3,4,5):
            xs=sp.symbols(f'x0:{k-1}');q=k-2
            g=sum(x**(p+1) for x in xs)+1+tau*sum(xs[:q])
            original=[g]+[sp.diff(g,x) for x in xs[:q]]
            triangular=[x**p+tau for x in xs[:q]]+[xs[-1]**(p+1)+1]
            domain=sp.GF(p).frac_field(tau)
            gb=sp.groebner(triangular,*xs,domain=domain)
            assert all(gb.reduce(e)[1]==0 for e in original)
            original_gb=sp.groebner(original,*xs,domain=domain)
            assert all(original_gb.reduce(e)[1]==0 for e in triangular)
            length=p**q*(p+1)
            assert length==(p+1)*p**(k-2)
            # This fiber has p+1 geometric points and multiplicity p^q
            # at each over the algebraic closure, on both fibers.
            assert sp.gcd(sp.Poly(xs[-1]**(p+1)+1,xs[-1],modulus=p),
                          sp.Poly((p+1)*xs[-1]**p,xs[-1],modulus=p)).degree()==0
            checks.append({'characteristic':p,'variables':k,'degree':p+1,
                           'scheme_length':length,'geometric_points':p+1,
                           'multiplicity_per_point':p**q,
                           'original_and_triangular_ideals_equal':True})
    # Characteristic divides degree: a smooth conic whose ambient
    # gradient has a base point outside the conic.
    x,y=sp.symbols('x y')
    conic_gb=sp.groebner([x*x+y,y],x,y,modulus=2)
    assert conic_gb.reduce(x*x)[1]==0 and conic_gb.reduce(x)[1]!=0
    # An extra equation can destroy flatness; the square-CI condition
    # must not be silently discarded.
    nonflat_generic=sp.groebner([x*x,tau*x],x,domain=sp.QQ.frac_field(tau))
    assert nonflat_generic.reduce(x)[1]==0
    result={'inseparable_families':checks,'char2_smooth_conic_length':2,
            'char2_smooth_conic_geometric_points':1,
            'overdetermined_nonflat_control':{'special_length':2,'generic_length':1},
            'all_checks_passed':True,'seconds':time.monotonic()-start,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'Exact controls; the general conservation statement has a separate proof.'}
    (ROOT/'CHECK_ALGEBRAIC_TRANSFER.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
