"""Solver-free verification of the sharp-six finite proof certificate.

Regenerates the finite systems, independently audits their rule instances,
checks every integer Farkas identity, and checks complete case coverage.
The written proof supplies the reduction from valued fields to these rules.
"""
from pathlib import Path
from itertools import combinations,combinations_with_replacement,permutations
from fractions import Fraction
from collections import Counter
from hashlib import sha256
from datetime import datetime,timezone
import json,time
from certificate_system import make_system
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run this exact verifier without Python optimization flags.')
PAIRS=list(combinations(range(6),2))
GRID=list(combinations_with_replacement(range(6),2))

def combination(*forms):
    out={}
    for factor,form in forms:
        for k,v in form.items():out[k]=out.get(k,0)+factor*v
    return {k:v for k,v in out.items() if v}
def variable(prefix,e):return {prefix+''.join(map(str,sorted(e))):1}
def position(e):
    out={}
    for i in e:out['A'+str(i)]=out.get('A'+str(i),0)+1
    return out
def form_of(c):
    assert c['kind'] in ['eq','ge'] and type(c['strict']) is bool
    assert all(type(value) is int for value in c['form'].values())
    assert c['kind']!='eq' or not c['strict']
    return c['kind'],c['strict'],c['form']
def constraint(form,kind='ge',strict=False):return kind,strict,form

class RuleAudit:
    def __init__(self,case):
        self.a=case['anchor'];self.primary=tuple(case['primary'])
        self.groups=[tuple(tuple(e) for e in g) for g in case.get('groups',[[e] for e in PAIRS])]
        self.unmarked=set(case.get('unmarked_indices',[PAIRS.index(tuple(e)) for e in case.get('unmarked',[])]))
        assert self.a in [1,2] and self.primary[0]<self.a<self.primary[1]
        assert sorted(e for g in self.groups for e in g)==PAIRS
        assert all(list(g)==sorted(set(g)) for g in self.groups)
        self.relations=[combination((1,position(self.primary)),(-1,position((self.a,self.a))))]
        self.relations += [combination((1,position(e)),(-1,position(g[0]))) for g in self.groups for e in g[1:]]
        self.basis={}
        for relation in self.relations:
            row={k:Fraction(v) for k,v in relation.items() if v}
            for pivot,b in sorted(self.basis.items()):
                if pivot in row:row=combination((1,row),(-row[pivot],b))
            if row:
                pivot=min(row);v=row[pivot];self.basis[pivot]={k:x/v for k,x in row.items()}
        self.marked={e for r,g in enumerate(self.groups) if r not in self.unmarked for e in g}
        self.good={g[0] for r,g in enumerate(self.groups) if r not in self.unmarked and len(g)==1 and self.primary not in g}
        self.vertex={e:any(self.implied_equal(position(e),position(f)) for f in self.marked) for e in GRID}

    def implied_equal(self,left,right):
        row=combination((1,left),(-1,right))
        for pivot,b in sorted(self.basis.items()):
            if pivot in row:row=combination((1,row),(-row[pivot],b))
        return not row

    def strict_order_for_all_supports(self,left,right):
        row=combination((1,right),(-1,left));c=[row.get('A%d'%i,0) for i in range(6)]
        if sum(c)!=0:return False
        gaps=[sum(c[j+1:]) for j in range(5)]
        return all(v>=0 for v in gaps) and any(v>0 for v in gaps)

    def axiom(self,c):
        rule=c['rule'];H=lambda e:variable('h',e);W=lambda e:variable('w',e)
        if rule=='epsilon':expected=constraint({'epsilon':1})
        elif rule=='support_order':
            i=c['index'];assert 0<=i<5;expected=constraint({'A%d'%(i+1):1,'A%d'%i:-1},strict=True)
        elif rule=='support_relation':
            assert c['form'] in self.relations;expected=constraint(c['form'],'eq')
        elif rule=='entry_normalization':
            e=tuple(c['pair']);assert e in PAIRS
            expected=constraint(W(e),'eq') if e==self.primary else constraint(W(e),strict=True)
        elif rule=='hidden_boundary':expected=constraint(H(self.primary),strict=True)
        elif rule=='same_exponent':
            e,f=map(tuple,c['pairs']);assert self.implied_equal(position(e),position(f))
            expected=constraint(combination((1,H(e)),(-1,H(f))),'eq')
        elif rule=='output_positive':
            r=c['group'];assert r in range(len(self.groups));expected=constraint({'H%d'%r:1},strict=True)
        elif rule=='boundary':
            r=c['group'];e=tuple(c['pair']);assert e in self.groups[r]
            expected=constraint(combination((1,{'H%d'%r:1}),(-1,H(e))),'ge' if r in self.unmarked else 'eq')
        elif rule=='singleton_coefficient':
            r=c['group'];g=self.groups[r];assert len(g)==1 and self.primary not in g
            expected=constraint(combination((1,{'H%d'%r:1}),(-1,W(g[0]))),'eq')
        elif rule=='monge':
            outer=[tuple(e) for e in c['outer']];inner=[tuple(e) for e in c['inner']]
            assert combination(*[(1,position(e)) for e in outer],*[(-1,position(e)) for e in inner])=={}
            for e in inner:
                assert self.strict_order_for_all_supports(position(outer[0]),position(e))
                assert self.strict_order_for_all_supports(position(e),position(outer[1]))
            expected=constraint(combination(*[(1,H(e)) for e in outer],*[(-1,H(e)) for e in inner]),strict=any(self.vertex[e] for e in inner))
        elif rule=='primary_midpoint':
            r=c['index'];p,q=self.primary;a=self.a
            expected=constraint(combination((1,H((p,r))),(1,H((q,r))),(-2,H((a,r)))),strict=self.vertex[tuple(sorted((a,r)))])
        elif rule=='clean_gram':
            i,j,k,l=c['quad'];quad=[i,j,k,l]
            assert quad==sorted(set(quad)) and self.a in quad and set(combinations(quad,2))<=self.good
            others=[v for v in quad if v!=self.a]
            form=combination((1,{'epsilon':2}),*[(1,W(e)) for e in combinations(others,2)],(-2,W((i,l))),(-2,W((j,k))))
            expected=constraint(form,'eq')
        else:raise AssertionError(rule)
        assert form_of(c)==expected,(rule,form_of(c),expected)

    def clause(self,c):
        rule=c['rule'];W=lambda e:variable('w',e);H=lambda e:variable('h',e)
        if rule=='coefficient_minimum':
            r=c['group'];g=self.groups[r];assert len(g)>1 and self.primary not in g
            values=[W(e) for e in g]+[{'H%d'%r:1}]
        elif rule=='gram_minimum':
            i,j,k,l=c['quad'];assert [i,j,k,l]==sorted(set([i,j,k,l]))
            values=[combination((2,W((i,j))),(2,W((k,l)))),combination((2,W((i,k))),(2,W((j,l)))),combination((2,W((i,l))),(2,W((j,k))))]
            if self.a in [i,j,k,l]:
                others=[v for v in [i,j,k,l] if v!=self.a]
                values.append(combination((1,{'epsilon':2}),*[(1,W(e)) for e in combinations(others,2)]))
        elif rule=='barycenter_convexity':
            outer=[tuple(e) for e in c['outer']];inner=[tuple(e) for e in c['inner']];u=tuple(c['left_endpoint'])
            assert u in outer
            assert self.implied_equal(combination(*[(1,position(e)) for e in outer]),combination(*[(1,position(e)) for e in inner]))
            gap=combination(*[(1,H(e)) for e in outer],*[(-1,H(e)) for e in inner])
            expected=[[constraint(combination((1,position(u)),(-1,position(inner[0]))))],
                      [constraint(combination((1,position(u)),(-1,position(inner[1]))))],
                      [constraint(gap,strict=any(self.vertex[e] for e in inner))]]
            assert [[form_of(v) for v in option] for option in c['options']]==expected
            return
        elif rule=='distinct_output_exponents':
            r,t=c['groups'];assert r!=t
            gap=combination((1,position(self.groups[r][0])),(-1,position(self.groups[t][0])))
            expected=[[constraint(gap,strict=True)],[constraint(combination((-1,gap)),strict=True)]]
            assert [[form_of(v) for v in option] for option in c['options']]==expected
            return
        else:raise AssertionError(rule)
        assert c['values']==values
        expected=[]
        for i,j in combinations(range(len(values)),2):
            expected.append([constraint(combination((1,values[i]),(-1,values[j])),'eq')]+
                            [constraint(combination((1,v),(-1,values[i]))) for k,v in enumerate(values) if k not in [i,j]])
        assert [[form_of(v) for v in option] for option in c['options']]==expected

def verify_tree(node,rows,clauses):
    if 'multipliers' in node:
        total={};strict=0;seen=set()
        for index,factor in node['multipliers']:
            assert type(index) is int and type(factor) is int and 0<=index<len(rows) and index not in seen
            seen.add(index);c=rows[index]
            assert c['kind']=='eq' or factor>=0
            total=combination((1,total),(factor,c['form']))
            if c['strict']:strict+=factor
        assert total=={} and strict>0
        return 1,1
    index=node['clause'];assert type(index) is int and 0<=index<len(clauses)
    opts=clauses[index]['options'];assert len(node['children'])==len(opts)
    nodes=1;leaves=0
    for child,option in zip(node['children'],opts):
        a,b=verify_tree(child,rows+option,clauses);nodes+=a;leaves+=b
    return nodes,leaves

def all_partitions():
    # Independent equivalence-closure enumeration, without the generator's union/find.
    equations=[((i,l),(j,k)) for i,j,k,l in combinations(range(6),4)]
    found=set()
    for count in range(3):
        for chosen in combinations(equations,count):
            blocks=[{e} for e in PAIRS]
            for e,f in chosen:
                touched=[b for b in blocks if e in b or f in b]
                blocks=[b for b in blocks if b not in touched]+[set().union(*touched)]
            found.add(tuple(sorted(tuple(sorted(b)) for b in blocks)))
    return found

def case_key(case,marked=True):
    audit=RuleAudit(case)
    key=(audit.a,audit.primary,tuple(audit.groups))
    return key+(tuple(sorted(audit.unmarked)),) if marked else key

def null_obstruction(audit):
    collisions={e for g in audit.groups if len(g)>1 for e in g}
    lower=collisions|{audit.primary}
    upper=collisions|{e for r in audit.unmarked for e in audit.groups[r]}
    for i,j,k,l in combinations([v for v in range(6) if v!=audit.a],4):
        if not {(i,j),(k,l),(i,k),(j,l)}&lower and not {(i,l),(j,k)}&upper:
            return (i,j,k,l)
    return None

def gram_identity():
    # Formal determinant of the doubled Gram matrix, in seven indeterminates.
    names=['d','x01','x02','x03','x12','x13','x23']
    zero=(0,)*len(names)
    def term(name,factor=1):
        mon=list(zero);mon[names.index(name)]=1;return {tuple(mon):factor}
    def plus(*polys):
        out=Counter()
        for poly in polys:
            for mon,c in poly.items():out[mon]+=c
        return {mon:c for mon,c in out.items() if c}
    def times(*polys):
        out={zero:1}
        for poly in polys:
            nxt=Counter()
            for m,c in out.items():
                for n,d in poly.items():nxt[tuple(a+b for a,b in zip(m,n))]+=c*d
            out=dict(nxt)
        return out
    def scale(poly,c):return {m:c*v for m,v in poly.items()}
    matrix=[[{} for _ in range(4)] for _ in range(4)]
    matrix[0][0]=term('d',2)
    for i,j in combinations(range(4),2):matrix[i][j]=matrix[j][i]=term('x%d%d'%(i,j))
    terms=[]
    for perm in permutations(range(4)):
        sign=(-1)**sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4))
        terms.append(scale(times(*[matrix[i][perm[i]] for i in range(4)]),sign))
    X=times(term('x01'),term('x23'));Y=times(term('x02'),term('x13'));Z=times(term('x03'),term('x12'))
    expected=plus(times(X,X),times(Y,Y),times(Z,Z),scale(times(X,Y),-2),scale(times(X,Z),-2),scale(times(Y,Z),-2),
                  times(term('d',4),term('x12'),term('x13'),term('x23')))
    assert plus(*terms)==expected
    return len(expected)

def readable_case_identities():
    I1={'u':1,'v':2,'r':-1,'n':-1}
    I2={'x':1,'k':1,'u':-1,'z':-1}
    I3={'z':1,'r':1,'k':-1,'v':-1}
    I4={'m':1,'n':1,'v':-2}
    J={'u':1,'r':1,'k':-2}
    B={'z':1,'k':1,'u':-1,'x':-1,'m':-1}
    assert combination((1,I1),(1,I2),(1,I3),(1,I4))=={'x':1,'m':1,'v':-1}
    assert combination((1,I1),(1,I2),(1,I4),(1,J),(1,B))=={}
    return 2

def main():
    start=time.monotonic();parts=all_partitions();assert len(parts)==119
    expected_geometry={(a,(p,q),groups) for groups in parts for a in [1,2] for p in range(a) for q in range(a+1,6)}
    geo_path=HERE/'GEOMETRY_CERTIFICATE.json';geometry=json.loads(geo_path.read_bytes())
    seen=set();needed=set();counts=Counter();pattern_counts=Counter();direct=0
    for row in geometry['rows']:
        case=row['case'];audit=RuleAudit(case);key=case_key(case,False)
        assert key in expected_geometry and key not in seen;seen.add(key);counts[row['kind']]+=1
        if row['kind']=='forced_collision':
            e,f=map(tuple,row['pairs'])
            assert next(r for r,g in enumerate(audit.groups) if e in g)!=next(r for r,g in enumerate(audit.groups) if f in g)
            assert audit.implied_equal(position(e),position(f))
        elif row['kind']=='order_contradiction':
            rows=[{'kind':'ge','strict':True,'form':{'A%d'%(i+1):1,'A%d'%i:-1}} for i in range(5)]
            rows += [{'kind':'eq','strict':False,'form':r} for r in audit.relations]
            assert verify_tree(row['proof'],rows,[])==(1,1)
        elif row['kind']=='feasible':
            A=list(map(Fraction,row['support']));assert len(A)==6 and all(A[i]<A[i+1] for i in range(5))
            assert A[audit.primary[0]]+A[audit.primary[1]]==2*A[audit.a]
            values=[]
            for group in audit.groups:
                sums={A[i]+A[j] for i,j in group};assert len(sums)==1;values.append(sums.pop())
            assert len(set(values))==len(values)
            for unmarked in combinations(range(len(values)),len(values)-13):
                marked_case=dict(case,unmarked_indices=list(unmarked));marked_audit=RuleAudit(marked_case)
                pattern_counts[15-len(values)]+=1
                if null_obstruction(marked_audit) is not None:direct+=1
                else:needed.add(case_key(marked_case))
        else:raise AssertionError(row['kind'])
    assert seen==expected_geometry and len(seen)==1190
    assert counts==Counter(feasible=227,forced_collision=915,order_contradiction=48)
    assert pattern_counts==Counter({0:1050,1:1176,2:133}) and direct==1397 and len(needed)==962
    manifest_path=HERE/'PROOF_BATCH.json';manifest=json.loads(manifest_path.read_bytes())
    covered=set();nodes=leaves=0;rule_counts=Counter();barycenter=0;proof_bytes=0;rigidity_cases=[]
    system_hash=sha256((HERE/'certificate_system.py').read_bytes()).hexdigest()
    for item in manifest['rows']:
        path=HERE/item['proof'];raw=path.read_bytes();proof_bytes+=len(raw)
        assert sha256(raw).hexdigest()==item['sha256'];data=json.loads(raw)
        assert data['status']=='certified' and data['system_sha256']==system_hash
        key=case_key(data['case']);assert key in needed and key not in covered;covered.add(key)
        audit=RuleAudit(data['case']);axioms,clauses=make_system(data['case'],data['barycenter'])
        if item['label'] in ['c1_0046','c1_0312']:
            j=next(i for i in [1,2] if i!=audit.a)
            null_indices=[0,j,3,4,5];collision={(0,4),(j,3)}
            assert audit.primary==(0,3)
            assert any(set(g)==collision and r not in audit.unmarked for r,g in enumerate(audit.groups))
            assert set(combinations(null_indices,2))-collision-{(0,3)}<=audit.good
            assert audit.implied_equal(position((0,4)),position((j,3)))
            rigidity_cases.append(item['label'])
        assert len(axioms)==data['axioms'] and len(clauses)==data['clauses']
        for c in axioms:audit.axiom(c);rule_counts[c['rule']]+=1
        for c in clauses:audit.clause(c);rule_counts[c['rule']]+=1
        n,l=verify_tree(data['proof'],axioms,clauses)
        assert n==data['nodes'] and l==data['leaves'];nodes+=n;leaves+=l;barycenter+=data['barycenter']
    assert covered==needed
    assert sorted(rigidity_cases)==['c1_0046','c1_0312']
    report={'at':datetime.now(timezone.utc).isoformat(),'status':'PASS','seconds':time.monotonic()-start,
            'partitions':len(parts),'geometry_cases':len(seen),'geometry_counts':dict(counts),
            'marked_patterns_by_collision_count':dict(pattern_counts),'direct_null_obstructions':direct,
            'linear_cases':len(covered),'barycenter_cases':barycenter,'proof_nodes':nodes,'farkas_leaves':leaves,
            'formal_gram_determinant_terms':gram_identity(),'readable_case_identities':readable_case_identities(),
            'convex_rigidity_case_hypotheses_checked':rigidity_cases,
            'audited_rule_instances':dict(rule_counts),'proof_bytes':proof_bytes,
            'hashes':{p.name:sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'certificate_system.py',geo_path,manifest_path]},
            'scope':'Exact standard-library verification of rule instances, complete finite coverage, and integer contradictions. The mathematical reduction is proved in the manuscript.'}
    (HERE/'SHARP_SIX_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
