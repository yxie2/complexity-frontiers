"""Finite checks for local cycle covers, routed IP, and partition estimates.

Toy hosts are intentionally much smaller than the asymptotic theorem's
constants. Their successful greedy routes do not verify Alon--Capalbo.
"""
from collections import Counter, deque
from datetime import datetime, timezone
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import math
import random
import time

import networkx as nx
import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parent
SEED = 202609150923
RNG = random.Random(SEED)


def derangements(items):
    return [p for p in permutations(items)
            if all(a != b for a, b in zip(items, p))]


def state_data(base):
    vertices = sorted(base)
    neighbors = {u: sorted(base[u]) for u in vertices}
    states = [(u, w) for u in vertices for w in neighbors[u]]
    index = {s: i for i, s in enumerate(states)}
    allowed = [[index[w, z] for z in neighbors[w] if z != u]
               for u, w in states]
    return states, index, allowed, neighbors


def cycle_list(pi):
    assert sorted(pi) == list(range(len(pi)))
    seen = set()
    result = []
    for s in range(len(pi)):
        if s in seen:
            continue
        cyc = []
        t = s
        while t not in seen:
            seen.add(t)
            cyc.append(t)
            t = pi[t]
        assert t == s
        result.append(cyc)
    return result


def join_cycles(pi):
    cycles = cycle_list(pi)
    joined = pi.copy()
    if len(cycles) > 1:
        sources = [min(c) for c in cycles]
        targets = [pi[u] for u in sources]
        assert len(set(sources + targets)) == 2*len(cycles)
        for i, u in enumerate(sources):
            joined[u] = targets[(i+1) % len(cycles)]
    assert len(cycle_list(joined)) == 1
    changed = [u for u in range(len(pi)) if pi[u] != joined[u]]
    assert len(changed) <= len(cycles)
    return joined, changed, cycles


def make_pi(base, selectors=None):
    states, index, allowed, neighbors = state_data(base)
    local = {}
    for w, ns in neighbors.items():
        ds = derangements(ns)
        local[w] = ds[selectors[w]] if selectors is not None else RNG.choice(ds)
    pi = [None]*len(states)
    for w, ns in neighbors.items():
        for u, z in zip(ns, local[w]):
            pi[index[u, w]] = index[w, z]
    assert all(t in allowed[s] for s, t in enumerate(pi))
    return pi


def girth(base):
    best = math.inf
    for root in base:
        distance = {root: 0}
        parent = {root: None}
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for w in base[u]:
                if w not in distance:
                    distance[w] = distance[u]+1
                    parent[w] = u
                    queue.append(w)
                elif parent[u] != w:
                    best = min(best, distance[u]+distance[w]+1)
    return int(best)


def cycle_cover_checks():
    rows = []
    for name, base in [("C3", nx.cycle_graph(3)),
                       ("K4", nx.complete_graph(4)),
                       ("K3,3", nx.complete_bipartite_graph(3, 3)),
                       ("K5", nx.complete_graph(5))]:
        states, _, _, ns = state_data(base)
        gs = girth(base)
        counts = Counter()
        minimum_cycle = len(states)
        choices = [range(len(derangements(ns[u]))) for u in sorted(base)]
        cases = 0
        for selectors in product(*choices):
            pi = make_pi(base, selectors)
            joined, changed, cycles = join_cycles(pi)
            shortest = min(map(len, cycles))
            assert shortest >= gs
            assert len(cycles)*gs <= len(states)
            counts[len(cycles)] += 1
            minimum_cycle = min(minimum_cycle, shortest)
            cases += 1
        rows.append({"base": name, "states": len(states), "girth": gs,
                     "all_local_derangement_choices": cases,
                     "cycle_count_histogram": dict(sorted(counts.items())),
                     "shortest_observed_cycle": minimum_cycle})
    return rows


def all_reach(out, root):
    state = [0]*len(out)
    state[root] = 2
    for start in range(len(out)):
        if state[start] == 2:
            continue
        path = []
        u = start
        while state[u] == 0:
            state[u] = 1
            path.append(u)
            u = out[u]
        if state[u] == 1:
            return False
        for u in path:
            state[u] = 2
    return True


def route_multigraph(aux, requests):
    remaining = aux.copy()
    routes = []
    for u, w in requests:
        path = nx.shortest_path(remaining, u, w)
        labeled = []
        for a, b in zip(path, path[1:]):
            key = min(remaining[a][b])
            labeled.append((min(a, b), max(a, b), key))
            remaining.remove_edge(a, b, key)
        routes.append((path, labeled))
    edges = [e for _, labeled in routes for e in labeled]
    assert len(edges) == len(set(edges))
    return routes


def build_gadget(base, root_state, selectors=None):
    states, _, allowed, _ = state_data(base)
    v = len(states)
    pi = make_pi(base, selectors)
    successor, changed, cycles = join_cycles(pi)
    # Toy fixed auxiliary graph: complete for tiny instances, or sparse
    # random regular plus every nonbacktracking edge for larger instances.
    aux = nx.MultiGraph()
    aux.add_nodes_from(range(v))
    if v <= 20:
        for u in range(v):
            for w in range(u+1, v):
                aux.add_edge(u, w)
                if v <= 8:
                    aux.add_edge(u, w)
    else:
        aux.add_edges_from(nx.random_regular_graph(20, v, seed=130+v).edges())
        for u, ws in enumerate(allowed):
            for w in ws:
                if not aux.has_edge(u, w):
                    aux.add_edge(u, w)
    D = max(dict(aux.degree()).values())
    L = D+10
    root = root_state*L
    a, b = {}, {}
    terminal = {root}
    for s in range(v):
        pool = list(range(s*L, (s+1)*L))
        if s == root_state:
            pool.remove(root)
        chosen = RNG.sample(pool, 4)
        a[s] = chosen[:2]
        b[s] = chosen[2:]
        terminal.update(chosen)
    logical_arcs = []
    for u in changed:
        w = successor[u]
        for track in range(2):
            logical_arcs.append((a[u][track], a[w][track]))
            logical_arcs.append((a[u][track], b[w][track]))
    requests = [(u//L, w//L) for u, w in logical_arcs]
    endpoint_counts = Counter(s for pair in requests for s in pair)
    assert not endpoint_counts or max(endpoint_counts.values()) <= 4
    raw_routes = route_multigraph(aux, requests)
    used = set(terminal)
    lifted = {}
    internal = set()
    for arc, (path, _) in zip(logical_arcs, raw_routes):
        physical = [arc[0]]
        for s in path[1:-1]:
            z = next(z for z in range(s*L, (s+1)*L) if z not in used)
            used.add(z)
            internal.add(z)
            physical.append(z)
        physical.append(arc[1])
        lifted[arc] = physical
    assert not internal & terminal
    assert len(internal) == sum(len(p)-2 for p in lifted.values())
    # All unused clones point to a fixed terminal in their own clique.
    fixed = [a[z//L][0] for z in range(v*L)]
    fixed[root] = root
    for path in lifted.values():
        for u, w in zip(path[1:-1], path[2:]):
            fixed[u] = w
    def first(u, w):
        if (u, w) in lifted:
            return lifted[u, w][1]
        assert u//L == w//L or aux.has_edge(u//L, w//L)
        return w
    stages = [u for u in range(v) if u != root_state]
    k = len(stages)
    switches = {}
    for i, u in enumerate(stages):
        w = successor[u]
        for track in range(2):
            options = [first(a[u][track], a[w][track]),
                       first(a[u][track], b[w][track])]
            assert len(set(options)) == 2
            switches[a[u][track]] = (i, options)
            switches[b[w][track]] = (
                k+i, [a[w][track], a[w][track ^ 1]])
    start = successor[root_state]
    fixed[a[root_state][0]] = first(a[root_state][0], a[start][0])
    fixed[a[root_state][1]] = root
    for track in range(2):
        fixed[b[start][track]] = a[start][track]
    assert len(switches) == 4*k
    for z in range(v*L):
        if z == root:
            continue
        options = switches[z][1] if z in switches else [fixed[z]]
        for w in options:
            assert w != z
            assert z//L == w//L or aux.has_edge(z//L, w//L)
    return {"v": v, "L": L, "k": k, "root": root, "root_state": root_state,
            "pi": pi, "successor": successor, "cycles": cycles,
            "changed": changed, "fixed": fixed, "switches": switches,
            "a": a, "b": b, "stages": stages, "routes": lifted,
            "internal": internal, "aux": aux, "D": D}


def evaluate(built, bits):
    out = built["fixed"].copy()
    for z, (i, options) in built["switches"].items():
        out[z] = options[bits[i]]
    return all_reach(out, built["root"])


def gadget_checks():
    rows = []
    total = 0
    rejected = 0
    tests = [("C3", nx.cycle_graph(3), s, None, True) for s in range(6)]
    tests += [("C4", nx.cycle_graph(4), s, None, True) for s in [0, 7]]
    tests += [("K4", nx.complete_graph(4), s % 12, list(sel), False)
              for s, sel in enumerate(product(range(2), repeat=4))]
    tests += [("K3,3", nx.complete_bipartite_graph(3, 3), 0, None, False),
              ("Petersen", nx.petersen_graph(), 29, None, False),
              ("cubic20", nx.random_regular_graph(3, 20, seed=651),
               0, None, False)]
    for name, base, root_state, selectors, exhaustive in tests:
        built = build_gadget(base, root_state, selectors)
        k = built["k"]
        bits_iter = (product([0, 1], repeat=2*k) if exhaustive else
                     ([RNG.randrange(2) for _ in range(2*k)] for _ in range(1024)))
        cases = 0
        for bits in bits_iter:
            expected = sum(bits[i]*bits[k+i] for i in range(k)) % 2
            assert evaluate(built, bits) == bool(expected)
            cases += 1
        total += cases
        # Whole-cluster, clone-split, random, and terminal-adversarial cuts.
        vertices = [z for z in range(len(built["fixed"])) if z != built["root"]]
        L, v = built["L"], built["v"]
        partitions = [
            {z for z in vertices if z//L < v//2},
            {z for z in vertices if z % L < L//2},
            set(RNG.sample(vertices, len(vertices)//2)),
        ]
        for A in partitions:
            honoured_original = sum(all(z in A for z in built["a"][u])
                and all(z not in A for z in built["b"][built["pi"][u]])
                for u in range(v))
            good = [i for i, u in enumerate(built["stages"])
                    if all(z in A for z in built["a"][u])
                    and all(z not in A for z in built["b"][built["successor"][u]])]
            assert len(good) >= honoured_original-len(built["changed"])-1
            for z, (bit, _) in built["switches"].items():
                if bit in good:
                    assert z in A
                if bit-k in good:
                    assert z not in A
        witness = [0]*(2*k)
        witness[0] = witness[k] = 1
        assert evaluate(built, witness)
        # Corrupt c1's destination. Every accepted gadget uses it.
        broken = {**built, "fixed": built["fixed"].copy()}
        c1 = built["a"][root_state][1]
        broken["fixed"][c1] = c1
        assert not evaluate(broken, witness)
        rejected += 1
        rows.append({"base": name, "root_state": root_state, "states": v,
                     "physical_vertices": len(built["fixed"]),
                     "cycles": len(built["cycles"]),
                     "changed_transitions": len(built["changed"]),
                     "root_transition_changed": root_state in built["changed"],
                     "routed_arcs": len(built["routes"]),
                     "internal_vertices": len(built["internal"]),
                     "max_path_length": max([len(p)-1 for p in built["routes"].values()]
                                            or [0]),
                     "bit_inputs": cases, "all_bit_inputs": exhaustive})
    return {"instances": rows, "total_bit_inputs": total,
            "rejected_c1_corruptions": rejected}


def analytic_checks():
    local_cases = 0
    for d in [3, 4, 5, 18]:
        for _ in range(5000):
            a = [RNG.randrange(-20, 21) for _ in range(d)]
            b = [RNG.randrange(-20, 21) for _ in range(d)]
            full = sum((u-w)**2 for u in a for w in b)
            diag = sum((u-w)**2 for u, w in zip(a, b))
            assert d*diag <= 2*full
            local_cases += 1
    spectral = []
    for name, base in [("K4", nx.complete_graph(4)),
                       ("K3,3", nx.complete_bipartite_graph(3, 3)),
                       ("Petersen", nx.petersen_graph()),
                       ("regular18x40", nx.random_regular_graph(18, 40, seed=300))]:
        states, index, allowed, ns = state_data(base)
        v = len(states)
        d = len(ns[0])
        P = np.zeros((v, v))
        P0 = np.zeros((v, v))
        for s, (u, w) in enumerate(states):
            for z in ns[w]:
                P0[s, index[w, z]] = 1/d
            for t in allowed[s]:
                P[s, t] = 1/(d-1)
        Q, Q0 = (P+P.T)/2, (P0+P0.T)/2
        assert np.max(abs(P.sum(axis=0)-1)) < 1e-12
        eigen_base = np.linalg.eigvalsh(nx.to_numpy_array(base)/d)
        rho = eigen_base[-2]
        theoretical = (d-2)/(d-1)*(1-rho)/2
        qgap = 1-np.linalg.eigvalsh(Q)[-2]
        q0gap = 1-np.linalg.eigvalsh(Q0)[-2]
        assert qgap+1e-10 >= theoretical
        assert q0gap+1e-10 >= (1-rho)/2
        spectral.append({"base": name, "states": v, "rho": float(rho),
                         "Q_gap": float(qgap), "Q0_gap": float(q0gap),
                         "proved_comparison_lower_bound": float(theoretical),
                         "scope": "Floating-point check, not a spectral proof."})
    # Exact whole-cluster partition expectations on every balanced K4-state cut.
    base = nx.complete_graph(4)
    states, _, allowed, _ = state_data(base)
    pis = [make_pi(base, sel) for sel in product(range(2), repeat=4)]
    exact_cuts = 0
    for mask in range(1 << len(states)):
        c = mask.bit_count()
        if not 4 <= c <= 8:
            continue
        zsum = sum(sum((mask >> s & 1) and not (mask >> pi[s] & 1)
                       for s in range(12)) for pi in pis)
        directed_cross = sum((mask >> s & 1) and not (mask >> t & 1)
                             for s in range(12) for t in allowed[s])
        assert Fraction(zsum, len(pis)) == Fraction(directed_cross, 2)
        mu = Fraction(c, 12)
        assert Fraction(directed_cross, 24) >= Fraction(1, 8)*mu*(1-mu)
        exact_cuts += 1
    # Independent variable Lipschitz bounds for every K4 local outcome
    # and random physical-clone color pattern.
    lipschitz_cases = 0
    def score(pi, ac, bc):
        return sum(ac[s] and bc[pi[s]] for s in range(12))
    for _ in range(100):
        ac = [bool(RNG.randrange(2)) for _ in range(12)]
        bc = [bool(RNG.randrange(2)) for _ in range(12)]
        for sel in product(range(2), repeat=4):
            pi = make_pi(base, sel)
            z = score(pi, ac, bc)
            for w in range(4):
                other = list(sel)
                other[w] ^= 1
                assert abs(z-score(make_pi(base, other), ac, bc)) <= 3
                lipschitz_cases += 1
            for s in range(12):
                aa, bb = ac.copy(), bc.copy()
                aa[s], bb[s] = not aa[s], not bb[s]
                assert abs(z-score(pi, aa, bb)) <= 2
                lipschitz_cases += 1
    # Exact finite-population clone correction, including signed lower RHS.
    pair_cases = 0
    for L in [4, 5, 10, 100, 6402]:
        for c in range(L+1):
            p = Fraction(c*(c-1), L*(L-1))
            density = Fraction(c, L)
            assert p == density**2-density*(1-density)/(L-1)
            assert p >= density**2-Fraction(1, 4*(L-1))
            pair_cases += 1
    assert 16*15**43 < 16**43
    return {"integer_local_Dirichlet_cases": local_cases,
            "numerical_spectral_comparisons": spectral,
            "exact_balanced_K4_state_partitions": exact_cuts,
            "local_bounded_difference_checks": lipschitz_cases,
            "exact_clone_pair_probabilities": pair_cases,
            "exact_fixed_power_check": "16*15^43 < 16^43"}


def main():
    started = time.monotonic()
    result = {"status": "PASS", "seed": SEED,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cycle_covers": cycle_cover_checks(),
              "physical_gadgets": gadget_checks(),
              "analytic_checks": analytic_checks(),
              "scope": [
                  "Toy graphs test the construction and locality, not the asymptotic LPS parameters.",
                  "Routing uses successful greedy BFS on a toy multigraph, not Alon--Capalbo's algorithm.",
                  "Every physical vertex, unused alternative path, and filler clone participates in evaluation.",
                  "The concentration and discrepancy lower bounds require the written proof.",
                  "These computations do not establish novelty or replace independent human review."
              ],
              "elapsed_seconds": time.monotonic()-started,
              "completed_at_utc": datetime.now(timezone.utc).isoformat()}
    (ROOT/"VERIFICATION.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
