"""Exact linear axioms and finite disjunctions for the six-support proof.

This module uses only the standard library. The proof note justifies the
axiom families; an arithmetic certificate never replaces that justification.
"""
from itertools import combinations,combinations_with_replacement
from fractions import Fraction as F
from collections import defaultdict

PAIRS=list(combinations(range(6),2))
GRID=list(combinations_with_replacement(range(6),2))

def lin(*terms):
    out={}
    for k,v in terms:out[k]=out.get(k,0)+v
    return {k:v for k,v in out.items() if v}
def add(*forms):return lin(*[(k,v) for f in forms for k,v in f.items()])
def mul(f,c):return {k:v*c for k,v in f.items() if v*c}
def h(e):return {'h%d%d'%tuple(sorted(e)):1}
def w(e):return {'w%d%d'%tuple(sorted(e)):1}
def E(e):return lin(*[('A%d'%i,1) for i in e])
def eq(f):return {'form':f,'kind':'eq','strict':False}
def ge(f,strict=False):return {'form':f,'kind':'ge','strict':strict}

def row_reduce(rows):
    rows=[[F(x) for x in r] for r in rows];at=0;pivots=[]
    for col in range(6):
        i=next((i for i in range(at,len(rows)) if rows[i][col]),None)
        if i is None:continue
        rows[at],rows[i]=rows[i],rows[at];v=rows[at][col];rows[at]=[x/v for x in rows[at]]
        for j in range(len(rows)):
            if j!=at:
                c=rows[j][col];rows[j]=[x-c*y for x,y in zip(rows[j],rows[at])]
        pivots.append(col);at+=1
    return rows[:at],pivots

def vector(e):
    out=[F(0)]*6
    for i in e:out[i]+=1
    return out

def setup(row):
    a=row['anchor'];primary=tuple(row['primary'])
    groups=[tuple(tuple(e) for e in g) for g in row.get('groups',[[e] for e in PAIRS])]
    unmarked=set(row.get('unmarked_indices',[PAIRS.index(tuple(e)) for e in row.get('unmarked',[])]))
    relations=[add(E(primary),mul(E((a,a)),-1))]
    for g in groups:relations += [add(E(e),mul(E(g[0]),-1)) for e in g[1:]]
    basis,pivots=row_reduce([[r.get('A%d'%i,0) for i in range(6)] for r in relations])
    def reduce(e):
        v=vector(e)
        for b,p in zip(basis,pivots):
            c=v[p];v=[x-c*y for x,y in zip(v,b)]
        return tuple(v)
    residues={e:reduce(e) for e in GRID}
    return a,primary,groups,unmarked,relations,residues

def make_system(row,barycenter=False):
    a,primary,groups,unmarked,relations,residues=setup(row)
    marked={residues[g[0]] for r,g in enumerate(groups) if r not in unmarked}
    good={e for r,g in enumerate(groups) if r not in unmarked and len(g)==1 and primary not in g for e in g}
    axioms=[];clauses=[]
    def put(c,rule,**meta):axioms.append({**c,'rule':rule,**meta})
    def clause(options,rule,**meta):clauses.append({'options':options,'rule':rule,**meta})
    def minimum(values,rule,**meta):
        options=[]
        for i,j in combinations(range(len(values)),2):
            options.append([eq(add(values[i],mul(values[j],-1)))]+
                           [ge(add(v,mul(values[i],-1))) for k,v in enumerate(values) if k not in [i,j]])
        clause(options,rule,values=values,**meta)
    put(ge({'epsilon':1}),'epsilon')
    for i in range(5):put(ge(lin(('A%d'%(i+1),1),('A%d'%i,-1)),True),'support_order',index=i)
    for f in relations:put(eq(f),'support_relation')
    for e in PAIRS:put(eq(w(e)) if e==primary else ge(w(e),True),'entry_normalization',pair=e)
    put(ge(h(primary),True),'hidden_boundary')
    for e,f in combinations(GRID,2):
        if residues[e]==residues[f]:put(eq(add(h(e),mul(h(f),-1))),'same_exponent',pairs=[e,f])
    for r,g in enumerate(groups):
        height={'H%d'%r:1};put(ge(height,True),'output_positive',group=r)
        for e in g:
            f=add(height,mul(h(e),-1))
            put(ge(f) if r in unmarked else eq(f),'boundary',pair=e,group=r)
        if primary in g:
            # Two zero-height terms (the primary and the diagonal); all
            # other terms are positive by the normalization axioms.
            pass
        elif len(g)==1:put(eq(add(height,mul(w(g[0]),-1))),'singleton_coefficient',group=r)
        else:minimum([w(e) for e in g]+[height],'coefficient_minimum',group=r)
    seen=set()
    for i,k in combinations(range(6),2):
        for j,l in combinations(range(6),2):
            outer=tuple(sorted([tuple(sorted((i,j))),tuple(sorted((k,l)))]))
            inner=tuple(sorted([tuple(sorted((i,l))),tuple(sorted((k,j)))]))
            if (outer,inner) in seen:continue
            seen.add((outer,inner));form=add(*[h(e) for e in outer],*[mul(h(e),-1) for e in inner])
            put(ge(form,any(residues[e] in marked for e in inner)),'monge',outer=outer,inner=inner)
    p,q=primary
    for r in range(6):
        mid=tuple(sorted((a,r)))
        put(ge(add(h((p,r)),h((q,r)),mul(h(mid),-2)),residues[mid] in marked),'primary_midpoint',index=r)
    for quad in combinations(range(6),4):
        i,j,k,l=quad
        values=[mul(add(w((i,j)),w((k,l))),2),mul(add(w((i,k)),w((j,l))),2),mul(add(w((i,l)),w((j,k))),2)]
        if a in quad:
            others=[v for v in quad if v!=a]
            diagonal=add({'epsilon':2},*[w(e) for e in combinations(others,2)])
            values.append(diagonal)
            if set(combinations(quad,2))<=good:
                put(eq(add(diagonal,mul(values[2],-1))),'clean_gram',quad=quad)
                continue
        minimum(values,'gram_minimum',quad=quad)
    if barycenter:
        sums=defaultdict(list)
        for e,f in combinations_with_replacement(GRID,2):
            sums[tuple(x+y for x,y in zip(residues[e],residues[f]))].append((e,f))
        for pairs in sums.values():
            for left,right in combinations(pairs,2):
                for outer,inner in [(left,right),(right,left)]:
                    gap=add(*[h(e) for e in outer],*[mul(h(e),-1) for e in inner])
                    strict=any(residues[e] in marked for e in inner)
                    for u in outer:
                        options=[[ge(add(E(u),mul(E(inner[0]),-1)))],
                                 [ge(add(E(u),mul(E(inner[1]),-1)))],[ge(gap,strict)]]
                        clause(options,'barycenter_convexity',outer=outer,inner=inner,left_endpoint=u)
        for r,t in combinations(range(len(groups)),2):
            gap=add(E(groups[r][0]),mul(E(groups[t][0]),-1))
            clause([[ge(gap,True)],[ge(mul(gap,-1),True)]],'distinct_output_exponents',groups=[r,t])
    return axioms,clauses
