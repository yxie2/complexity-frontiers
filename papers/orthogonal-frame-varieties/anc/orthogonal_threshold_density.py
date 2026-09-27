"""Exact integer controls for the density corollary; not a singularity proof."""
from pathlib import Path
from math import isqrt
import hashlib, json, time

start=time.monotonic()

def floor_half_difference(a, rad):
    s=isqrt(rad)
    return (a-s-1)//2 if s*s != rad else (a-s)//2

def ceil_half_difference(a, rad):
    return (a-isqrt(rad)+1)//2

def prime(h):
    return min(2*floor_half_difference(2*h+1,8*h+1)+2,
               2*floor_half_difference(2*h+1,8*h-7)+1)

def ufd(h):
    return min(2*ceil_half_difference(2*h+1,8*h-23),
               2*ceil_half_difference(2*h-1,8*h-31)+1)

checked=0; factorial=0; examples=[]; cumulative=0
for k in range(4,1001):
    lo=k*(k-1)//2+2; hi=k*k//2; count=0
    for h in range(lo,hi+1):
        q=h-k; M=2*q+1; c=h-k*(k-1)//2
        delta=k*(k-1)//2-q
        N=M*h-h*(h-1)//2; S=q*(q+1)//2+q*h
        assert prime(h)==M
        assert N-S==c and delta==k-c
        assert delta-c==k*k-2*h>=0
        if c>=4:
            assert ufd(h)==M
            factorial+=1
        if k<=10:
            examples.append(dict(k=k,h=h,M=M,stratum_codim=c,
                                 tangent_excess=delta,jet_excess=delta-c,
                                 factorial_certified=c>=4))
        checked+=1; count+=1
    assert count==k//2-1
    cumulative+=count
    assert cumulative==((k-2)**2)//4

block_checks=0
for k in range(2,301):
    for h in range(k*(k-1)//2+2,k*(k+1)//2+1):
        assert prime(h)==2*h-2*k+1
        block_checks+=1
    h=k*(k+1)//2+1
    assert prime(h)==2*h-2*k
    block_checks+=1

out=dict(status="passed",counterexample_parameter_checks=checked,
         factorial_parameter_checks=factorial,prime_block_checks=block_checks,
         k_max=1000,examples=examples,seconds=time.monotonic()-start,
         producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         scope="Exact arithmetic controls only; all-size proof is in the companion note.")
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='examples'},indent=2))
