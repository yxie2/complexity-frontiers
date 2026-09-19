"""Exact BEST counting, uniform sampler, and direct physical gadget checks."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations, permutations, product
from math import factorial
from pathlib import Path
import hashlib
import json
import random
import time

import networkx as nx
import sympy as sp

import verify as V
import check_inactive_forest as F
from check_all_step_cover import make_all_pi

ROOT = Path(__file__).resolve().parent
SEED = 202609151126
RNG = random.Random(SEED)


def tour_from_orders(base, orders, start=0):
    positions = {u: 0 for u in base}
    current, tour = start, []
    while positions[current] < len(orders[current]):
        target = orders[current][positions[current]]
        positions[current] += 1
        tour.append((current, target))
        current = target
    return tour, current


def transition_from_tour(base, tour):
    states, index, _, _ = V.state_data(base)
    assert len(tour) == len(states) and set(tour) == set(states)
    pi = [None]*len(states)
    for i, edge in enumerate(tour):
        following = tour[(i+1) % len(tour)]
        assert edge[1] == following[0]
        pi[index[edge]] = index[following]
    assert len(V.cycle_list(pi)) == 1
    return tuple(pi)


def enumerate_best(base):
    n, d = len(base), base.degree[0]
    trees = []
    for edges in combinations(base.edges(), n-1):
        tree = nx.Graph()
        tree.add_nodes_from(base)
        tree.add_edges_from(edges)
        if nx.is_tree(tree):
            trees.append(tree)
    images = Counter()
    wrong_last_exit_rejected = 0
    for tree in trees:
        parent = {child: root for root, child in nx.bfs_edges(tree, 0)}
        options = []
        for u in sorted(base):
            ns = sorted(base[u])
            options.append(list(permutations(ns)) if u == 0 else
                           [p+(parent[u],) for p in permutations([w for w in ns if w != parent[u]])])
        for choices in product(*options):
            orders = dict(zip(sorted(base), choices))
            tour, finish = tour_from_orders(base, orders)
            assert finish == 0
            pi = transition_from_tour(base, tour)
            images[pi] += 1
            last = {}
            for u, w in tour:
                last[u] = w
            assert all(last[u] == parent[u] for u in parent)
            if not wrong_last_exit_rejected:
                corrupted = {u: order if u == 0 else (order[-1],)+order[:-1]
                             for u, order in orders.items()}
                bad_tour, _ = tour_from_orders(base, corrupted)
                if len(bad_tour) < n*d:
                    wrong_last_exit_rejected = 1
    expected = len(trees)*factorial(d-1)**n
    assert len(images) == expected and set(images.values()) == {d}
    assert sum(images.values()) == len(trees)*factorial(d)*factorial(d-1)**(n-1)
    return trees, images, wrong_last_exit_rejected


def check_base(name, base):
    n, d = len(base), base.degree[0]
    all_covers = Counter()
    for selectors in product(range(factorial(d)), repeat=n):
        pi = tuple(make_all_pi(base, selectors))
        if len(V.cycle_list(list(pi))) == 1:
            all_covers[pi] += 1
    assert set(all_covers.values()) == {1}
    trees, images, rejected = enumerate_best(base)
    assert set(images) == set(all_covers)
    A = sp.Matrix(nx.to_numpy_array(base, dtype=int).tolist())
    laplacian = d*sp.eye(n)-A
    tree_count = int(laplacian[1:, 1:].det())
    t = sp.Symbol("t")
    derivative_count = sp.diff(A.charpoly(t).as_expr(), t).subs(t, d)/n
    assert derivative_count == tree_count == len(trees)
    probability = Fraction(len(all_covers), factorial(d)**n)
    assert probability == Fraction(tree_count, d**n)
    return {
        "base": name, "n": n, "d": d, "states": n*d,
        "all_local_covers": factorial(d)**n,
        "single_cycle_covers": len(all_covers),
        "spanning_trees": tree_count, "exact_conditioning_probability": str(probability),
        "BEST_sampler_linear_tours": sum(images.values()),
        "preimages_per_cyclic_configuration": d,
        "false_tree_edge_first_sampler_rejected": rejected,
        "exact_matrix_tree_spectral_product_identity": True,
    }, sorted(all_covers)


def physical_checks(name, base, covers):
    selected = covers if len(covers) <= 8 else RNG.sample(covers, 8)
    rows = []
    states = V.state_data(base)[0]
    old_make = V.make_pi
    try:
        for pi in selected:
            V.make_pi = lambda graph, selectors=None, value=pi: list(value)
            for root_state in (0, len(pi)-1):
                built = F.make_gadget(base, root_state, 0)
                assert not built["changed"] and not built["paths"]
                assert not built["inactive"] and not built["internal"]
                L, k, root = built["L"], built["k"], built["root"]
                # Check every possible direct arc against the actual base
                # clique blow-up, not merely the complete toy routing graph.
                for z in range(len(built["fixed"])):
                    if z == root:
                        continue
                    destinations = (built["switches"][z][1] if z in built["switches"]
                                    else [built["fixed"][z]])
                    for target in destinations:
                        tail_u = states[z//L][0]
                        tail_w = states[target//L][0]
                        assert z != target
                        assert tail_u == tail_w or base.has_edge(tail_u, tail_w)
                inputs = (product([0, 1], repeat=2*k) if k <= 5 else
                          ([RNG.randrange(2) for _ in range(2*k)] for _ in range(512)))
                count = 0
                for bits in inputs:
                    parity = sum(bits[i]*bits[k+i] for i in range(k)) % 2
                    assert V.all_reach(F.outgoing(built, bits), root) == bool(parity)
                    count += 1
                witness = [0]*(2*k)
                witness[0] = witness[k] = 1
                valid = F.outgoing(built, witness)
                assert V.all_reach(valid, root)
                # A locally valid replacement of the root exit by the c0
                # terminal traps the gadget in a cycle on this odd input.
                c0, c1 = built["a"][root_state]
                valid[c1] = c0
                assert c0 != c1 and c0//L == c1//L
                assert not V.all_reach(valid, root)
                rows.append({"base": name, "root_state": root_state,
                             "states": len(pi), "physical_vertices": len(built["fixed"]),
                             "bit_inputs": count, "all_bit_inputs": k <= 5,
                             "all_arcs_checked_in_base_clique_blowup": True,
                             "routed_arcs": 0, "discarded_states": 0,
                             "locally_valid_root_exit_corruption_rejected": True})
    finally:
        V.make_pi = old_make
    return rows


def exposure_checks():
    cases = 0
    # Exact conditional means for the rank-one local matching score after
    # any prefix. Counts describe every possible remaining binary pattern.
    for remaining in range(2, 101):
        for a_current in (0, 1):
            for a_other in range(remaining):
                for b_count in range(1, remaining):
                    means = [
                        a_current*b+a_other*Fraction(b_count-b, remaining-1)
                        for b in (0, 1)]
                    assert abs(means[0]-means[1]) <= 1
                    cases += 1
    # Our proof uses the weaker safe range 2 and adds range 2 for each
    # whole clone-placement block, giving squared-range budget <=8v.
    return {"exact_conditional_mean_configurations": cases,
            "observed_proved_upper_range": 1,
            "range_used_in_theorem": 2}


def constants():
    eta, tau = Fraction(1, 200), Fraction(1, 640000)
    assert tau == eta**2/16
    d, L = 734, 1024
    mean_margin = Fraction(4, 625)-Fraction(1, 2*(L-1))-eta
    assert mean_margin == Fraction(4661, 5115000)
    assert 2500*mean_margin > 2
    assert Fraction(27, 50*d*d) < 2*tau/3
    assert 2**32 > 32*3840000
    c = Fraction(1, 7680000)
    DH, K = (d+1)*d*L-1, L*((d+1)*d*L-1)
    assert c*2**32 > 10
    return {"eta": str(eta), "tau": str(tau), "mean_margin": str(mean_margin),
            "conditioning_rate_bound": str(Fraction(27, 50*d*d)),
            "conditioning_budget": str(2*tau/3),
            "state_count_cutoff": 2**32, "c": str(c),
            "physical_degree": DH, "N_upper_factor_K": K,
            "a": str(c/(2*K)), "b": str(c/(3*K))}


def main():
    started = time.monotonic()
    F.RNG.seed(SEED)
    rows, physical = [], []
    for name, base in [
        ("C3", nx.cycle_graph(3)), ("C4", nx.cycle_graph(4)),
        ("K4", nx.complete_graph(4)), ("K3,3", nx.complete_bipartite_graph(3, 3)),
    ]:
        row, covers = check_base(name, base)
        rows.append(row)
        physical.extend(physical_checks(name, base, covers))
    result = {
        "status": "PASS", "seed": SEED,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "imported_sources": [
            {"path": name, "sha256": hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}
            for name in ("verify.py", "check_inactive_forest.py", "check_all_step_cover.py")],
        "exact_BEST_checks": rows,
        "permutation_exposure_checks": exposure_checks(),
        "direct_physical_gadgets": physical,
        "total_physical_instances": len(physical),
        "total_bit_inputs": sum(r["bit_inputs"] for r in physical),
        "exact_constants": constants(),
        "scope": [
            "All local covers and all last-exit sampler descriptions of the listed bases were enumerated.",
            "Uniformity is checked by exact constant preimage counts, not empirical sampling frequencies.",
            "Physical tests verify direct edges in the actual base clique blow-up.",
            "No routing or discarded-cycle forest is used in these physical tests.",
            "The toy bases do not satisfy the asymptotic spectral hypothesis.",
            "The general theorem is established by the written proof, not these finite tests.",
        ],
        "elapsed_seconds": time.monotonic()-started,
        }
    (ROOT/"EULER_CONDITIONING_CHECK.json").write_text(
        json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "direct_physical_gadgets"}, indent=2))


if __name__ == "__main__":
    main()
