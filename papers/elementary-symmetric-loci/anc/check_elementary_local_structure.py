"""Independent polynomial, order, and tangent-rank controls for local claims."""
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def derivative_terms(n, d, indices):
    outside = [i for i in range(n) if i not in indices]
    return Counter({subset:1 for subset in combinations(outside, d-len(indices))})


def difference_identities():
    count = 0
    for n in range(2, 10):
        for d in range(2, n+1):
            for q in range(1, d):
                r = d-q
                fat = list(range(r-1, n))
                for i,j in combinations(fat, 2):
                    rest = [a for a in fat if a not in (i,j)][:q-1]
                    left = derivative_terms(n, d, rest+[i])
                    left.subtract(derivative_terms(n, d, rest+[j]))
                    right = Counter()
                    for monomial, coefficient in derivative_terms(n, d, rest+[i,j]).items():
                        right[tuple(sorted(monomial+(j,)))] += coefficient
                        right[tuple(sorted(monomial+(i,)))] -= coefficient
                    assert {m:c for m,c in left.items() if c} == {m:c for m,c in right.items() if c}
                    count += 1
    return count


def power(n, p):
    q = 1
    while n % p == 0:
        q *= p
        n //= p
    return q


def restricted_order(n, d, q, p, lower):
    r = d-q
    L = n-d+1
    best = None
    orders = range(q+1) if lower else (q,)
    for h in orders:
        for a in range(min(h, r-1)+1):
            fat_left = L+q-h+a
            for j in range(q-h+a+1, d-h+1):
                coefficient = comb(fat_left, j) if j <= fat_left else 0
                if coefficient % p:
                    best = j if best is None else min(best, j)
    return best


def order_checks():
    count = 0
    nonreduced = 0
    for p in (2, 3, 5, 7, 11):
        for n in range(2, 41):
            for d in range(2, min(12,n)+1):
                Q = power(n-d+1, p)
                for q in range(1, d):
                    for lower in (False, True):
                        actual = restricted_order(n, d, q, p, lower)
                        threshold = d if lower else d-q
                        expected = Q if Q <= threshold else None
                        assert actual == expected, (p,n,d,q,lower,actual,expected)
                        count += 1
                        nonreduced += actual is not None and actual > 1
        print('LOCAL ORDERS', p, 'controls', count, flush=True)
    return dict(controls=count, nonreduced_controls=nonreduced)


def rank(matrix, p):
    if not matrix:
        return 0
    pivots = {}
    for source in matrix:
        row = [a % p for a in source]
        for j in range(len(row)):
            if not row[j]:
                continue
            if j in pivots:
                c = row[j]
                row = [(a-c*b) % p for a,b in zip(row,pivots[j])]
            else:
                inverse = pow(row[j], -1, p)
                pivots[j] = [a*inverse % p for a in row]
                break
    return len(pivots)


def tangent_checks():
    count = 0
    for n in range(2, 11):
        for d in range(2, n+1):
            for q in range(1, d):
                r = d-q
                support = set(range(r-1))
                matrix = []
                for indices in combinations(range(n), q):
                    row = []
                    for j in range(n):
                        if j in indices:
                            row.append(0)
                        else:
                            survivors = len(support-set(indices)-{j})
                            row.append(comb(survivors, r-1) if survivors >= r-1 else 0)
                    matrix.append(row)
                for p in (2, 3, 5, 7):
                    actual = rank(matrix, p)
                    fat = n-r+1
                    expected = fat-1 if (n-d+1) % p == 0 else fat
                    assert actual == expected, (p,n,d,q,actual,expected)
                    count += 1
    return count


def main():
    start = time.monotonic()
    report = dict(status='PASS', integer_polynomial_identities=difference_identities(),
                  local_orders=order_checks(), tangent_ranks=tangent_checks(),
                  seconds=time.monotonic()-start,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Finite direct polynomial identities, binomial restrictions and full Jacobian ranks. The all-size localization argument is the proof, not these checks.')
    (HERE/'ELEMENTARY_LOCAL_STRUCTURE_CHECKS.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
