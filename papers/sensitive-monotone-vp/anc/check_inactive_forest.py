"""Finite semantic checks of discarded cycles and fixed forest attachment.

Toy routing graphs are complete multigraphs, not the theorem's expanders.
The check includes internal routed paths passing through inactive clusters.
"""
from collections import Counter, deque
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import random
import time

import networkx as nx

import verify as V

ROOT = Path(__file__).resolve().parent
SEED = 202609151054
RNG = random.Random(SEED)


def make_gadget(base, root_state, cutoff, selectors=None):
    pi = V.make_pi(base, selectors)
    v = len(pi)
    all_cycles = V.cycle_list(pi)
    kept = [c for c in all_cycles if len(c) >= cutoff or root_state in c]
    active = set(s for c in kept for s in c)
    inactive = set(range(v))-active
    assert root_state in active and all(pi[s] in inactive for s in inactive)
    successor = pi.copy()
    if len(kept) > 1:
        sources = [min(c) for c in kept]
        targets = [pi[u] for u in sources]
        assert len(set(sources+targets)) == 2*len(kept)
        for i, u in enumerate(sources):
            successor[u] = targets[(i+1) % len(kept)]
    changed = [u for u in active if successor[u] != pi[u]]
    walk = []
    s = root_state
    while s not in walk:
        walk.append(s)
        s = successor[s]
    assert s == root_state and set(walk) == active
    # Put inactive states first in adjacency order so later parallel requests
    # preferentially route through them. This exercises clone reservations.
    state_order = sorted(inactive)+sorted(active)
    aux = nx.MultiGraph()
    aux.add_nodes_from(state_order)
    for u, w in combinations(state_order, 2):
        aux.add_edge(u, w)
        if v <= 8:
            aux.add_edge(u, w)
    D = max(dict(aux.degree()).values())
    L = D+10
    root = root_state*L
    a, b = {}, {}
    terminals = {root}
    for s in range(v):
        pool = list(range(s*L, (s+1)*L))
        if s == root_state:
            pool.remove(root)
        selected = RNG.sample(pool, 4)
        a[s], b[s] = selected[:2], selected[2:]
        terminals.update(selected)
    arcs = []
    for u in sorted(changed):
        w = successor[u]
        for track in range(2):
            arcs.extend([(a[u][track], a[w][track]),
                         (a[u][track], b[w][track])])
    requests = [(u//L, w//L) for u, w in arcs]
    endpoint_counts = Counter(s for request in requests for s in request)
    assert not endpoint_counts or max(endpoint_counts.values()) <= 4
    raw = V.route_multigraph(aux, requests)
    used = set(terminals)
    internal = set()
    paths = {}
    for arc, (route, _) in zip(arcs, raw):
        physical = [arc[0]]
        for state in route[1:-1]:
            z = next(z for z in range(state*L, (state+1)*L) if z not in used)
            used.add(z)
            internal.add(z)
            physical.append(z)
        physical.append(arc[1])
        paths[arc] = physical
    assert not internal & terminals
    assert len(internal) == sum(len(p)-2 for p in paths.values())
    # A fixed spanning path is a valid spanning tree of the toy auxiliary graph.
    # With active states first, the inactive suffix gives genuine long forests.
    tree_order = sorted(active)+sorted(inactive)
    tree = nx.path_graph(tree_order)
    assert all(aux.has_edge(u, w) for u, w in tree.edges())
    distance = {s: 0 for s in active}
    parent = {}
    queue = deque(sorted(active))
    while queue:
        u = queue.popleft()
        for w in tree[u]:
            if w not in distance:
                distance[w] = distance[u]+1
                parent[w] = u
                queue.append(w)
    assert set(parent) == inactive
    assert all(distance[parent[s]] == distance[s]-1 for s in inactive)
    fixed = [a[z//L][0] for z in range(v*L)]
    fixed[root] = root
    for s in inactive:
        fixed[a[s][0]] = a[parent[s]][0]
    for path in paths.values():
        for u, w in zip(path[1:-1], path[2:]):
            fixed[u] = w

    def first(u, w):
        return paths[u, w][1] if (u, w) in paths else w

    stages = sorted(active-{root_state})
    k = len(stages)
    switches = {}
    for i, u in enumerate(stages):
        w = successor[u]
        for track in range(2):
            options = [first(a[u][track], a[w][track]),
                       first(a[u][track], b[w][track])]
            assert len(set(options)) == 2
            switches[a[u][track]] = (i, options)
            switches[b[w][track]] = (k+i, [a[w][track], a[w][track ^ 1]])
    fixed[a[root_state][0]] = first(a[root_state][0], a[successor[root_state]][0])
    fixed[a[root_state][1]] = root
    for track in range(2):
        fixed[b[successor[root_state]][track]] = a[successor[root_state]][track]
    assert len(switches) == 4*k
    assert not {z for z in switches if z//L in inactive}
    for z in range(v*L):
        if z == root:
            continue
        destinations = switches[z][1] if z in switches else [fixed[z]]
        for w in destinations:
            assert w != z
            assert z//L == w//L or aux.has_edge(z//L, w//L)
    return {
        "v": v, "L": L, "root": root, "root_state": root_state, "k": k,
        "pi": pi, "successor": successor, "active": active, "inactive": inactive,
        "a": a, "b": b, "fixed": fixed, "switches": switches, "stages": stages,
        "paths": paths, "internal": internal, "distance": distance,
        "changed": changed, "kept_cycles": len(kept),
        "original_cycles": len(all_cycles),
    }


def outgoing(built, bits):
    out = built["fixed"].copy()
    for z, (i, choices) in built["switches"].items():
        out[z] = choices[bits[i]]
    return out


def check_case(name, base, root, cutoff, selectors):
    built = make_gadget(base, root, cutoff, selectors)
    k = built["k"]
    exhaustive = k <= 5
    bit_inputs = (product([0, 1], repeat=2*k) if exhaustive else
                  ([RNG.randrange(2) for _ in range(2*k)] for _ in range(512)))
    count = 0
    for bits in bit_inputs:
        expected = sum(bits[i]*bits[k+i] for i in range(k)) % 2
        assert V.all_reach(outgoing(built, bits), built["root"]) == bool(expected)
        count += 1
    baseline = [0]*(2*k)
    base_map = outgoing(built, baseline)
    # Check actual maps, not only the variable-to-switch dictionary.
    for i in range(2*k):
        bits = baseline.copy()
        bits[i] = 1
        changed_map = outgoing(built, bits)
        differences = {z for z in range(len(base_map)) if base_map[z] != changed_map[z]}
        expected_vertices = (set(built["a"][built["stages"][i]]) if i < k else
                             set(built["b"][built["successor"][built["stages"][i-k]]]))
        assert differences == expected_vertices
    vertices = [z for z in range(len(base_map)) if z != built["root"]]
    L, v = built["L"], built["v"]
    partitions = [
        {z for z in vertices if z//L < v//2},
        {z for z in vertices if z % L < L//2},
        set(RNG.sample(vertices, len(vertices)//2)),
    ]
    for A in partitions:
        Z = sum(all(z in A for z in built["a"][u])
                and all(z not in A for z in built["b"][built["pi"][u]])
                for u in range(v))
        honoured = [i for i, u in enumerate(built["stages"])
                    if all(z in A for z in built["a"][u])
                    and all(z not in A for z in built["b"][built["successor"][u]])]
        assert len(honoured) >= Z-len(built["inactive"])-len(built["changed"])-1
        for z, (bit, _) in built["switches"].items():
            if bit in honoured:
                assert z in A
            if bit-k in honoured:
                assert z not in A
    witness = [0]*(2*k)
    witness[0] = witness[k] = 1
    correct = outgoing(built, witness)
    assert V.all_reach(correct, built["root"])
    rejected = 0
    if built["inactive"]:
        # All these corrupted arrows remain valid graph edges. Leaving the
        # discarded cycle in place must destroy an otherwise accepted input.
        corrupted = correct.copy()
        for s in built["inactive"]:
            corrupted[built["a"][s][0]] = built["a"][built["pi"][s]][0]
        assert not V.all_reach(corrupted, built["root"])
        rejected = 1
    return {
        "base": name, "root_state": root, "cutoff": cutoff, "states": v,
        "active_states": len(built["active"]), "inactive_states": len(built["inactive"]),
        "original_cycles": built["original_cycles"], "kept_cycles": built["kept_cycles"],
        "changed_transitions": len(built["changed"]),
        "root_transition_changed": root in built["changed"],
        "physical_vertices": len(base_map),
        "routed_arcs": len(built["paths"]),
        "internal_clones_in_inactive_clusters": sum(z//L in built["inactive"]
                                                   for z in built["internal"]),
        "maximum_inactive_forest_depth": max(built["distance"].values()),
        "bit_inputs": count, "all_bit_inputs": exhaustive,
        "actual_map_locality_checks": 2*k,
        "rejected_locally_valid_discarded_cycle_corruption": rejected,
    }


def main():
    started = time.monotonic()
    V.RNG.seed(SEED)
    cases = [("C3", nx.cycle_graph(3), s, 4, None) for s in range(6)]
    cases += [("C4", nx.cycle_graph(4), s, 5, None) for s in (0, 7)]
    cases += [("K4", nx.complete_graph(4), i % 12, 5 if i % 2 else 10, sel)
              for i, sel in enumerate(product(range(2), repeat=4))]
    # Find several configurations with both a discarded cycle and at least
    # two retained cycles. The chosen local selectors are then fixed.
    base = nx.complete_graph(5)
    richer = []
    for _ in range(1000):
        selectors = [RNG.randrange(9) for _ in range(5)]
        pi = V.make_pi(base, selectors)
        cycles = V.cycle_list(pi)
        root, cutoff = RNG.randrange(20), 5
        kept = [c for c in cycles if len(c) >= cutoff or root in c]
        if len(kept) >= 2 and sum(map(len, kept)) < 20:
            richer.append(("K5", base, root, cutoff, selectors))
            if len(richer) == 8:
                break
    assert len(richer) == 8
    cases += richer
    rows = [check_case(*case) for case in cases]
    assert any(r["internal_clones_in_inactive_clusters"] > 0 for r in rows)
    assert any(r["maximum_inactive_forest_depth"] > 1 for r in rows)
    assert any(r["root_transition_changed"] for r in rows)
    result = {
        "status": "PASS", "seed": SEED,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "imported_graph_checker_sha256": hashlib.sha256((ROOT/"verify.py").read_bytes()).hexdigest(),
        "instances": rows,
        "total_instances": len(rows),
        "total_bit_inputs": sum(r["bit_inputs"] for r in rows),
        "total_actual_map_locality_checks": sum(r["actual_map_locality_checks"] for r in rows),
        "rejected_locally_valid_discarded_cycle_corruptions": sum(
            r["rejected_locally_valid_discarded_cycle_corruption"] for r in rows),
        "scope": [
            "The forest and routed gadget are checked on actual full neighbor maps.",
            "Inactive vertices remain in the completeness predicate and partitions.",
            "Some internal routes pass through inactive clusters with separate forest anchors.",
            "Toy routing is successful greedy BFS on complete multigraphs, not the asymptotic routing theorem.",
            "The short-mass event is not required on these deliberately small stress cases.",
            "Finite checks do not establish the asymptotic lower bound or novelty.",
        ],
        "elapsed_seconds": time.monotonic()-started,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (ROOT/"INACTIVE_FOREST_CHECK.json").write_text(
        json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: value for k, value in result.items() if k != "instances"}, indent=2))


if __name__ == "__main__":
    main()
