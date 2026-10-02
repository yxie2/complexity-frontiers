"""Exact floor/boundary controls for the new uniform parameter proof."""
from pathlib import Path
import hashlib
import json
import random
import time

ROOT = Path(__file__).resolve().parent


def check(n):
    t = n.bit_length()-1
    d = t//2
    b = n//(2*t)
    r = b*t
    s = n-r+d
    K = b*(s*(t-d+2)-(2**t-1))
    assert t >= 6 and 3 <= d <= min(t, s) and b >= 1
    assert r+s-d == n and 3 <= K <= r*s
    assert 2*r <= n and n-2*t < 2*r
    assert 4*r*s >= n*n-4*t*t
    assert 8*K >= n*n-4*t*t-16*t
    assert 8*(t*t+4*t+2)*(t-3) <= 2*n*n
    assert 16*(K-1)*(d-1) >= n*n*(t-4)
    return t, d, b, r, s, K


def main():
    start = time.monotonic()
    count = 0
    for n in range(64, 1_000_001):
        check(n)
        count += 1
    boundary = set()
    for exponent in range(6, 1001):
        for offset in [-2, -1, 0, 1, 2, 2*exponent-1, 2*exponent]:
            n = (1 << exponent)+offset
            if n >= 64:
                boundary.add(n)
    rng = random.Random(0x135283a)
    for _ in range(2500):
        bits = rng.randrange(6, 2001)
        boundary.add((1 << bits) + rng.getrandbits(bits))
    for n in sorted(boundary):
        check(n)
        count += 1
    for t in range(6, 2001):
        assert 8*t**3 <= 1 << (2*t)
        assert (t+1)**3 < 4*t**3
        assert t*t+4*t+2 <= 2*t*t
    controls = []
    for n in [64, 65, 127, 128, 65536, 10**6, 1 << 100]:
        values = check(n)
        controls.append(dict(zip(['n', 't', 'd', 'b', 'r', 's', 'K'], [n, *values])) |
                        {'four_e_times_bridge_bound': (values[-1]-1)*(values[1]-1)})
    out = {'status': 'passed', 'checked_n': count,
           'exhaustive_interval': [64, 1_000_000],
           'additional_distinct_large_samples': len(boundary),
           'controls': controls, 'seconds': time.monotonic()-start,
           'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'scope': 'Exact finite floor controls. The separate written induction proves the uniform bound.'}
    (ROOT / 'IMPROVED_BORDER_PARAMETER_CHECKS.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: out[k] for k in ['status', 'checked_n', 'seconds']}))


if __name__ == '__main__':
    main()
