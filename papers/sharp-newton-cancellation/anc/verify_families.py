"""Exact checks for the five-support bound and the all-size family."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from fractions import Fraction as F
from math import lcm
from itertools import permutations
import json
from polynomial_arithmetic import load, expand, order, hull, counts
from verify_unit10_examples import lift

HERE = Path(__file__).resolve().parent
if not __debug__:
    raise RuntimeError('Run without Python optimization flags.')


def read(name):
    path = HERE / 'family_examples' / name
    return json.loads(path.read_bytes()), {'source': path.relative_to(HERE).as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()}


def vectors(polys):
    return {e: tuple(f.get(e, F(0)) for f in polys) for e in sorted(set().union(*map(set, polys)))}


def polys(v):
    return [{e: row[i] for e, row in v.items() if row[i]} for i in range(3)]


def core_vertices(prime):
    head = [(1,371),(2,294),(3,219),(5,146),(6,110),(7,75)] if prime == 2 else [(1,369),(2,292),(3,217),(5,144),(6,108),(7,75)]
    end = [(15,-9),(16,-10),(17,-10),(18,-9),(19,-6)] if prime == 2 else [(15,-7),(16,-8),(17,-8),(18,-7),(19,-4)]
    return head + [(8,61),(9,48),(10,36),(11,25),(12,15),(13,6),(14,-2)] + end


def polynomial_tail_checks():
    # Exact coefficient identities plus monotonicity certify the unbounded
    # integer ranges; the below-core comparisons are genuinely finite.
    finite = 0
    differences = [(0,-79,20),(1,-96,19),(2,-43,18),(4,54,16),(7,160,13),(8,191,12)]
    for prime in [2,3]:
        hc = 113 if prime == 2 else 114
        constants = [220,145,144,145,137,138] if prime == 2 else [219,144,143,144,138,139]
        boundary = dict(core_vertices(prime))
        for (i, constant, start), C in zip(differences, constants):
            linear = -6-4*i
            actual_constant = hc+C-2*i*i+60*i-412
            expected_constant = constant + (2 if prime != 2 and i in [7,8] else 0)
            assert actual_constant == expected_constant
            value = lambda j: 2*j*j+linear*j+actual_constant
            assert value(start) > (2 if prime != 2 else 0)
            assert 4*start+2+linear > 0
            for j in range(11,start):
                margin = 4*j*j-66*j+hc+C-boundary[j+i]
                assert margin > 0, (prime,i,j,margin)
                finite += 1
        # The (9,j) formula and the odd-prime exceptional height at 20.
        C9 = 141 if prime == 2 else 142
        assert hc+C9-2*81+60*9-412 == 220+(0 if prime==2 else 2)
        assert 4*121-66*11+hc+C9 == (12 if prime==2 else 14)
        # Minimum of the tail-tail quadratic: unique nearest allowed integer.
        # For e=2m and i=m-1+d the excess is 8d^2-4d;
        # for e=2m+1 and i=m+d it is 8d^2+4d.
        # Both are positive for every nonzero integer d.
        for parity in [0,1]:
            for m in [11,12]:
                e=2*m+parity; i=m-1 if parity==0 else m; j=e-i
                assert 4*i*i+4*j*j-54*i-66*j+416 == 2*e*e-60*e+412
        # All determinant terms of the four-by-four core system.
        M=[[145,220,None,None],[144,145,220,None],[None,144,145,220],[142,None,144,145]]
        if prime!=2:M=[[None if x is None else x-1 for x in row] for row in M]
        terms=[(sum(M[i][j] for i,j in enumerate(perm)),perm) for perm in permutations(range(4)) if all(M[i][j] is not None for i,j in enumerate(perm))]
        minimum=min(v for v,_ in terms)
        assert [(v,perm) for v,perm in terms if v==minimum]==[(580 if prime==2 else 576,(0,1,2,3))]
    return {'unbounded_tail_polynomial_ranges':12,'finite_core_comparisons':finite,'core_determinant_patterns':2}


def main():
    sources=[]; five=[]; families=[]; roots=0
    for prime in [2,3,5,7,11,17]:
        data,source=read(f'SHARP_N5_UNIT_COMPACT_P{prime}.json');sources.append(source)
        g=load(data['inputs']);v=vectors(g);f=expand(g);D=int(data['integer_scale'])
        shift=2*order(F(D),prime)
        expected=[(e,h+shift) for e,h in zip(range(2,11),[17,11,7,4,2,1,1,2,5])]
        assert hull(f,prime)==expected and counts(expected)==(8,8)
        assert len(v)==5 and sum(map(len,g))==11
        assert {e:x*y+z*z for e,(x,y,z) in v.items() if x*y+z*z}=={3:D*D}
        integer_f={e:int(c) for e,c in f.items()};assert all(F(integer_f[e])==c for e,c in f.items())
        for a,b in zip(expected,expected[1:]):lift(integer_f,a[1]-b[1],prime);roots+=1
        five.append({'prime':prime,'n':5,'k':1,'V':8,'U':8,'S':11})

        data,source=read(f'STRONGER_N8_U16_P{prime}.json');sources.append(source)
        base=vectors(load(data['rational_inputs']));D=int(data['integer_scale']);T=F(prime)
        integer_core=load(data['inputs']);core=core_vertices(prime)
        assert hull(expand(integer_core),prime)==[(e,h+2*order(F(D),prime)) for e,h in core]
        core_f={e:int(c) for e,c in expand(integer_core).items()}
        for a,b in zip(core,core[1:]):
            if b[0]-a[0]==1:lift(core_f,a[1]-b[1],prime);roots+=1
        for n in ([8,9,12,25,35] if prime==2 else [8,9,12,25]):
            v=base.copy();hc,dc=(113,89) if prime==2 else (114,88)
            for j in range(11,n+3):
                t=T**(4*j*j-66*j+hc)
                s=1+T**144+sum(T**(6*r+dc) for r in range(11,j+1))
                v[j]=(-t*s*s,t,t*s)
            f=expand(polys(v));H=hull(f,prime)
            expected=core+([(20,12 if prime==2 else 14)] if n>=9 else [])
            expected += [(e,2*e*e-60*e+412) for e in range(21,2*n+4)]
            assert H==expected and counts(H)==(2*n+1,2*n)
            assert {e:x*y+z*z for e,(x,y,z) in v.items() if x*y+z*z}=={4:1}
            a,b=T**-3,T**-4
            transformed={e:((x+2*a*z-a*a*y)/(a-b),(-x-2*b*z+b*b*y)/(a-b),(-x-(a+b)*z+a*b*y)/(a-b)) for e,(x,y,z) in v.items()}
            assert expand(polys(transformed))==f
            assert lcm(*(c.denominator for row in transformed.values() for c in row))==D
            assert sum(bool(c) for row in transformed.values() for c in row)==3*n-4
            families.append({'prime':prime,'n':n,'k':1,'V':2*n+1,'U':2*n,'S':3*n-4})
    report={'at':datetime.now(timezone.utc).isoformat(),'status':'PASS','sources':sources,
            'five_support_examples':five,'family_members':families,'root_lifts':roots,
            'tail_checks':polynomial_tail_checks(),
            'hashes':{n:sha256((HERE/n).read_bytes()).hexdigest() for n in ['verify_families.py','polynomial_arithmetic.py','verify_unit10_examples.py']},
            'scope':'Exact independent expansion of incorporated frozen examples and finite family members; symbolic tail comparisons supplement the written all-n and every-prime proof.'}
    (HERE/'FAMILIES_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','five_support_examples':len(five),'family_members':len(families),'root_lifts':roots,'tail_checks':report['tail_checks']}))


if __name__=='__main__':main()
