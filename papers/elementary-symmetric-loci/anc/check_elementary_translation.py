"""Check exact translation-stabilizer ideals and diagonal normal forms."""
from itertools import combinations
from math import comb
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def valuation_power(n, p):
    q = 1
    while n % p == 0:
        n //= p
        q *= p
    return q


def main():
    import sympy as sp
    start = time.monotonic()
    ideals = []
    for p in (2, 3, 5, 7):
        for n in range(2, 8):
            v = sp.symbols(f'v0:{n}')
            for d in range(2, n+1):
                generators = []
                # Coefficients of each x_I in e_d(x+v)-e_d(x), computed
                # directly as elementary polynomials in the complement.
                for h in range(d):
                    for indices in combinations(range(n), h):
                        outside = [i for i in range(n) if i not in indices]
                        generators.append(sum(sp.prod(v[i] for i in subset)
                                              for subset in combinations(outside, d-h)))
                actual = sp.groebner(generators, *v, modulus=p, order='lex')
                q = valuation_power(n-d+1, p)
                predicted = [v[i]-v[-1] for i in range(n-1)]
                if q <= d:
                    predicted.append(v[-1]**q)
                expected = sp.groebner(predicted, *v, modulus=p, order='lex')
                assert actual.polys == expected.polys, (p, n, d, actual, expected)
                ideals.append(dict(p=p, n=n, d=d, valuation_power=q,
                                  finite_length=q if q <= d else None))
        print('EXACT IDEAL PRIME', p, 'completed', flush=True)
    normal_forms = []
    cases = [(2, 3, 2), (2, 5, 2), (2, 7, 4), (2, 8, 5),
             (2, 9, 6), (3, 5, 3), (3, 11, 3), (5, 9, 5)]
    for p, n, d in cases:
        z = sp.symbols(f'z0:{n-1}')
        t = sp.Symbol('t')
        x = [variable+t for variable in z]+[t]
        direct = sum(sp.prod(x[i] for i in subset) for subset in combinations(range(n), d))
        q = valuation_power(n-d+1, p)
        u = (n-d+1)//q
        predicted = 0
        for b in range(d//q+1):
            degree = d-b*q
            elementary = sum(sp.prod(z[i] for i in subset)
                             for subset in combinations(range(n-1), degree))
            predicted += comb(u+b-1, b)*t**(b*q)*elementary
        assert sp.Poly(direct-predicted, *z, t, modulus=p).is_zero
        normal_forms.append(dict(p=p, n=n, d=d, valuation_power=q))
    binomial_controls = 0
    for p in (2, 3, 5, 7, 11):
        for n in range(2, 151):
            for d in range(2, n+1):
                q = valuation_power(n-d+1, p)
                first_nonzero = next((h for h in range(1, d+1)
                                      if comb(n-d+h, h) % p), None)
                assert first_nonzero == (q if q <= d else None)
                binomial_controls += 1
    report = dict(status='PASS', exact_ideal_checks=ideals,
                  direct_normal_form_checks=normal_forms,
                  binomial_threshold_controls=binomial_controls,
                  seconds=time.monotonic()-start,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Exact finite ideal equality and polynomial identity controls; the general scheme proof is separate.')
    (HERE/'ELEMENTARY_TRANSLATION_CHECKS.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS', len(ideals), 'exact ideals;', len(normal_forms),
          'normal forms;', binomial_controls, 'binomial thresholds;',
          report['seconds'], 'seconds', flush=True)


if __name__ == '__main__':
    main()
