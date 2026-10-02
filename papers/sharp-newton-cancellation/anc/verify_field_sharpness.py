"""Exact formal Laurent-polynomial verification of field-uniform sharpness.

For v(2)=0, every leading coefficient is a signed power of two, so the
formal T-adic table specializes to every field in question. For v(2)>0,
the dyadic rational recipe is checked by exact Fraction arithmetic.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
from itertools import combinations
from hashlib import sha256
from datetime import datetime,timezone
import json
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run this exact verifier without Python optimization flags.')

def add(*polys):
    out=defaultdict(int)
    for p in polys:
        for e,c in p.items():out[e]+=c
    return {e:c for e,c in out.items() if c}
def mul(*polys):
    out={0:1}
    for p in polys:
        nxt=defaultdict(int)
        for e,c in out.items():
            for f,d in p.items():nxt[e+f]+=c*d
        out={e:c for e,c in nxt.items() if c}
    return out
def scale(p,c):return {e:c*v for e,v in p.items() if c*v}
def shift(p,e):return {e+f:c for f,c in p.items()}
def mon(e,c=1):return {e:c}
def norm(c):return add(mul(c[0],c[1]),mul(c[2],c[2]))
def cross(c,d):return add(mul(c[0],d[1]),mul(c[1],d[0]),scale(mul(c[2],d[2]),2))
def check_slopes(table):
    slopes=[F(b[1]-a[1],b[0]-a[0]) for a,b in zip(table,table[1:])]
    assert all(x<y for x,y in zip(slopes,slopes[1:]))
    assert len(slopes)==11 and sum(b[0]-a[0]==1 for a,b in zip(table,table[1:]))==9
    return list(map(str,slopes))

def formal_odd():
    one={0:1};D24=mul({0:1,3:-1,56:-1},{0:1,3:-1,56:-1})
    D29=mul({0:1,3:-1,35:-1},{0:1,3:-1,35:-1});D=mul(D24,D29)
    dirs={0:mon(-7),2:mon(-3),4:{0:1,53:1},7:{0:1,28:1},9:{0:1,32:1}}
    # These are D*t_i, so all vector coordinates are Laurent polynomials.
    ts={0:shift(D,-35),2:shift(D,-3),4:shift(mul({0:1,26:-1},D29),9),7:shift(D,144),
        9:shift(add(scale(shift(D24,1),-1),scale(mul({0:1,26:-1},{0:1,25:-1},{0:1,25:-1}),-1)),218)}
    vectors={i:(scale(mul(t,s,s),-1),t,mul(t,s)) for i,t in ts.items() for s in [dirs[i]]}
    vectors[3]=({},scale(D,2),D)
    assert all(not norm(c) for i,c in vectors.items() if i!=3)
    assert norm(vectors[3])==mul(D,D)
    out={}
    for i,c in vectors.items():out[2*i]=add(out.get(2*i,{}),norm(c))
    for i,j in combinations(sorted(vectors),2):out[i+j]=add(out.get(i+j,{}),cross(vectors[i],vectors[j]))
    out={e:p for e,p in out.items() if p}
    table=[];leading=[]
    for e,p in sorted(out.items()):
        h=min(p);c=p[h];absolute=abs(c)
        assert absolute>0 and absolute&(absolute-1)==0,(e,h,c)
        table.append((e,h));leading.append({'exponent':e,'valuation_in_vT_units':h,'leading_coefficient':c,'laurent_terms':len(p)})
    expected=[(2,-52),(3,-49),(4,-40),(5,-9),(6,26),(7,62),(9,135),(10,172),(11,210),(12,250),(13,291),(16,418)]
    assert table==expected
    assert D[0]==1 and min(D)==0
    return {'table':leading,'slopes':check_slopes(table),'common_denominator_has_constant_term':1,
            'interpretation':'Leading coefficients are signed powers of 2. Therefore the table is valid whenever v(2)=0 and v(T)>0, including odd positive characteristic.'}

def vp2(x):
    def order(n):return (abs(n)&-abs(n)).bit_length()-1
    return order(x.numerator)-order(x.denominator)

def dyadic():
    T=F(2);s={0:T**-7,2:T**-3,4:1+T**53,7:1+T**28,9:1+T**33}
    t={0:T**-35,2:T**-3,7:T**147}
    t[4]=(1-T**26)/(t[2]*(s[2]-s[4])**2)
    t[9]=(-T**215-t[4]*t[7]*(s[4]-s[7])**2)/(t[2]*(s[2]-s[9])**2)
    vectors={i:(-t[i]*s[i]**2,t[i],t[i]*s[i]) for i in s};vectors[3]=(F(0),F(2),F(1))
    out=defaultdict(F)
    for i,c in vectors.items():
        d=c[0]*c[1]+c[2]**2;assert d==(1 if i==3 else 0);out[2*i]+=d
    for i,j in combinations(sorted(vectors),2):
        c,d=vectors[i],vectors[j];out[i+j]+=c[0]*d[1]+c[1]*d[0]+2*c[2]*d[2]
    table=[(e,vp2(c)) for e,c in sorted(out.items()) if c]
    expected=[(2,-52),(3,-48),(4,-40),(5,-8),(6,26),(7,63),(9,138),(10,176),(11,215),(12,255),(13,296),(16,424)]
    assert table==expected
    return {'table':table,'slopes':check_slopes(table),
            'interpretation':'If v(2)>0, characteristic is zero and v on Q is v(2) times the ordinary 2-adic valuation.'}

def main():
    out={'at':datetime.now(timezone.utc).isoformat(),'status':'PASS','v2_zero':formal_odd(),'v2_positive':dyadic(),
         'n':6,'k':1,'V':11,'U':9,'support':[0,2,3,4,7,9],
         'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'Formal exact arithmetic checks the two sharpness recipes; the accompanying field argument supplies the universal specialization.'}
    (HERE/'FIELD_SHARPNESS_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','cases':['v(2)=0','v(2)>0'],'V':11,'U':9}),flush=True)

if __name__=='__main__':main()
