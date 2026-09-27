"""Exact finite checks of the examples, generator spans, and Lefschetz maps.

Polynomial monomials are sorted tuples of variable indices. Determinants
are expanded from permutations. No representation-theory package is used.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations
from math import comb, factorial
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parent.parent
START = time.monotonic()


def sign(perm):
    return (-1) ** sum(perm[i] > perm[j]
                       for i in range(len(perm)) for j in range(i+1, len(perm)))


def clean(poly, p):
    if p:
        return {m: c % p for m, c in poly.items() if c % p}
    return {m: c for m, c in poly.items() if c}


def matrix_data(n):
    edges = tuple(combinations_with_replacement(range(n), 2))
    return edges, {edge: i for i, edge in enumerate(edges)}


@lru_cache(None)
def determinant(n):
    edges, indices = matrix_data(n)
    out = defaultdict(int)
    for perm in permutations(range(n)):
        mon = tuple(sorted(indices[tuple(sorted((i, j)))]
                           for i, j in enumerate(perm)))
        out[mon] += sign(perm)
    return clean(out, None)


def differentiate(poly, variable, p):
    out = {}
    for mon, c in poly.items():
        if variable in mon:
            j = mon.index(variable)
            reduced = mon[:j] + mon[j+1:]
            out[reduced] = c * mon.count(variable)
    return clean(out, p)


def all_first_derivatives(poly, p):
    out = defaultdict(dict)
    for mon, c in poly.items():
        for variable, multiplicity in Counter(mon).items():
            j = mon.index(variable)
            out[variable][mon[:j] + mon[j+1:]] = c * multiplicity
    return [clean(col, p) for col in out.values()]


def apply_operator(poly, operator, p=None):
    out = defaultdict(int)
    for mon, coefficient in operator.items():
        col = poly
        for variable in mon:
            col = differentiate(col, variable, p)
        for residual, value in col.items():
            out[residual] += coefficient * value
    return clean(out, p)


def echelon(columns, p):
    basis = {}
    for col in columns:
        v = clean(col, p)
        while v:
            lead = min(v)
            if lead not in basis:
                inv = pow(int(v[lead]), -1, p) if p else Fraction(1, v[lead])
                basis[lead] = clean({m: c*inv for m, c in v.items()}, p)
                break
            coefficient = v[lead]
            for mon, value in basis[lead].items():
                new = v.get(mon, 0) - coefficient*value
                if p:
                    new %= p
                if new:
                    v[mon] = new
                else:
                    v.pop(mon, None)
    return list(basis.values())


def rank(columns, p):
    return len(echelon(columns, p))


def bounded_dyck(s, p):
    height = p-2 if p else s
    state = [1] + [0]*height
    for _ in range(2*s):
        new = [0]*(height+1)
        for j, value in enumerate(state):
            if j:
                new[j-1] += value
            if j < height:
                new[j+1] += value
        state = new
    return state[0]


def expected_hilbert(n, p):
    return [
        sum(comb(n, 2*s)*comb(n-2*s, k-s)*bounded_dyck(s, p)
            for s in range(min(k, n-k)+1))
        for k in range(n+1)
    ]


def derivative_spaces(n, p):
    spaces = [[clean(determinant(n), p)]]
    for k in range(n):
        columns = (col for poly in spaces[-1]
                   for col in all_first_derivatives(poly, p))
        spaces.append(echelon(columns, p))
    return spaces


def diagonal_derivative(poly, diagonal, p):
    out = defaultdict(int)
    for variable in diagonal:
        for mon, value in differentiate(poly, variable, p).items():
            out[mon] += value
    return clean(out, p)


def direct_lefschetz(n, p):
    spaces = derivative_spaces(n, p)
    h = [len(space) for space in spaces]
    assert h == expected_hilbert(n, p), (n, p, h)
    _, lookup = matrix_data(n)
    diagonal = [lookup[i, i] for i in range(n)]
    maps = []
    for k in range(n):
        images = spaces[k]
        for q in range(1, n-k+1):
            images = [diagonal_derivative(poly, diagonal, p) for poly in images]
            r = rank(images, p)
            maps.append(dict(degree=k, power=q, rank=r,
                             maximal_rank=min(h[k], h[k+q]),
                             kernel=h[k]-r))
    wlp = all(row["rank"] == row["maximal_rank"] for row in maps if row["power"] == 1)
    slp = all(row["rank"] == row["maximal_rank"] for row in maps)
    assert wlp == (n <= 2*p-2), (n, p, "WLP", maps)
    assert slp == (n < p), (n, p, "SLP", maps)
    if n == 2*p-1:
        middle = next(row for row in maps
                      if row["degree"] == p-1 and row["power"] == 1)
        assert middle["kernel"] == 1, middle
    return dict(n=n, p=p, hilbert=h, weak_lefschetz=wlp,
                strong_lefschetz=slp, maps=maps)


def vertex_degree(mon, edges, n):
    degree = [0]*n
    for variable in mon:
        i, j = edges[variable]
        degree[i] += 1
        degree[j] += 1
    return tuple(degree)


def monomial_enumerator(n):
    edges, lookup = matrix_data(n)

    @lru_cache(None)
    def enumerate_degree(alpha, lower=0):
        if not any(alpha):
            return ((),)
        out = []
        for v in range(lower, len(edges)):
            i, j = edges[v]
            if alpha[i] < 1 or alpha[j] < 1 or (i == j and alpha[i] < 2):
                continue
            reduced = list(alpha)
            reduced[i] -= 1
            reduced[j] -= 1
            for rest in enumerate_degree(tuple(reduced), v):
                out.append((v,)+rest)
        return tuple(out)
    return enumerate_degree


def partitions(total, maximum=None):
    if total == 0:
        yield ()
        return
    for value in range(min(total, maximum or total), 0, -1):
        for rest in partitions(total-value, value):
            yield (value,)+rest


def orbit_size(parts, n):
    result = factorial(n)//factorial(n-len(parts))
    for count in Counter(parts).values():
        result //= factorial(count)
    return result


def quadratic_generators(n):
    edges, d = matrix_data(n)

    def mon(*pairs):
        return tuple(sorted(d[tuple(sorted(pair))] for pair in pairs))

    out = []
    for i in range(n):
        out.append({mon((i, i), (i, i)): 1})
        for j in range(n):
            if i != j:
                out.append({mon((i, i), (i, j)): 1})
        for j, k in combinations([v for v in range(n) if v != i], 2):
            out.append({mon((i, j), (i, k)): 1,
                        mon((i, i), (j, k)): 1})
    for i, j in combinations(range(n), 2):
        out.append({mon((i, j), (i, j)): 1,
                    mon((i, i), (j, j)): 2})
    for i, j, k, l in combinations(range(n), 4):
        out.append({mon((i, j), (k, l)): 1,
                    mon((i, k), (j, l)): 1,
                    mon((i, l), (j, k)): 1})
    return out


def extra_generator(vertices, lookup):
    m = len(vertices)//2
    left, right = vertices[:m], vertices[m:]
    return {
        tuple(sorted(lookup[tuple(sorted((left[i], right[perm[i]])))]
                     for i in range(m))): sign(perm)
        for perm in permutations(range(m))
    }


def weighted_direct_hilbert(n, primes):
    edges, _ = matrix_data(n)
    enumerate_degree = monomial_enumerator(n)
    result = {p: [] for p in primes}
    for k in range(n//2+1):
        totals = dict.fromkeys(primes, 0)
        for s in range(min(k, n-k)+1):
            t = k-s
            alpha = (2,)*t + (1,)*(2*s) + (0,)*(n-t-2*s)
            operators = enumerate_degree(alpha)
            columns = [apply_operator(determinant(n), {op: 1}) for op in operators]
            weight = comb(n, 2*s)*comb(n-2*s, t)
            for p in primes:
                totals[p] += weight*rank(columns, p or None)
        for p in primes:
            result[p].append(totals[p])
        print("weighted derivative ranks", n, k, totals, flush=True)
    for p in primes:
        half = result[p]
        result[p] = half + (half[-2::-1] if n % 2 == 0 else half[::-1])
        assert result[p] == expected_hilbert(n, p), (n, p, result[p])
    return result


def degree_ideal_check(n, p, h):
    k = p-1
    edges, lookup = matrix_data(n)
    enumerate_degree = monomial_enumerator(n)
    quadrics = quadratic_generators(n)
    extras = [extra_generator(tuple(v), lookup)
              for v in combinations(range(n), 2*k)]
    def mon(*pairs):
        return tuple(sorted(lookup[tuple(sorted(pair))] for pair in pairs))
    representatives = [
        {mon((0, 0), (0, 0)): 1},
        {mon((0, 0), (0, 1)): 1},
        {mon((0, 1), (0, 1)): 1, mon((0, 0), (1, 1)): 2},
        {mon((0, 1), (0, 2)): 1, mon((0, 0), (1, 2)): 1},
        {mon((0, 1), (2, 3)): 1, mon((0, 2), (1, 3)): 1,
         mon((0, 3), (1, 2)): 1},
    ]
    for q in representatives:
        assert not apply_operator(determinant(n), q), (n, "quadratic containment")
    if extras:
        assert not apply_operator(determinant(n), extras[0], p), (n, p, "extra containment")
    families = [quadrics, extras]
    graded = [[(g, vertex_degree(next(iter(g)), edges, n)) for g in family]
              for family in families]
    totals = [0, 0]
    ambient_total = 0
    for parts in partitions(2*k):
        if len(parts) > n:
            continue
        alpha = parts+(0,)*(n-len(parts))
        ambient = enumerate_degree(alpha)
        weight = orbit_size(parts, n)
        ambient_total += weight*len(ambient)
        columns = []
        for group, generators in enumerate(graded):
            for generator, beta in generators:
                remaining = tuple(a-b for a, b in zip(alpha, beta))
                if min(remaining) < 0:
                    continue
                for factor in enumerate_degree(remaining):
                    columns.append({
                        tuple(sorted(mon+factor)): coefficient
                        for mon, coefficient in generator.items()
                    })
            totals[group] += weight*rank(columns, p)
    dim_s = comb(len(edges)+k-1, k)
    assert ambient_total == dim_s, (n, p, ambient_total, dim_s)
    assert totals[1] == dim_s-h[k], (n, p, totals, h)
    assert totals[1]-totals[0] == comb(n, 2*k)
    return dict(n=n, p=p, degree=k, ambient_dimension=dim_s,
                annihilator_dimension=dim_s-h[k],
                quadratic_ideal_dimension=totals[0],
                augmented_ideal_dimension=totals[1],
                independent_extra_generators=totals[1]-totals[0],
                containment_verified_by_literal_differentiation_and_index_symmetry=True)


def literal_cayley(n):
    edges, lookup = matrix_data(n)
    m = n//2
    generator = extra_generator(tuple(range(n)), lookup)
    result = apply_operator(determinant(n), generator)
    scalar = (-1)**m*factorial(m+1)
    assert result == {mon: scalar*c for mon, c in generator.items()}
    return dict(n=n, operator_degree=m, integer_factor=scalar,
                determinant_term_count=len(determinant(n)),
                result_term_count=len(result))


def boolean_boundary(p):
    n = 2*p-1
    blocks = []
    total_dimension = total_rank = 0
    for s in range(n//2+1):
        size = n-2*s
        j = p-1-s
        lower = list(combinations(range(size), j))
        columns = []
        for subset in lower:
            columns.append({tuple(sorted(subset+(x,))): 1
                            for x in range(size) if x not in subset})
        r = rank(columns, p)
        multiplicity = comb(n, 2*s)*bounded_dyck(s, p)
        total_dimension += multiplicity*len(lower)
        total_rank += multiplicity*r
        blocks.append(dict(boolean_size=size, degree=j,
                           dimension=len(lower), rank=r,
                           multiplicity=multiplicity))
    assert total_dimension-total_rank == 1
    return dict(n=n, p=p, method="Literal subset-inclusion matrices, assembled using Proposition 6.2",
                middle_dimension=total_dimension, middle_rank=total_rank,
                kernel=total_dimension-total_rank, blocks=blocks)


def main():
    report = {
        "scope": "Finite exact arithmetic; not a proof of the all-size theorems.",
        "integer_differentiation": [literal_cayley(4), literal_cayley(8)],
        "direct_derivative_and_lefschetz": [],
    }
    for n in range(1, 8):
        for p in (3, 5, 7, 101):
            row = direct_lefschetz(n, p)
            report["direct_derivative_and_lefschetz"].append(row)
            print("direct", n, p, row["hilbert"], "WLP", row["weak_lefschetz"],
                  "SLP", row["strong_lefschetz"], flush=True)
    h4 = weighted_direct_hilbert(4, (0, 3))
    report["size_four_exact_derivative_ranks"] = [
        dict(n=4, characteristic=p, hilbert=h, length=sum(h))
        for p, h in h4.items()
    ]
    h8 = weighted_direct_hilbert(8, (0, 3, 5, 7, 101))
    report["size_eight_exact_derivative_ranks"] = [
        dict(n=8, characteristic=p,
             arithmetic="rational" if not p else "prime field",
             hilbert=h, length=sum(h))
        for p, h in h8.items()
    ]
    report["degree_p_minus_one_ideal_checks"] = []
    for n in range(4, 9):
        h = h8[3] if n == 8 else next(
            r["hilbert"] for r in report["direct_derivative_and_lefschetz"]
            if r["n"] == n and r["p"] == 3)
        row = degree_ideal_check(n, 3, h)
        report["degree_p_minus_one_ideal_checks"].append(row)
        print("ideal", row, flush=True)
    row = degree_ideal_check(8, 5, h8[5])
    report["degree_p_minus_one_ideal_checks"].append(row)
    print("ideal", row, flush=True)
    report["boolean_boundary_checks"] = []
    for p in (3, 5, 7):
        row = boolean_boundary(p)
        report["boolean_boundary_checks"].append(row)
        print("Boolean boundary", p, row["middle_dimension"], row["middle_rank"], flush=True)
    report["passed"] = True
    report["seconds"] = time.monotonic()-START
    source = ROOT/"main.tex"
    report["manuscript_source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT/"anc/verification_results.json").write_text(
        json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print("ALL CHECKS PASSED", report["seconds"], flush=True)


if __name__ == "__main__":
    main()
