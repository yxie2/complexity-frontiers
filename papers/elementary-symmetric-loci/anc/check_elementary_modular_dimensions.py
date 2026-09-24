"""Exact independent coefficient and small Groebner controls.

The dimension theorem is proved in the accompanying manuscript, Theorem 1.1.
These finite checks do not replace that proof. SymPy is needed only for
the optional --groebner controls; all coefficient controls use the stdlib.
"""
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def prime_power(p, degree, strict=False):
    q = 1
    while q < degree or (strict and q == degree):
        q *= p
    return q


def partitions(n, k, minimum=1):
    if k == 1:
        if n >= minimum:
            yield (n,)
        return
    for first in range(minimum, n // k + 1):
        for rest in partitions(n-first, k-1, first):
            yield (first,) + rest


@lru_cache(None)
def powers_with_nonzero_coefficient(m, p, degree):
    return tuple(j for j in range(min(m, degree)+1) if comb(m, j) % p)


@lru_cache(None)
def restricted_polynomial_nonzero(multiplicities, p, degree):
    # Variables belonging to different blocks are independent. Each vector
    # of exponents occurs once, with coefficient product binom(m_i,j_i).
    # Thus possible total degrees combine by boolean, not numerical, sums.
    mask = (1 << (degree+1))-1
    attainable = 1
    for m in multiplicities:
        next_attainable = 0
        for j in powers_with_nonzero_coefficient(m, p, degree):
            next_attainable |= attainable << j
        attainable = next_attainable & mask
    return bool(attainable & (1 << degree))


def actual_partition_conditions(sizes, p, d):
    critical = True
    for i in range(len(sizes)):
        reduced = list(sizes)
        reduced[i] -= 1
        if restricted_polynomial_nonzero(tuple(sorted(reduced)), p, d-1):
            critical = False
            break
    order_two = critical and not restricted_polynomial_nonzero(sizes, p, d)
    return critical, order_two


def coefficient_checks(max_n):
    count = 0
    dimension_controls = 0
    exceptional = [0, 0]
    for p in (2, 3, 5, 7, 11):
        for d in range(2, min(12, max_n)+1):
            pm, pp = prime_power(p, d), prime_power(p, d, strict=True)
            for n in range(d, max_n+1):
                any_actual = [False, False]
                for sizes in partitions(n, d-1):
                    actual = actual_partition_conditions(sizes, p, d)
                    predicted = (all((m-1) % pm == 0 for m in sizes),
                                 all((m-1) % pp == 0 for m in sizes))
                    assert actual == predicted, (p, n, d, sizes, actual, predicted)
                    for j in (0, 1):
                        any_actual[j] |= actual[j]
                        exceptional[j] += actual[j]
                    count += 1
                assert any_actual == [(n-d+1) % pm == 0, (n-d+1) % pp == 0]
                dimension_controls += 2
        print('COEFFICIENT PRIME', p, 'partition controls', count, flush=True)
    # Targets with characteristic-power degree and much larger n. These
    # exercise the strict/non-strict threshold independently of small n.
    large = []
    for p in (2, 3, 5, 7, 11):
        for exponent in (1, 2):
            d = p**exponent
            for quotient in (1, p, p+1):
                sizes = (1,)*(d-2) + (1+quotient*d,)
                actual = actual_partition_conditions(sizes, p, d)
                assert actual == (True, quotient % p == 0)
                large.append(dict(p=p, d=d, n=sum(sizes), quotient=quotient,
                                  critical=actual[0], order_two=actual[1]))
    return dict(partition_controls=count, dimension_controls=dimension_controls,
                exceptional_partitions=exceptional, large_boundary_controls=large)


def monomial_ideal_dimension(groebner, variables):
    supports = []
    for polynomial in groebner.polys:
        lm = polynomial.monoms(order=groebner.order)[0]
        support = {i for i, exponent in enumerate(lm) if exponent}
        if not support:
            return -1
        supports.append(support)
    # Height of a monomial ideal is minimum size of a variable set hitting
    # every generator support; this avoids assuming a dimension API.
    for height in range(variables+1):
        for subset in combinations(range(variables), height):
            hit = set(subset)
            if all(hit & support for support in supports):
                return variables-height
    raise AssertionError('No vertex cover found')


def groebner_checks(max_n):
    import sympy as sp
    rows = []
    for p in (2, 3, 5):
        for n in range(2, max_n+1):
            x = sp.symbols(f'x0:{n}')
            for d in range(2, n+1):
                polynomial = sum(sp.prod(x[i] for i in subset)
                                 for subset in combinations(range(n), d))
                gradient = [sp.diff(polynomial, variable) for variable in x]
                dimensions = []
                for include_value in (False, True):
                    generators = gradient + ([polynomial] if include_value else [])
                    gb = sp.groebner(generators, *x, modulus=p, order='grevlex')
                    dimension = monomial_ideal_dimension(gb, n)
                    pp = prime_power(p, d, strict=include_value)
                    expected = d-1 if (n-d+1) % pp == 0 else d-2
                    assert dimension == expected, (p, n, d, include_value, dimension, expected)
                    dimensions.append(dimension)
                rows.append(dict(p=p, n=n, d=d, critical_dimension=dimensions[0],
                                 order_two_dimension=dimensions[1]))
            print('GROEBNER', p, n, 'completed', flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=28)
    parser.add_argument('--groebner', action='store_true')
    parser.add_argument('--groebner-max-n', type=int, default=6)
    args = parser.parse_args()
    start = time.monotonic()
    report = dict(status='PASS', coefficient_checks=coefficient_checks(args.max_n))
    if args.groebner:
        report['groebner_checks'] = groebner_checks(args.groebner_max_n)
    report['seconds'] = time.monotonic()-start
    report['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['scope'] = 'Finite exact coefficient controls and, when requested, independent Groebner dimensions; the general theorem requires the written proof.'
    output = HERE / 'ELEMENTARY_MODULAR_DIMENSION_CHECKS.json'
    output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS', report['coefficient_checks']['partition_controls'],
          'partition controls;', len(report.get('groebner_checks', []))*2,
          'Groebner dimensions;', report['seconds'], 'seconds', flush=True)


if __name__ == '__main__':
    main()
