"""Independent exact expansion, root checks, and uniform formal sharpness."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
from itertools import combinations
from math import isqrt
from hashlib import sha256
from datetime import datetime,timezone
import json
from verify_field_sharpness import add,mul,scale,shift,norm,cross
HERE=Path(__file__).resolve().parent

def vp(n,p):
    assert n;k=0
    while n%p==0:n//=p;k+=1
    return k

def lift(f,root_valuation,p,precision=24):
    weights={e:vp(c,p)+e*root_valuation for e,c in f.items()};low=min(weights.values());mod=p**precision
    coeff={e:(c//p**vp(c,p))*pow(p,weights[e]-low,mod)%mod for e,c in f.items()}
    def value(x,m):return sum(c*pow(x,e,m) for e,c in coeff.items())%m
    def derivative(x,m):return sum(e*c*pow(x,e-1,m) for e,c in coeff.items() if e)%m
    roots=[x for x in range(1,p) if value(x,p)==0];assert len(roots)==1
    root=roots[0];assert derivative(root,p)!=0;power=p
    for _ in range(1,precision):
        residue=value(root,power*p);assert residue%power==0
        digit=(-(residue//power)*pow(derivative(root,p),-1,p))%p
        root+=digit*power;power*=p
    assert value(root,mod)==0 and derivative(root,p)!=0
    return {'valuation':root_valuation,'unit_mod_p24':str(root),'precision':precision}

def check_frozen(p):
    path=HERE/('SHARP_N6_U10_P%d.json'%p);data=json.loads(path.read_bytes())
    polys=[{int(e):int(c) for e,c in row} for row in data['inputs']]
    support=sorted(set().union(*(set(f) for f in polys)));assert support==[0,2,3,4,6,8]
    vectors={e:tuple(f.get(e,0) for f in polys) for e in support}
    norms={e:u*v+r*r for e,(u,v,r) in vectors.items()};nonzero={e:c for e,c in norms.items() if c}
    assert set(nonzero)=={3} and isqrt(nonzero[3])**2==nonzero[3]
    # Ordered scalar convolution, distinct from the builder's vector pairing.
    f=defaultdict(int)
    for e,c in polys[0].items():
        for h,d in polys[1].items():f[e+h]+=c*d
    for e,c in polys[2].items():
        for h,d in polys[2].items():f[e+h]+=c*d
    f={e:c for e,c in f.items() if c};table=[(e,vp(c,p)) for e,c in sorted(f.items())]
    base=[75,50,27,23,20,18,17,17,18,20,23,30] if p==2 else [63,42,23,19,16,14,13,13,14,16,19,26]
    shift0=2*vp(int(data['integer_scale']),p)
    assert table==[(e,h+shift0) for e,h in zip(list(range(2,13))+[14],base)]
    slopes=[F(b[1]-a[1],b[0]-a[0]) for a,b in zip(table,table[1:])]
    assert len(slopes)==11 and all(x<y for x,y in zip(slopes,slopes[1:])) and slopes[-1]==F(7,2)
    # Every candidate line supports every coefficient, and is strict away
    # from its two endpoints; this checks the whole hull, not just ordering.
    for (a,h),(b,k) in zip(table,table[1:]):
        for e,y in table:
            gap=(y-h)*(b-a)-(k-h)*(e-a)
            assert gap==0 if e in [a,b] else gap>0
    roots=[lift(f,-int(slope),p) for slope in slopes[:-1]]
    assert len(roots)==10 and len({r['valuation'] for r in roots})==10
    assert sum(len(f) for f in polys)==14
    return {'prime':p,'n':6,'k':1,'V':11,'U':10,'S':14,'roots':roots,'source':path.name,
            'sha256':sha256(path.read_bytes()).hexdigest(),'maximum_input_bits':max(abs(c).bit_length() for f in polys for c in f.values())}

def formal_unit_example():
    # Odd-characteristic / v(2)=0 recipe in Z[T,T^-1], after clearing
    # the two denominator factors, both with constant term one.
    R24=mul({0:1,34:-1,35:-1},{0:1,34:-1,35:-1})
    R28=mul({0:1,22:-1,23:-1},{0:1,22:-1,23:-1});D=mul(R24,R28)
    N4=add({0:1,16:-1},scale(shift(mul({0:1,19:-1},{0:1,19:-1}),36),-1))
    N8=add(scale(shift(R24,1),-1),scale(mul(N4,{0:1,15:-1},{0:1,15:-1}),-1))
    directions={0:{33:1},2:{33:1,34:1},4:{-1:1},6:{14:1},8:{11:1}}
    scales={0:shift(D,9),2:shift(D,-14),4:shift(mul(N4,R28),16),6:shift(D,-1),8:shift(N8,5)}
    vectors={i:(scale(mul(t,s,s),-1),t,mul(t,s)) for i,t in scales.items() for s in [directions[i]]}
    vectors[3]=({},scale(D,2),D)
    assert all(not norm(c) for i,c in vectors.items() if i!=3) and norm(vectors[3])==mul(D,D)
    out={}
    for i,c in vectors.items():out[2*i]=add(out.get(2*i,{}),norm(c))
    for i,j in combinations(sorted(vectors),2):out[i+j]=add(out.get(i+j,{}),cross(vectors[i],vectors[j]))
    out={e:p for e,p in out.items() if p};table=[]
    for e,p in sorted(out.items()):
        low=min(p);c=p[low];assert abs(c)&(abs(c)-1)==0
        table.append({'exponent':e,'valuation_in_vT_units':low,'leading_coefficient':c})
    assert [(r['exponent'],r['valuation_in_vT_units']) for r in table]==list(zip(list(range(2,13))+[14],[63,42,23,19,16,14,13,13,14,16,19,26]))
    assert min(D)==0 and D[0]==1
    return {'table':table,'denominator_constant_term':1,'scope':'Formal Laurent-polynomial identity with unit leading coefficients at every field where v(2)=0.'}

def main():
    rows=[check_frozen(p) for p in [2,3,5,7,11,17]]
    report={'at':datetime.now(timezone.utc).isoformat(),'status':'PASS','members':rows,'root_lifts':sum(len(r['roots']) for r in rows),
            'formal_v2_zero_sharpness':formal_unit_example(),
            'hashes':{p.name:sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'verify_field_sharpness.py']},
            'scope':'Exact frozen-input expansion and supporting-line checks; 60 simple root lifts to p^24; symbolic specialization for v(2)=0. Dyadic rational specialization covers v(2)>0. No constructor imported.'}
    (HERE/'UNIT10_EXAMPLES_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','primes':len(rows),'root_lifts':report['root_lifts'],'formal_sharpness':'PASS'}),flush=True)

if __name__=='__main__':main()
