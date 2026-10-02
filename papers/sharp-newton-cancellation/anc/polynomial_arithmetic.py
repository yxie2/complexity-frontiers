"""Exact rational polynomial expansion, valuations, and lower hulls."""
from fractions import Fraction as F
from collections import defaultdict
import sys
if not __debug__: raise RuntimeError('Run without Python optimization flags.')
sys.set_int_max_str_digits(0)

def load(rows):return [{int(e):F(c) for e,c in row} for row in rows]
def expand(polys):
    out=defaultdict(F)
    for i,j in [(0,1),(2,2)]:
        for e,c in polys[i].items():
            for f,d in polys[j].items():out[e+f]+=c*d
    return {e:c for e,c in out.items() if c}
def order(x,p):
    def v(n):
        assert n;k=0
        while n%p==0:n//=p;k+=1
        return k
    return v(abs(x.numerator))-v(x.denominator)
def hull(poly,p):
    points=[(e,order(c,p)) for e,c in sorted(poly.items())];vertices=[]
    for point in points:
        while len(vertices)>=2:
            a,b=vertices[-2:];c=point
            if (b[1]-a[1])*(c[0]-b[0])<(c[1]-b[1])*(b[0]-a[0]):break
            vertices.pop()
        vertices.append(point)
    for (a,h),(b,k) in zip(vertices,vertices[1:]):
        assert all((y-h)*(b-a)>=(k-h)*(e-a) for e,y in points)
    return vertices
def counts(H):return len(H)-1,sum(b[0]-a[0]==1 for a,b in zip(H,H[1:]))
