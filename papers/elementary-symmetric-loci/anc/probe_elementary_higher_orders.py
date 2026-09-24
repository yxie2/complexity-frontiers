"""Exact checks for the higher derivative and multiplicity dimension formulas."""
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import time

import check_elementary_modular_dimensions as first

HERE = Path(__file__).resolve().parent


def removals(sizes, total):
    if len(sizes) == 1:
        if 0 <= total <= sizes[0]:
            yield (total,)
        return
    for a in range(min(total, sizes[0])+1):
        for rest in removals(sizes[1:], total-a):
            yield (a,)+rest


def all_partials_vanish(sizes, p, d, order):
    for removed in removals(sizes, order):
        left = tuple(sorted(m-a for m, a in zip(sizes, removed)))
        if first.restricted_polynomial_nonzero(left, p, d-order):
            return False
    return True


def coefficients(max_n):
    count = 0
    dimension_controls = 0
    for p in (2, 3, 5, 7):
        for d in range(3, min(11, max_n)+1):
            for q in range(2, d):
                r = d-q
                small = first.prime_power(p, r, strict=True)
                large = first.prime_power(p, d, strict=True)
                for n in range(d, max_n+1):
                    any_actual = [False, False]
                    for sizes in first.partitions(n, r):
                        c = all_partials_vanish(sizes, p, d, q)
                        z = c and all(all_partials_vanish(sizes, p, d, h)
                                      for h in range(q))
                        shape = sum(m > 1 for m in sizes) == 1
                        expected = (shape and (n-d+1) % small == 0,
                                    shape and (n-d+1) % large == 0)
                        assert (c, z) == expected, (p, n, d, q, sizes, c, z, expected)
                        any_actual[0] |= c
                        any_actual[1] |= z
                        count += 1
                    assert any_actual == [(n-d+1) % small == 0,
                                          (n-d+1) % large == 0]
                    dimension_controls += 2
        print('COEFFICIENT PRIME', p, 'controls', count, flush=True)
    return dict(partition_controls=count, dimension_controls=dimension_controls)


def groebner(max_n):
    import sympy as sp
    rows = []
    for p in (2, 3, 5):
        for n in range(3, max_n+1):
            x = sp.symbols(f'x0:{n}')
            for d in range(3, n+1):
                layers = {}
                for h in range(d):
                    layer = []
                    for removed in combinations(range(n), h):
                        available = [i for i in range(n) if i not in removed]
                        layer.append(sum(sp.prod(x[i] for i in subset)
                                         for subset in combinations(available, d-h)))
                    layers[h] = layer
                for q in range(2, d):
                    dimensions = []
                    for lower in (False, True):
                        generators = sum((layers[h] for h in range(q+1)), []) if lower else layers[q]
                        gb = sp.groebner(generators, *x, modulus=p, order='grevlex')
                        actual = first.monomial_ideal_dimension(gb, n)
                        threshold = first.prime_power(p, d if lower else d-q, strict=True)
                        expected = d-q if (n-d+1) % threshold == 0 else d-q-1
                        assert actual == expected, (p, n, d, q, lower, actual, expected)
                        dimensions.append(actual)
                    rows.append(dict(p=p, n=n, d=d, derivative_order=q,
                                     derivative_locus_dimension=dimensions[0],
                                     multiplicity_locus_dimension=dimensions[1]))
            print('GROEBNER PRIME', p, 'variables', n, flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=22)
    parser.add_argument('--groebner', action='store_true')
    parser.add_argument('--groebner-max-n', type=int, default=6)
    args = parser.parse_args()
    start = time.monotonic()
    report = dict(status='PASS', coefficients=coefficients(args.max_n))
    if args.groebner:
        report['groebner'] = groebner(args.groebner_max_n)
    report['seconds'] = time.monotonic()-start
    report['sources'] = [dict(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                         for path in (Path(__file__), Path(first.__file__))]
    report['scope'] = 'Exact finite controls, not a replacement for the all-size proof.'
    (HERE/'ELEMENTARY_HIGHER_ORDER_CHECKS.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS', report['coefficients'], 'Groebner dimensions',
          len(report.get('groebner', []))*2, 'seconds', report['seconds'], flush=True)


if __name__ == '__main__':
    main()
