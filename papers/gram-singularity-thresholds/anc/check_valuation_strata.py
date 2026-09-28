"""Exact checks of content strata and hollow pivot fibers by kernel enumeration.

Run with Python 3.11 or later; no other files or packages are required.
Both Z/p^L and F_p[t]/(t^L) are implemented directly. Image lengths are
computed from literal kernel cardinalities, without Smith elimination.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from math import comb
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


class Ring:
    def __init__(self, kind, p, length):
        self.kind, self.p, self.length = kind, p, length
        self.size = p ** length
        self.digits = [tuple((x // p ** i) % p for i in range(length))
                       for x in range(self.size)]
        self.add = [[self.operation(x, y, False) for y in range(self.size)]
                    for x in range(self.size)]
        self.mul = [[self.operation(x, y, True) for y in range(self.size)]
                    for x in range(self.size)]
        self.neg = [next(y for y in range(self.size) if self.add[x][y] == 0)
                    for x in range(self.size)]
        self.val = [next((i for i, c in enumerate(d) if c), length)
                    for d in self.digits]
        self.units = [x for x in range(self.size) if self.val[x] == 0]
        self.inv = {x: next(y for y in self.units if self.mul[x][y] == 1)
                    for x in self.units}
        self.product_counts = Counter(self.mul[x][y]
                                      for x in range(self.size)
                                      for y in range(self.size))
        self.vectors = {}
        self.row_kernels = {}
        self.image_lengths = {}

    def operation(self, x, y, multiply):
        if self.kind == 'integer':
            return (x * y if multiply else x + y) % self.size
        a, b = self.digits[x], self.digits[y]
        if multiply:
            digits = [sum(a[j] * b[i - j] for j in range(i + 1)) % self.p
                      for i in range(self.length)]
        else:
            digits = [(u + v) % self.p for u, v in zip(a, b)]
        return sum(c * self.p ** i for i, c in enumerate(digits))

    def row_kernel(self, row):
        row = tuple(row)
        if row not in self.row_kernels:
            n = len(row)
            vectors = self.vectors.setdefault(n, tuple(product(range(self.size), repeat=n)))
            mask = bytearray((len(vectors) + 7) // 8)
            for i, vector in enumerate(vectors):
                value = 0
                for a, b in zip(row, vector):
                    value = self.add[value][self.mul[a][b]]
                if value == 0:
                    mask[i // 8] |= 1 << (i % 8)
            self.row_kernels[row] = int.from_bytes(mask, 'little')
        return self.row_kernels[row]

    def rho(self, matrix):
        key = tuple(map(tuple, matrix))
        if key not in self.image_lengths:
            if not key:
                self.image_lengths[key] = 0
            else:
                mask = self.row_kernel(key[0])
                for row in key[1:]:
                    mask &= self.row_kernel(row)
                kernel = mask.bit_count()
                exponent, power = 0, 1
                while power < kernel:
                    exponent += 1
                    power *= self.p
                assert power == kernel
                self.image_lengths[key] = len(key) * self.length - exponent
        return self.image_lengths[key]


def matrices(n, size, hollow):
    positions = list(combinations(range(n), 2)) if hollow else [
        (i, j) for i in range(n) for j in range(i, n)]
    for entries in product(range(size), repeat=len(positions)):
        matrix = [[0] * n for _ in range(n)]
        for (i, j), value in zip(positions, entries):
            matrix[i][j] = matrix[j][i] = value
        yield matrix


def residual(ring, matrix):
    inverse = ring.inv[matrix[0][1]]
    out = []
    for i in range(2, len(matrix)):
        row = []
        for j in range(2, len(matrix)):
            cross = ring.add[ring.mul[matrix[i][0]][matrix[1][j]]][
                ring.mul[matrix[i][1]][matrix[0][j]]]
            row.append(ring.add[matrix[i][j]][ring.neg[ring.mul[inverse][cross]]])
        out.append(row)
    return out


@lru_cache(None)
def inspect(kind, p, length, h):
    ring = Ring(kind, p, length)
    for value in range(ring.size):
        w = ring.val[value]
        expected = ((w + 1) * (p - 1) * p ** (length - 1) if value else
                    ring.size + length * (p - 1) * p ** (length - 1))
        assert ring.product_counts[value] == expected
    histogram, primitive, fixed = Counter(), Counter(), Counter()
    strata = defaultdict(Counter)
    fibers = Counter()
    for matrix in matrices(h, ring.size, True):
        rho = ring.rho(matrix)
        common = min(ring.val[x] for row in matrix for x in row)
        histogram[rho] += 1
        strata[common][rho] += 1
        if common == 0:
            primitive[rho] += 1
        a = matrix[0][1]
        if a in ring.inv:
            s = residual(ring, matrix)
            assert rho == 2 * length + ring.rho(s)
            fixed[rho] += 1
            fibers[(a, tuple(map(tuple, s)))] += 1
    assert sum(histogram.values()) == ring.size ** comb(h, 2)
    assert strata[length] == Counter({0: 1})
    for common in range(1, length):
        smaller = inspect(kind, p, length - common, h)
        assert strata[common] == smaller['primitive_histogram']
    assert strata[0] == primitive

    predicted = Counter()
    symmetric = Counter()
    fiber_checks = 0
    k = h - 2
    inverse_two = ring.inv[ring.add[1][1]]
    for s in matrices(k, ring.size, False):
        rho_s = ring.rho(s)
        symmetric[rho_s] += 1
        for a in ring.units:
            count = 1
            for j in range(k):
                target = ring.neg[ring.mul[ring.mul[a][s[j][j]]][inverse_two]]
                count *= ring.product_counts[target]
            assert fibers[(a, tuple(map(tuple, s)))] == count
            predicted[2 * length + rho_s] += count
            fiber_checks += 1
    assert fixed == predicted
    for rho, count in primitive.items():
        assert count <= comb(h, 2) * fixed[rho]
        bound = (comb(h, 2) * (length + 1) ** k *
                 ring.size ** (h - 1) * symmetric[rho - 2 * length])
        assert count <= bound
    return dict(ring=('Z/%d' % ring.size if kind == 'integer' else
                      'F_%d[t]/(t^%d)' % (p, length)), h=h, p=p, length=length,
                matrices=sum(histogram.values()), primitive_matrices=sum(primitive.values()),
                image_length_histogram=dict(sorted(histogram.items())),
                primitive_histogram=dict(sorted(primitive.items())),
                fixed_pivot_histogram=dict(sorted(fixed.items())),
                common_valuation_histograms={v: dict(sorted(counts.items()))
                                             for v, counts in sorted(strata.items())},
                exact_pivot_fibers_checked=fiber_checks,
                scalar_product_counts_exact=True, content_strata_exact=True,
                pivot_image_lengths_exact=True, pivot_fiber_counts_exact=True,
                coefficientwise_mass_bound=True)


def main():
    start = time.monotonic()
    records = []
    for kind in ['integer', 'polynomial']:
        for h, length in [(2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (4, 1)]:
            record = inspect(kind, 3, length, h)
            records.append(record)
            print(json.dumps({k: record[k] for k in ['ring', 'h', 'matrices', 'fixed_pivot_histogram']}), flush=True)
    ring = Ring('integer', 3, 3)
    example = [[0, 3, 3], [3, 0, 9], [3, 9, 0]]
    assert ring.rho(example) == 5
    assert inspect('integer', 3, 2, 3)['fixed_pivot_histogram'] == {4: 126, 5: 144, 6: 216}
    result = dict(status='PASS', records=records,
                  total_hollow_matrices=sum(r['matrices'] for r in records),
                  exact_pivot_fibers_checked=sum(r['exact_pivot_fibers_checked'] for r in records),
                  mixed_valuation_example={'ring': 'Z/27', 'matrix': example, 'rho': 5, 'kernel_size': 81},
                  seconds=time.monotonic() - start,
                  producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Finite exact kernel, content-stratum, scalar-product, and pivot-fiber counts.')
    (HERE / 'valuation_strata_checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['status', 'total_hollow_matrices', 'exact_pivot_fibers_checked', 'seconds']}))


if __name__ == '__main__':
    main()
