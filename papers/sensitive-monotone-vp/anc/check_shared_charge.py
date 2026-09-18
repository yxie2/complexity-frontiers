"""Exact stress checks for global gate replacement and the rectangle charge."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import random
import time

import check_shared_decomposition as S

ROOT = Path(__file__).resolve().parent
SEED = 202609151538


def constant(value):
    return {S.ZERO: F(value)} if value else {}


def setup():
    nodes = [("v", i) for i in range(S.VARIABLES)]
    pairs = []
    for i in range(S.G):
        nodes.append(("+", 2*i, 2*i+1))
        pairs.append(len(nodes)-1)
    nodes.append(("*", pairs[0], pairs[1]))
    u = len(nodes)-1
    v = pairs[2]
    for right in pairs[3:]:
        nodes.append(("*", v, right))
        v = len(nodes)-1
    return nodes, pairs, u, v


def linear_parts(poly):
    parts = [{}, {}]
    for exponent, coefficient in poly.items():
        assert exponent[S.Z] <= 1, "Nonlinear replacement polynomial"
        e = list(exponent)
        k = e[S.Z]
        e[S.Z] = 0
        e = tuple(e)
        parts[k][e] = parts[k].get(e, F(0)) + coefficient
    return parts


def dag_checks():
    depths = [0, 1, 8, 64, 256]
    checked = 0
    for depth in depths:
        nodes, _, u, v = setup()
        values = S.evaluate(nodes)
        up, vp = values[u], values[v]
        current = u
        for _ in range(depth):
            nodes.append(("+", current, current))
            current = len(nodes)-1
        nodes.append(("*", current, v))
        residual, context = linear_parts(S.evaluate(nodes, selected=u)[-1])
        expected = S.times(constant(2**depth), vp)
        assert not residual and context == expected
        assert S.evaluate(nodes)[-1] == S.times(up, expected)
        assert S.groups(S.evaluate(nodes)[-1]) == frozenset(range(S.G))
        checked += 1

    # Equal polynomials at distinct nodes must not be identified by a gate cut.
    nodes, pairs, u, v = setup()
    values = S.evaluate(nodes)
    up, vp = values[u], values[v]
    nodes.append(("*", pairs[0], pairs[1])); duplicate = len(nodes)-1
    nodes.append(("*", u, v)); first = len(nodes)-1
    nodes.append(("*", duplicate, v)); second = len(nodes)-1
    nodes.append(("+", first, second))
    residual, context = linear_parts(S.evaluate(nodes, selected=u)[-1])
    assert context == vp and residual == S.times(up, vp)
    assert S.evaluate(nodes, zeros={u})[-1] == residual
    assert S.plus(S.times(up, context), residual) == S.evaluate(nodes)[-1]
    checked += 1

    # A nonlinear dead branch contributes no coefficient after multiplication by zero.
    nodes, _, u, v = setup()
    nodes.append(("*", u, v)); valid = len(nodes)-1
    nodes.append(("*", u, u)); square = len(nodes)-1
    nodes.append(("c", F(0))); zero = len(nodes)-1
    nodes.append(("*", square, zero)); dead = len(nodes)-1
    nodes.append(("+", valid, dead))
    assert linear_parts(S.evaluate(nodes, selected=u)[-1])[0] == {}
    assert S.groups(S.evaluate(nodes)[-1]) == frozenset(range(S.G))
    checked += 1

    # Reciprocal internal rescalings must leave the charged product norm unchanged.
    scale_bits = [64, 256, 512]
    for bits in scale_bits:
        nodes, _, u, v = setup()
        original = S.times(S.evaluate(nodes)[u], S.evaluate(nodes)[v])
        nodes.append(("c", F(2**bits))); big = len(nodes)-1
        nodes.append(("*", u, big)); scaled_u = len(nodes)-1
        nodes.append(("c", F(1, 2**bits))); small = len(nodes)-1
        nodes.append(("*", v, small)); scaled_v = len(nodes)-1
        nodes.append(("*", scaled_u, scaled_v))
        values = S.evaluate(nodes)
        residual, context = linear_parts(S.evaluate(nodes, selected=scaled_u)[-1])
        assert not residual and values[-1] == original
        assert max(values[scaled_u].values()) == 2**bits
        assert max(context.values()) == F(1, 2**bits)
        assert max(values[scaled_u].values()) * max(context.values()) == 1
        checked += 1

    # Outside the lemma's hypotheses the replacement can have a genuine square.
    nodes, _, u, v = setup()
    nodes.append(("*", u, u)); square = len(nodes)-1
    nodes.append(("*", square, v))
    assert max(e[S.Z] for e in S.evaluate(nodes, selected=u)[-1]) == 2
    try:
        S.groups(S.evaluate(nodes)[-1])
    except AssertionError:
        invalid_rejected = True
    else:
        raise AssertionError("Repeated-group output was incorrectly admitted")
    return {
        "valid_global_replacement_fixtures": checked,
        "diamond_depths": depths,
        "maximum_context_multiplicity": str(2**max(depths)),
        "same_polynomial_distinct_node_fixture": "PASS",
        "nonlinear_zero_branch_fixture": "PASS",
        "reciprocal_rescaling_bits": scale_bits,
        "nonmultilinear_generalization_rejected": invalid_rejected,
    }


def level_terms(vector):
    previous = F(0)
    result = []
    for value in sorted(set(vector) - {F(0)}):
        result.append((value-previous, tuple(i for i, x in enumerate(vector) if x >= value)))
        previous = value
    return result


def rectangle_checks():
    rng = random.Random(SEED)
    total_rectangles = 0
    for case in range(80):
        u = [F(rng.randrange(9), rng.randrange(1, 6)) for _ in range(4)]
        v = [F(rng.randrange(9), rng.randrange(1, 6)) for _ in range(4)]
        u[0] = max(u[0], F(1, 3)); v[0] = max(v[0], F(1, 5))
        raw = [[rng.randrange(-7, 8) for _ in range(4)] for _ in range(4)]
        norm = sum(abs(x) for row in raw for x in row)
        assert norm > 0
        measure = [[F(x, norm) for x in row] for row in raw]
        discrepancy = F(0)
        for amask in range(16):
            for bmask in range(16):
                mass = sum((measure[i][j] for i in range(4) for j in range(4)
                            if amask & (1 << i) and bmask & (1 << j)), F(0))
                discrepancy = max(discrepancy, abs(mass))
                total_rectangles += 1
        reconstructed = [[F(0) for _ in range(4)] for _ in range(4)]
        weight = F(0)
        for a, rows in level_terms(u):
            for b, columns in level_terms(v):
                weight += a*b
                for i in rows:
                    for j in columns:
                        reconstructed[i][j] += a*b
        assert reconstructed == [[a*b for b in v] for a in u]
        assert weight == max(u)*max(v)
        charge = sum((measure[i][j]*u[i]*v[j] for i in range(4) for j in range(4)), F(0))
        assert abs(charge) <= discrepancy*weight
        # These vector coordinates can have arbitrary magnitude individually.
        scale = F(2**(case+1))
        assert max(a*scale for a in u)*max(b/scale for b in v) == weight
    return {"signed_measure_cases": 80, "rectangles_enumerated": total_rectangles,
            "exact_level_decomposition_and_charge": "PASS"}


def main():
    start = time.monotonic()
    result = {
        "status": "PASS", "seed": SEED,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "helper_sha256": hashlib.sha256((ROOT/"check_shared_decomposition.py").read_bytes()).hexdigest(),
        "global_replacement": dag_checks(),
        "rectangle_charge": rectangle_checks(),
        "scope": "Exact finite stress checks, supplementary to the first-principles proof of Lemma 4.1 and Proposition 4.2. These finite computations do not establish the asymptotic theorem.",
    }
    result["elapsed_seconds"] = time.monotonic()-start
    result["checked_at_utc"] = datetime.now(timezone.utc).isoformat()
    (ROOT/"SHARED_CHARGE_CHECK.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
