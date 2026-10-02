"""Exact symbolic controls for the collected column coefficients and their rank."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from math import comb, factorial, prod
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def subsets(mask, size):
    return [sum(1 << i for i in item) for item in combinations([i for i in range(mask.bit_length()) if mask >> i & 1], size)]


@lru_cache(None)
def partitions(mask):
    if not mask:
        return ((),)
    bit = mask & -mask
    rest = mask ^ bit
    out = []
    sub = rest
    while True:
        block = bit | sub
        out.extend((block,)+tail for tail in partitions(rest ^ sub))
        if not sub:
            break
        sub = (sub-1) & rest
    return tuple(out)


def mobius(partition):
    return prod((-1)**(block.bit_count()-1)*factorial(block.bit_count()-1) for block in partition)


def direct_q(t, d, i):
    result = Counter()
    for rowset in subsets(((1 << t)-1) ^ (1 << i), d-1):
        for partition in partitions(rowset):
            weight = mobius(partition)
            for choice in range(1 << len(partition)):
                u = 0
                moments = []
                for j, block in enumerate(partition):
                    if choice >> j & 1:
                        u |= block
                    else:
                        moments.append(block)
                result[u, tuple(sorted(moments))] += weight*(-1)**choice.bit_count()
    return {key: value for key, value in result.items() if value}


def collected_q(t, d, i):
    result = Counter()
    full = (1 << t)-1
    for j in range(d):
        for u in subsets(full ^ (1 << i), j):
            for rowset in subsets(full ^ u ^ (1 << i), d-1-j):
                for partition in partitions(rowset):
                    result[u, tuple(sorted(partition))] += (-1)**j*factorial(j)*mobius(partition)
    return {key: value for key, value in result.items() if value}


def rank(rows, prime):
    pivots = {}
    for row in rows:
        values = row[:]
        for i in range(len(values)):
            value = values[i]
            if not value:
                continue
            if i not in pivots:
                inverse = pow(value, -1, prime)
                pivots[i] = [c*inverse % prime for c in values]
                break
            values = [(a-value*b) % prime for a, b in zip(values, pivots[i])]
    return len(pivots)


def coefficient_count(t, d):
    return sum(comb(t, min(k, d-k)) for k in range(1, d))


def main():
    started = time.monotonic()
    symbolic = 0
    terms = 0
    rank_checks = 0
    for t in range(3, 9):
        for d in range(3, min(t, 7)+1):
            for i in range(t):
                left, right = direct_q(t, d, i), collected_q(t, d, i)
                assert left == right, (t, d, i)
                terms += len(left)
                symbolic += 1
            for k in range(1, d):
                small, large = min(k, d-k), max(k, d-k)
                source = subsets((1 << t)-1, small)
                target = subsets((1 << t)-1, large)
                rows = [[int(a & b == 0) for a in source] for b in target]
                for prime in [11, 13, 101]:
                    assert rank(rows, prime) == len(source), (t, d, k, prime)
                    rank_checks += 1
    profiles = []
    for t in range(3, 101):
        for d in range(3, t+1):
            h = d//2
            closed = 2*sum(comb(t, j) for j in range(1, h+1))-t if d % 2 else 2*sum(comb(t, j) for j in range(1, h))+comb(t, h)-t
            assert coefficient_count(t, d)-t == closed
    for t, d in [(8, 4), (16, 4), (24, 6), (32, 8), (64, 16), (100, 20)]:
        profiles.append(dict(rows=t, degree=d, former=2**t-1,
                             exact_formal=coefficient_count(t, d),
                             critical=coefficient_count(t, d)-t))
    # Verify the rowwise constant-block identity directly at the monomial level.
    constant_checks = 0
    for t, s, d in [(3, 4, 3), (4, 5, 3), (4, 5, 4), (5, 6, 4), (5, 6, 5)]:
        from itertools import permutations
        for omitted_row in range(t):
            lhs = Counter()
            rhs = Counter()
            for rows in combinations([i for i in range(t) if i != omitted_row], d-1):
                for cols in permutations(range(s), d-1):
                    monomial = tuple(sorted(zip(rows, cols)))
                    rhs[monomial] += s-d+1
                    for omitted_column in range(s):
                        if omitted_column not in cols:
                            lhs[monomial] += 1
            assert lhs == rhs
            constant_checks += 1
    sources = [Path(__file__)]
    result = dict(status='PASS', symbolic_equations=symbolic, exact_symbolic_terms=terms,
                  independent_incidence_rank_checks=rank_checks, constant_block_checks=constant_checks,
                  profiles=profiles, seconds=time.monotonic()-started,
                  sources=[dict(path=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
                  scope='Exact integer symbolic expansion, independent finite-field incidence ranks, and monomial counting controls. The written proof supplies the arbitrary-size theorem.')
    (HERE/'COLUMN_COEFFICIENT_COMPRESSION_CHECKS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['status', 'symbolic_equations', 'exact_symbolic_terms', 'independent_incidence_rank_checks', 'constant_block_checks', 'seconds']}), flush=True)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions must be enabled.')
    main()
