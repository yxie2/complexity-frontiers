"""Exact finite checks for Dimensions of permanental varieties in arbitrary size.

Python 3.10 or newer; standard library only. Polynomial coefficients are integers.
These checks supplement, and do not replace, the arguments for arbitrary size.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path


# A monomial is a sorted tuple of variable names; repetitions are exponents.
# A polynomial is a dictionary from monomials to nonzero integer coefficients.
Poly = dict[tuple[str, ...], int]
ONE: Poly = {(): 1}


def variable(name: str) -> Poly:
    return {(name,): 1}


def add(*polynomials: Poly) -> Poly:
    answer: Counter = Counter()
    for polynomial in polynomials:
        for monomial, coefficient in polynomial.items():
            answer[monomial] += coefficient
    return {m: c for m, c in answer.items() if c}


def scale(polynomial: Poly, coefficient: int) -> Poly:
    return {m: c * coefficient for m, c in polynomial.items() if c * coefficient}


def multiply(*polynomials: Poly) -> Poly:
    answer = ONE
    for polynomial in polynomials:
        terms: Counter = Counter()
        for m, c in answer.items():
            for n, d in polynomial.items():
                terms[tuple(sorted(m + n))] += c * d
        answer = {m: c for m, c in terms.items() if c}
    return answer


def highest(polynomial: Poly, weighted_variables: set[str]) -> Poly:
    if not polynomial:
        return {}
    degrees = {m: sum(v in weighted_variables for v in m) for m in polynomial}
    top_degree = max(degrees.values())
    return {m: c for m, c in polynomial.items() if degrees[m] == top_degree}


@lru_cache(maxsize=None)
def permanent_names(matrix: tuple[tuple[str, ...], ...]) -> Poly:
    """Literal permutation expansion, with the name '1' denoting the pivot."""
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("A permanent requires a square matrix")
    terms: Counter = Counter()
    for permutation in permutations(range(n)):
        monomial = tuple(sorted(matrix[i][permutation[i]] for i in range(n)
                                if matrix[i][permutation[i]] != "1"))
        terms[monomial] += 1
    return dict(terms)


def minor(y, rows, columns) -> Poly:
    return permanent_names(tuple(tuple(y[i][j] for j in columns) for i in rows))


def bordered(y, u, v, rows, columns) -> Poly:
    matrix = [tuple(y[i][j] for j in columns) + (u[i],) for i in rows]
    matrix.append(tuple(v[j] for j in columns) + ("1",))
    return permanent_names(tuple(matrix))


def avoiding_pivot_column(y, v, rows, columns) -> Poly:
    matrix = [tuple(y[i][j] for j in columns) for i in rows]
    matrix.append(tuple(v[j] for j in columns))
    return permanent_names(tuple(matrix))


def cubic(y, u, v, rows, columns) -> Poly:
    terms = []
    for i in rows:
        for j, ell in combinations(columns, 2):
            core_rows = tuple(a for a in rows if a != i)
            core_columns = tuple(b for b in columns if b not in (j, ell))
            terms.append(multiply(variable(u[i]), variable(v[j]), variable(v[ell]),
                                  minor(y, core_rows, core_columns)))
    return add(*terms)


def variables(a: int, b: int):
    y = tuple(tuple(f"y{i}_{j}" for j in range(b)) for i in range(a))
    u = tuple(f"u{i}" for i in range(a))
    v = tuple(f"v{j}" for j in range(b))
    return y, u, v


def transpose(y):
    return tuple(zip(*y))


def check_equal(actual: Poly, expected: Poly, label: str, counts: Counter) -> None:
    if actual != expected:
        difference = add(actual, scale(expected, -1))
        raise AssertionError(f"{label}: nonzero difference {difference}")
    counts[label.split(":", 1)[0]] += 1


def check_square_pivots(counts: Counter) -> None:
    for h in range(2, 6):
        m = h
        indices = tuple(range(m))
        y, u, v = variables(m, m)
        y_variables = {name for row in y for name in row}
        for rows in combinations(indices, h - 1):
            for columns in combinations(indices, h - 1):
                p = minor(y, rows, columns)
                correction = add(*(multiply(variable(u[i]), variable(v[j]),
                                    minor(y, tuple(a for a in rows if a != i),
                                          tuple(b for b in columns if b != j)))
                                   for i in rows for j in columns))
                full = bordered(y, u, v, rows, columns)
                check_equal(full, add(p, correction), f"border_expansion:{h}", counts)
                check_equal(highest(full, y_variables), p,
                            f"interior_highest_part:{h}", counts)

        for oriented_y, oriented_u, oriented_v in ((y, u, v), (transpose(y), v, u)):
            for rows in combinations(indices, h - 1):
                lhs = add(*(multiply(variable(oriented_v[j]),
                                     bordered(oriented_y, oriented_u, oriented_v,
                                              rows, tuple(b for b in indices if b != j)))
                            for j in indices),
                          scale(avoiding_pivot_column(oriented_y, oriented_v,
                                                     rows, indices), -1))
                rhs = cubic(oriented_y, oriented_u, oriented_v, rows, indices)
                check_equal(lhs, scale(rhs, 2), f"cubic_identity:{h}", counts)
                check_equal(highest(rhs, y_variables), rhs,
                            f"cubic_interior_homogeneity:{h}", counts)

            for core_rows in combinations(indices, h - 2):
                for core_columns in combinations(indices, h - 2):
                    outside_rows = tuple(i for i in indices if i not in core_rows)
                    outside_columns = tuple(j for j in indices if j not in core_columns)
                    outside = {oriented_u[i] for i in outside_rows}
                    outside.update(oriented_v[j] for j in outside_columns)
                    core = minor(oriented_y, core_rows, core_columns)
                    for i in outside_rows:
                        for j, ell in combinations(outside_columns, 2):
                            polynomial = cubic(oriented_y, oriented_u, oriented_v,
                                               tuple(sorted(core_rows + (i,))),
                                               tuple(sorted(core_columns + (j, ell))))
                            expected = multiply(core, variable(oriented_u[i]),
                                                variable(oriented_v[j]),
                                                variable(oriented_v[ell]))
                            check_equal(highest(polynomial, outside), expected,
                                        f"border_highest_part:{h}", counts)


def check_rectangular_pivots(counts: Counter) -> None:
    for k in range(2, 6):
        y, u, v = variables(k - 1, k)
        rows, columns = tuple(range(k - 1)), tuple(range(k))
        s = cubic(y, u, v, rows, columns)
        lhs = add(*(multiply(variable(v[j]),
                             bordered(y, u, v, rows,
                                      tuple(b for b in columns if b != j)))
                    for j in columns),
                  scale(avoiding_pivot_column(y, v, rows, columns), -1))
        check_equal(lhs, scale(s, 2), f"near_square_identity:{k}", counts)
        for core_rows in combinations(rows, k - 2):
            for core_columns in combinations(columns, k - 2):
                i, = (i for i in rows if i not in core_rows)
                j, ell = (j for j in columns if j not in core_columns)
                outside = {u[i], v[j], v[ell]}
                expected = multiply(minor(y, core_rows, core_columns), variable(u[i]),
                                    variable(v[j]), variable(v[ell]))
                check_equal(highest(s, outside), expected,
                            f"near_square_highest_part:{k}", counts)


def check_supports() -> dict:
    rows = []
    total = 0
    for k in range(2, 9):
        maximum = -1
        accepted = 0
        masks = tuple(product((0, 1), repeat=k))
        for u in masks:
            for v in masks:
                equations_hold = (
                    all(not (u[i] and v[j] and v[ell])
                        for i in range(k) for j, ell in combinations(range(k), 2))
                    and all(not (u[i] and u[ii] and v[j])
                            for i, ii in combinations(range(k), 2) for j in range(k)))
                predicted = not any(u) or not any(v) or (sum(u) <= 1 and sum(v) <= 1)
                if equations_hold != predicted:
                    raise AssertionError((k, u, v))
                if equations_hold:
                    accepted += 1
                    maximum = max(maximum, sum(u) + sum(v))
                total += 1
        if maximum != k:
            raise AssertionError((k, maximum))
        rows.append({"k": k, "support_pairs": 4**k,
                     "accepted_support_pairs": accepted, "maximum_dimension": maximum})
    return {"total_support_pairs": total, "cases": rows}


def run() -> dict:
    counts: Counter = Counter()
    check_square_pivots(counts)
    check_rectangular_pivots(counts)
    return {
        "status": "passed",
        "arithmetic": "exact integers; literal permutation expansion",
        "identity_sizes": [2, 3, 4, 5],
        "polynomial_checks": dict(sorted(counts.items())),
        "total_polynomial_checks": sum(counts.values()),
        "support_checks": check_supports(),
        "scope": "Finite identities and supports only; not a proof of the all-size theorems."
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the JSON report to this path")
    parser.add_argument("--compare", type=Path, help="Require exact agreement with an existing JSON report")
    args = parser.parse_args()
    report = run()
    if args.compare:
        expected = json.loads(args.compare.read_text(encoding="utf-8"))
        if report != expected:
            raise AssertionError("Report does not match the supplied expected output")
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
