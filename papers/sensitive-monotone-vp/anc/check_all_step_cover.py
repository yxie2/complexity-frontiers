"""Exact checks for the uniform-permutation, backtracking-allowed extension."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import permutations, product
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

ROOT = Path(__file__).resolve().parent
SEED = 202609151104
RNG = random.Random(SEED)


def make_all_pi(base, selectors=None):
    states, index, _, neighbors = V.state_data(base)
    pi = [None]*len(states)
    for w, ns in neighbors.items():
        choices = list(permutations(ns))
        selected = choices[selectors[w]] if selectors is not None else RNG.choice(choices)
        for u, z in zip(ns, selected):
            pi[index[u, w]] = index[w, z]
    assert sorted(pi) == list(range(len(states)))
    assert all(pi[s] != s for s in range(len(states)))
    return pi


def partial_permutations():
    rows = []
    total = 0
    for d in range(2, 8):
        all_perms = list(permutations(range(d)))
        counts = Counter(
            tuple(p[i] if mask >> i & 1 else -1 for i in range(d))
            for p in all_perms for mask in range(1, 1 << d))
        for key, count in counts.items():
            k = sum(x >= 0 for x in key)
            assert count == factorial(d-k)
            assert count*d**k <= len(all_perms)*3**k
        total += len(counts)
        rows.append({"d": d, "permutations": len(all_perms),
                     "all_injective_nonempty_partial_maps": len(counts)})
    return {"rows": rows, "total_partial_maps": total}


def canon(c):
    i = c.index(min(c))
    return tuple(c[i:]+c[:i])


def moments():
    rows = []
    total = 0
    omitted_two_cycles_rejected = 0
    for name, base in [
        ("C3", nx.cycle_graph(3)), ("C4", nx.cycle_graph(4)),
        ("K4", nx.complete_graph(4)), ("K3,3", nx.complete_bipartite_graph(3, 3)),
    ]:
        states, _, _, ns = V.state_data(base)
        d = len(next(iter(ns.values())))
        hist = {g: Counter() for g in (3, 4, 6)}
        appearing = set()
        outcomes = 0
        two_cycle_outcomes = 0
        for selectors in product(range(factorial(d)), repeat=len(base)):
            cycles = V.cycle_list(make_all_pi(base, selectors))
            two_cycle_outcomes += any(len(c) == 2 for c in cycles)
            for g in hist:
                hist[g][sum(len(c) for c in cycles if len(c) < g)] += 1
            appearing.update(canon(c) for c in cycles if len(c) < 6)
            outcomes += 1
        cycle_counts = Counter(map(len, appearing))
        assert cycle_counts[2] == base.number_of_edges()
        checks = []
        for g in hist:
            expected_numerator = sum((1 << w)*count for w, count in hist[g].items())
            numerator = denominator = 1
            for length, count in cycle_counts.items():
                if length < g:
                    numerator *= (d**length+((1 << length)-1)*3**length)**count
                    denominator *= d**(length*count)
            assert expected_numerator*denominator <= outcomes*numerator
            checks.append({
                "cutoff": g, "short_state_mass_histogram": dict(sorted(hist[g].items())),
                "exact_E_2_power_W": str(Fraction(expected_numerator, outcomes)),
                "exact_product_upper_bound_passed": True,
                "product_numerator_bits": numerator.bit_length(),
            })
        # At g=3 only two-cycles count. Omitting them would give the false bound 1.
        assert sum((1 << w)*count for w, count in hist[3].items()) > outcomes
        omitted_two_cycles_rejected += 1
        total += outcomes
        rows.append({"base": name, "states": len(states), "degree": d,
                     "all_local_permutation_covers": outcomes,
                     "covers_containing_two_cycles": two_cycle_outcomes,
                     "appearing_short_cycle_counts": dict(sorted(cycle_counts.items())),
                     "moment_checks": checks})
    return {"rows": rows, "total_covers": total,
            "rejected_omission_of_length_two_cycles": omitted_two_cycles_rejected}


def trace_identity():
    rows = []
    t = sp.Symbol("t")
    for name, base in [
        ("K4", nx.complete_graph(4)), ("K3,3", nx.complete_bipartite_graph(3, 3)),
        ("K5", nx.complete_graph(5)), ("Petersen", nx.petersen_graph()),
    ]:
        states, _, _, ns = V.state_data(base)
        n, v = len(base), len(states)
        U, T = sp.zeros(v, n), sp.zeros(n, v)
        for i, (u, w) in enumerate(states):
            U[i, w] = 1
            T[u, i] = 1
        A = sp.Matrix(nx.to_numpy_array(base, dtype=int).tolist())
        M = U*T
        assert T*U == A
        assert sp.trace(M) == 0 and sp.trace(M*M) == v
        assert sp.Poly(M.charpoly(t).as_expr(), t) == sp.Poly(
            t**(v-n)*A.charpoly(t).as_expr(), t)
        rows.append({"base": name, "state_matrix_dimension": v,
                     "exact_incidence_products": True,
                     "exact_characteristic_polynomial_identity": True,
                     "length_two_trace": v})
    return rows


def forest_cases():
    old_make = V.make_pi
    V.make_pi = make_all_pi
    F.RNG.seed(SEED)
    try:
        cases = []
        for i, selectors in enumerate(product(range(2), repeat=3)):
            cases.append(("C3", nx.cycle_graph(3), i % 6, 3 if i % 2 else 4, selectors))
        for i, selectors in enumerate(product(range(2), repeat=4)):
            cases.append(("C4", nx.cycle_graph(4), i % 8, 3 if i % 2 else 5, selectors))
        base = nx.complete_graph(4)
        richer = []
        for _ in range(2000):
            selectors = [RNG.randrange(6) for _ in range(4)]
            pi = make_all_pi(base, selectors)
            cycles = V.cycle_list(pi)
            root, cutoff = RNG.randrange(12), 3
            kept = [c for c in cycles if len(c) >= cutoff or root in c]
            if len(kept) >= 2 and sum(map(len, kept)) < 12:
                richer.append(("K4", base, root, cutoff, selectors))
                if len(richer) == 12:
                    break
        assert len(richer) == 12
        cases += richer
        rows = [F.check_case(*case) for case in cases]
        assert any(r["active_states"] == 2 for r in rows)
        assert any(r["internal_clones_in_inactive_clusters"] for r in rows)
        assert any(r["maximum_inactive_forest_depth"] > 1 for r in rows)
        assert any(r["root_transition_changed"] for r in rows)
        return {
            "instances": rows, "total_instances": len(rows),
            "total_bit_inputs": sum(r["bit_inputs"] for r in rows),
            "actual_map_locality_checks": sum(r["actual_map_locality_checks"] for r in rows),
            "rejected_locally_valid_discarded_cycle_corruptions": sum(
                r["rejected_locally_valid_discarded_cycle_corruption"] for r in rows),
        }
    finally:
        V.make_pi = old_make


def constants():
    d = 734
    delta = Fraction(2, 5)
    eta, zeta = delta**2/100, delta**2/800
    coefficient = Fraction(18, d*d)+Fraction(64, 1215*d)
    assert coefficient == Fraction(34423, 327294270)
    assert coefficient < 11*zeta/20
    assert eta == Fraction(1, 625) and zeta == Fraction(1, 5000)
    assert Fraction(25, 54) > delta
    assert d*d > 300*97
    assert 100/delta**2+2 == 627
    assert Fraction(2, 3)-Fraction(3, 5) == Fraction(1, 15)
    assert zeta/15 == Fraction(1, 75000)
    return {"moment_coefficient": str(coefficient), "budget": str(11*zeta/20),
            "eta": str(eta), "zeta": str(zeta), "mass_tail_exponent": "v/75000"}


def main():
    started = time.monotonic()
    result = {
        "status": "PASS", "seed": SEED,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "imported_sources": [
            {"path": name, "sha256": hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}
            for name in ("verify.py", "check_inactive_forest.py")],
        "partial_permutation_checks": partial_permutations(),
        "exact_cycle_moments": moments(),
        "exact_trace_checks": trace_identity(),
        "uniform_cover_forest_checks": forest_cases(),
        "exact_constants": constants(),
        "scope": [
            "Uniform local permutations include immediate reversals and two-state cycles.",
            "Every listed local cover and partial permutation is checked exhaustively.",
            "The complete physical-map checks include inactive vertices and internal routes.",
            "Toy hosts and routing do not establish the asymptotic spectral or routing hypotheses.",
            "The written proof is still needed for the general theorem and its exponent.",
            "Finite verification does not certify novelty or replace human review.",
        ],
        "elapsed_seconds": time.monotonic()-started,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (ROOT/"ALL_STEP_COVER_CHECK.json").write_text(
        json.dumps(result, indent=2)+"\n", encoding="utf-8")
    short = {k: value for k, value in result.items()
             if k not in ("exact_cycle_moments", "uniform_cover_forest_checks")}
    short["local_cover_count"] = result["exact_cycle_moments"]["total_covers"]
    short["forest_summary"] = {k: v for k, v in result["uniform_cover_forest_checks"].items()
                               if k != "instances"}
    print(json.dumps(short, indent=2))


if __name__ == "__main__":
    main()
