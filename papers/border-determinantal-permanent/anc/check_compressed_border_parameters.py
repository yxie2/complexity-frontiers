"""Integer-only checks of the compressed selector bound, including floor changes."""
from functools import lru_cache
from math import comb
from pathlib import Path
import hashlib
import json
import random
import time

HERE = Path(__file__).resolve().parent
A, B = 8**8, 7**7


@lru_cache(None)
def profile(a):
    t, d = 8*a, 2*a
    return 2*sum(comb(t, j) for j in range(1, a))+comb(t, a)-t


def choose(n):
    a, left, right = 0, 1, n
    while left*A <= right*B:
        a += 1
        left *= A
        right *= B
    return a


def check(n, a=None):
    a = choose(n) if a is None else a
    assert A**a <= n*B**a and A**(a+1) > n*B**(a+1)
    t, d = 8*a, 2*a
    b = n//(2*t)
    r = b*t
    s = n-r+d
    cost = profile(a)
    K = b*(s*(t-d+2)-cost)
    assert a >= 2 and b >= 1 and 3 <= d <= min(t, s) and r+s-d == n
    assert 3*cost*B**a <= 4*A**a <= 4*n*B**a
    assert 4*r*s >= n*n-4*t*t
    assert 48*a*K >= 9*a*n*n-n*n-2304*a**3-768*a*a
    assert 48*(48*a*a+16*a+1)*(2*a-1) <= n*n
    assert 8*(K-1)*(d-1) >= n*n*(3*a-2)
    assert 3 <= K <= r*s and 2**d < n
    return dict(n=n, a=a, t=t, d=d, b=b, r=r, s=s, moment_cost=cost, K=K,
                four_e_times_bridge_bound=(K-1)*(d-1))


def main():
    started = time.monotonic()
    count = 0
    a = choose(512)
    next_threshold = (A**(a+1)+B**(a+1)-1)//B**(a+1)
    for n in range(512, 1_000_001):
        if n >= next_threshold:
            a += 1
            next_threshold = (A**(a+1)+B**(a+1)-1)//B**(a+1)
        check(n, a)
        count += 1
    samples = set()
    for a in range(2, 201):
        threshold = (A**a+B**a-1)//B**a
        for offset in [-2, -1, 0, 1, 2, 16*a-1, 16*a]:
            if threshold+offset >= 512:
                samples.add(threshold+offset)
        assert 4608*a**3 <= 20**(2*a)
    rng = random.Random(0x78c3b6aa)
    for _ in range(500):
        bits = rng.randrange(10, 1001)
        samples.add((1 << bits)+rng.getrandbits(bits))
    for n in sorted(samples):
        check(n)
        count += 1
    controls = [check(n) for n in [512, 1024, 65536, 10**6, 1 << 100]]
    result = dict(status='PASS', integer_parameter_checks=count, exhaustive_interval=[512, 1_000_000],
                  extra_samples=len(samples), controls=controls, seconds=time.monotonic()-started,
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='All parameter and inequality checks use integers; the uniform estimate and its logarithmic conversion are proved in the accompanying manuscript.')
    (HERE/'COMPRESSED_BORDER_PARAMETER_CHECKS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['status', 'integer_parameter_checks', 'extra_samples', 'seconds']}), flush=True)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions must be enabled.')
    main()
