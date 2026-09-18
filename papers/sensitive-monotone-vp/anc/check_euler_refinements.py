"""Independent direct gadget, thin-host geometry, and one-sided spectral checks."""
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import random
import time

import networkx as nx
import sympy as sp

import check_euler_conditioning as E

ROOT = Path(__file__).resolve().parent
SEED = 202609151145
RNG = random.Random(SEED)


def last_exit_cover(base):
    # Finite construction test, not a claim of a uniform tree sampler.
    tree = nx.bfs_tree(base, 0).to_undirected()
    parent = {child: root for root, child in nx.bfs_edges(tree, 0)}
    orders = {}
    for u in base:
        ns = [w for w in base[u] if u == 0 or w != parent[u]]
        RNG.shuffle(ns)
        orders[u] = ns if u == 0 else ns + [parent[u]]
    tour, finish = E.tour_from_orders(base, orders)
    assert finish == 0
    return E.transition_from_tour(base, tour)


def graph_and_spectrum(name, base):
    states = sorted((u, w) for u in base for w in base[u])
    v, n, d = len(states), len(base), base.degree[0]
    assert all(base.degree[u] == d for u in base)
    T = nx.Graph()
    T.add_nodes_from(range(v))
    M = sp.zeros(v)
    for s, (u, w) in enumerate(states):
        for t, (x, z) in enumerate(states):
            if w == x:
                M[s, t] = 1
            if s != t and (w == x or z == u):
                T.add_edge(s, t)
    assert nx.is_connected(T)
    assert set(dict(T.degree()).values()) == {2*d-1}
    assert all(M[s, s] == 0 for s in range(v))
    J = sp.zeros(v)
    index = {edge: s for s, edge in enumerate(states)}
    for s, (u, w) in enumerate(states):
        J[s, index[w, u]] = 1
    assert M + M.T - J == sp.Matrix(nx.to_numpy_array(T, nodelist=range(v), dtype=int).tolist())
    Q = (M+M.T)/(2*d)
    A = sp.Matrix(nx.to_numpy_array(base, nodelist=sorted(base), dtype=int).tolist())
    small = (A.row_join(d*sp.eye(n))).col_join((d*sp.eye(n)).row_join(A))/(2*d)
    t = sp.Symbol("t")
    assert sp.expand(Q.charpoly(t).as_expr() - t**(v-2*n)*small.charpoly(t).as_expr()) == 0
    # The exact identity includes bipartite eigenvalue -1 and its dependent lifts.
    exact_bipartite = bool(nx.is_bipartite(base))
    if exact_bipartite:
        assert Q.det() == 0 or -1 in Q.eigenvals()
        assert (Q + sp.eye(v)).det() == 0
    L = 8
    physical = nx.lexicographic_product(T, nx.complete_graph(L))
    assert set(dict(physical.degree()).values()) == {2*d*L-1}
    return states, T, {
        "base": name, "vertices": n, "degree": d, "states": v,
        "bipartite": exact_bipartite, "thin_state_degree": 2*d-1,
        "physical_test_L": L, "physical_test_degree": 2*d*L-1,
        "exact_symmetrized_transition_characteristic_identity": True,
        "exact_reverse_edge_overlap_identity": True,
    }


def direct_gadget(pi, root_state, L=8):
    v = len(pi)
    root = root_state*L + RNG.randrange(L)
    aa, bb = [], []
    for s in range(v):
        choices = [z for z in range(s*L, (s+1)*L) if z != root]
        a0, a1, b0, b1 = RNG.sample(choices, 4)
        aa.append((a0, a1))
        bb.append((b0, b1))
    stages = [s for s in range(v) if s != root_state]
    k = len(stages)
    fixed = [aa[z//L][0] for z in range(v*L)]
    switches = {}
    for i, s in enumerate(stages):
        target = pi[s]
        for track in (0, 1):
            switches[aa[s][track]] = (i, (aa[target][track], bb[target][track]))
            switches[bb[target][track]] = (k+i, (aa[target][track], aa[target][1-track]))
    fixed[aa[root_state][0]] = aa[pi[root_state]][0]
    fixed[aa[root_state][1]] = root
    for track in (0, 1):
        fixed[bb[pi[root_state]][track]] = aa[pi[root_state]][track]
    fixed[root] = root
    return {"fixed": fixed, "switches": switches, "k": k, "root": root,
            "a": aa, "b": bb, "L": L}


def outgoing(gadget, bits):
    out = gadget["fixed"].copy()
    for z, (i, pair) in gadget["switches"].items():
        out[z] = pair[bits[i]]
    return out


def rooted(out, root):
    # Independently implement the total predicate via reverse reachability.
    incoming = [[] for _ in out]
    for u, w in enumerate(out):
        if u != root:
            incoming[w].append(u)
    reached = {root}
    stack = [root]
    while stack:
        u = stack.pop()
        for w in incoming[u]:
            if w not in reached:
                reached.add(w)
                stack.append(w)
    return len(reached) == len(out)


def gadget_checks(base, states, T):
    count = locality = reversed_steps = corruptions = 0
    for j in range(6):
        pi = last_exit_cover(base)
        for s, t in enumerate(pi):
            assert T.has_edge(s, t)
            reversed_steps += int(states[t] == states[s][::-1])
        root_state = RNG.randrange(len(pi))
        G = direct_gadget(pi, root_state)
        L, k, root = G["L"], G["k"], G["root"]
        for z in range(len(G["fixed"])):
            if z == root:
                continue
            destinations = G["switches"][z][1] if z in G["switches"] else [G["fixed"][z]]
            for w in destinations:
                assert z != w and (z//L == w//L or T.has_edge(z//L, w//L))
        for _ in range(256):
            bits = [RNG.randrange(2) for _ in range(2*k)]
            parity = sum(bits[i]*bits[k+i] for i in range(k)) % 2
            assert rooted(outgoing(G, bits), root) == bool(parity)
            count += 1
        bits = [0]*(2*k)
        baseline = outgoing(G, bits)
        for i in range(2*k):
            bits[i] = 1
            out = outgoing(G, bits)
            changed = {z for z, (a, b) in enumerate(zip(baseline, out)) if a != b}
            prescribed = {z for z, (index, _) in G["switches"].items() if index == i}
            assert len(changed) == 2 and changed == prescribed
            bits[i] = 0
            locality += 1
        bits[0] = bits[k] = 1
        odd = outgoing(G, bits)
        assert rooted(odd, root)
        a0, a1 = G["a"][root_state]
        odd[a1] = a0
        assert not rooted(odd, root)
        corruptions += 1
    return {"layouts": 6, "sampled_bit_inputs": count,
            "exact_single_bit_locality_checks": locality,
            "backtracking_transitions_used": reversed_steps,
            "valid_root_exit_corruptions_rejected": corruptions}


def logarithmic_inequality():
    x, rho = sp.symbols("x rho", real=True)
    f = sp.log(1-x)+x+x*x/(2*(1-rho))
    derivative = x*(rho-x)/((1-rho)*(1-x))
    assert sp.simplify(sp.diff(f, x)-derivative) == 0
    assert f.subs(x, 0) == 0
    # The interval sign argument is analytic in the manuscript.
    c = Fraction(1, 7680000)
    d, L = 734, 1024
    DH = 2*d*L-1
    assert DH == 1503231
    assert 367*1467*(1467**2-1) > 2**32
    return {"symbolic_log_derivative_identity": True,
            "domain_of_written_sign_proof": "-1 <= x <= rho < 1; 0 < rho",
            "thin_host_degree": DH, "thin_N_upper_factor": L*DH,
            "thin_a": str(c/(2*L*DH)), "thin_b": str(c/(3*L*DH))}


def main():
    start = time.monotonic()
    rows = []
    bases = [("C3", nx.cycle_graph(3)), ("C4", nx.cycle_graph(4)),
             ("C5", nx.cycle_graph(5)), ("K4", nx.complete_graph(4)),
             ("K3,3", nx.complete_bipartite_graph(3, 3)),
             ("K4,4", nx.complete_bipartite_graph(4, 4)),
             ("Petersen", nx.petersen_graph()),
             ("Cubic12", nx.random_regular_graph(3, 12, seed=SEED))]
    for name, base in bases:
        states, T, row = graph_and_spectrum(name, base)
        row.update(gadget_checks(base, states, T))
        rows.append(row)
    assert sum(r["backtracking_transitions_used"] for r in rows) > 0
    result = {
        "status": "PASS", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "imported_source": {"path": "check_euler_conditioning.py",
                            "sha256": hashlib.sha256((ROOT/"check_euler_conditioning.py").read_bytes()).hexdigest()},
        "rows": rows, "log_and_constants": logarithmic_inequality(),
        "total_layouts": sum(r["layouts"] for r in rows),
        "total_bit_inputs": sum(r["sampled_bit_inputs"] for r in rows),
        "total_locality_checks": sum(r["exact_single_bit_locality_checks"] for r in rows),
        "elapsed_seconds": time.monotonic()-start,
        "scope": [
            "The direct physical gadget and root predicate are independently reimplemented.",
            "Toy Euler covers use a fixed BFS tree and random local orders, not uniform trees.",
            "Exact graph identities and symbolic derivatives support the written general proof.",
            "The toy degrees do not satisfy the asymptotic degree requirement.",
            "These finite examples do not establish the asymptotic theorem.",
        ],
    }
    (ROOT/"EULER_REFINEMENTS_CHECK.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
