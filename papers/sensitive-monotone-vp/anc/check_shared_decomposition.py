"""Audit the shared-gate balanced-product extraction by exact polynomials."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import random
import time

ROOT = Path(__file__).resolve().parent
SEED = 202609151344
G = 6
VARIABLES = 2*G
Z = VARIABLES
ZERO = (0,)*(VARIABLES+1)


def plus(a,b):
    c=dict(a)
    for e,x in b.items():
        c[e]=c.get(e,F(0))+x
    return {e:x for e,x in c.items() if x}


def times(a,b):
    c={}
    for e,x in a.items():
        for f,y in b.items():
            g=tuple(u+v for u,v in zip(e,f))
            c[g]=c.get(g,F(0))+x*y
    return {e:x for e,x in c.items() if x}


def var(j):
    e=list(ZERO);e[j]=1
    return {tuple(e):F(1)}


def evaluate(nodes, zeros=frozenset(), selected=None):
    values=[]
    for j,node in enumerate(nodes):
        if j in zeros:
            values.append({})
        elif j==selected:
            values.append(var(Z))
        elif node[0]=='v':
            values.append(var(node[1]))
        elif node[0]=='c':
            values.append({ZERO:node[1]} if node[1] else {})
        else:
            values.append((plus if node[0]=='+' else times)(
                values[node[1]],values[node[2]]))
    return values


def groups(poly):
    if not poly:
        return None
    found=None
    for e in poly:
        assert not e[Z] and all(a<=1 for a in e)
        assert all(e[2*i]+e[2*i+1]<=1 for i in range(G))
        current=frozenset(i for i in range(G) if e[2*i]+e[2*i+1])
        if found is None:
            found=current
        assert current==found
    return found


def random_circuit(rng):
    nodes=[('v',j) for j in range(VARIABLES)]
    nodes += [('c',x) for x in (F(0),F(1),F(1,2),F(2))]
    pools={0:list(range(VARIABLES,len(nodes)))}
    for i in range(G):
        pools[1<<i]=[2*i,2*i+1]
        for _ in range(3):
            a,b=rng.choices(pools[1<<i],k=2)
            nodes.append(('+',a,b));pools[1<<i].append(len(nodes)-1)
    masks=sorted(range(1,1<<G),key=int.bit_count)
    for mask in masks:
        if mask.bit_count()==1:
            continue
        pools[mask]=[]
        splits=[left for left in range(1,mask) if left&mask==left]
        for _ in range(24 if mask == (1<<G)-1 else 3):
            left=rng.choice(splits);right=mask^left
            a=rng.choice(pools[left]);b=rng.choice(pools[right])
            nodes.append(('*',a,b));pools[mask].append(len(nodes)-1)
        for _ in range(2):
            a,b=rng.choices(pools[mask],k=2)
            nodes.append(('+',a,b));pools[mask].append(len(nodes)-1)
    top=(1<<G)-1
    # Force many different top-level cuts to contribute to the same output.
    summands=list(pools[top])
    current=summands[0]
    for other in summands[1:]:
        nodes.append(('+',current,other));current=len(nodes)-1
    # Several parents share a full-group subcircuit; zero branches are harmless.
    shared=current
    nodes.append(('*',shared,VARIABLES+2));a=len(nodes)-1
    nodes.append(('*',shared,VARIABLES+3));b=len(nodes)-1
    nodes.append(('+',a,b))
    current=len(nodes)-1
    nodes.append(('*',0,1));invalid=len(nodes)-1
    nodes.append(('*',invalid,VARIABLES));zero=len(nodes)-1
    nodes.append(('+',current,zero))
    return nodes


def decompose(nodes):
    original=evaluate(nodes)[-1]
    assert groups(original)==frozenset(range(G))
    zeroed=set();terms=[];cut_masks=[];occurrence_excess=0
    while True:
        values=evaluate(nodes,zeroed)
        if not values[-1]:
            break
        current=len(nodes)-1
        while 3*len(groups(values[current]))>2*G:
            op,l,r=nodes[current]
            assert op in ('+','*')
            children=[j for j in (l,r) if values[j]]
            if op=='+':
                current=children[0]
            else:
                current=next(j for j in children if 3*len(groups(values[j]))>=G)
        cut=groups(values[current])
        assert G<=3*len(cut)<=2*G and nodes[current][0] in ('+','*')
        assert current not in zeroed
        # Replace EVERY use of this node by one formal variable.
        with_z=evaluate(nodes,zeroed,current)[-1]
        assert all(e[Z]<=1 for e in with_z)
        coefficient={};constant={}
        for e,x in with_z.items():
            f=list(e);f[Z]=0;f=tuple(f)
            target=coefficient if e[Z] else constant
            target[f]=target.get(f,F(0))+x
        assert groups(coefficient)==frozenset(range(G))-cut
        term=times(values[current],coefficient)
        residual=evaluate(nodes,zeroed|{current})[-1]
        assert constant==residual
        assert plus(term,residual)==values[-1]
        assert all(x<=original.get(e,F(0)) for e,x in term.items())
        terms.append(term);cut_masks.append(sorted(cut));zeroed.add(current)
        productive=set()
        def visit(j):
            if j in productive or not values[j]:
                return
            productive.add(j)
            if nodes[j][0] in ('+','*'):
                visit(nodes[j][1]);visit(nodes[j][2])
        visit(len(nodes)-1)
        occurrence_excess+=max(0,sum(
            nodes[j][0] in ('+','*') and
            (nodes[j][1]==current or nodes[j][2]==current)
            for j in productive)-1)
    total={}
    for term in terms:
        total=plus(total,term)
    assert total==original
    gates=sum(node[0] in ('+','*') for node in nodes)
    assert len(terms)<=gates and len(terms)==len(zeroed)
    return len(terms),len(original),occurrence_excess,len(set(map(tuple,cut_masks)))


def main():
    start=time.monotonic();rng=random.Random(SEED)
    total_terms=coefficients=reused=0;max_terms=max_cuts=0
    for _ in range(120):
        nodes=random_circuit(rng)
        terms,coeff,excess,cuts=decompose(nodes)
        total_terms+=terms;coefficients+=coeff;reused+=excess
        max_terms=max(max_terms,terms);max_cuts=max(max_cuts,cuts)
    # A single-use substitution must fail when the selected node has two parents.
    # Both contexts use the same complementary two groups.
    a=times(var(0),var(2))
    b=times(var(4),var(6))
    target=plus(times(a,b),times(a,b))
    wrong_coefficient=b
    assert times(a,wrong_coefficient)!=target
    result={
        'status':'PASS','seed':SEED,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'manuscript_sha256':hashlib.sha256((ROOT.parent/'main.tex').read_bytes()).hexdigest(),
        'circuits':120,'groups':G,'binary_choices_per_group':2,
        'balanced_products_extracted':total_terms,
        'output_coefficients_reconstructed':coefficients,
        'extra_direct_parent_uses_of_selected_gates':reused,
        'maximum_terms_in_one_decomposition':max_terms,
        'maximum_distinct_cuts_in_one_decomposition':max_cuts,
        'zero_branches_with_invalid_group_monomials_ignored':120,
        'incorrect_single_use_charge_rejected':True,
        'elapsed_seconds':time.monotonic()-start,
        'scope':'Exact finite circuit identities test global substitution, balanced complementary groups, coefficient domination, and one charge per removed shared gate. The asymptotic theorem uses the analytic lemma.'
    }
    (ROOT/'SHARED_DECOMPOSITION_CHECK.json').write_text(
        json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
