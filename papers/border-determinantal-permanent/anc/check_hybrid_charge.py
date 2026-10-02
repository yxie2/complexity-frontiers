"""Exact controls for the shared-auxiliary determinant polar count.

Checks a projective-bundle coefficient identity, shared-gate adjoints,
and full local incidence Jacobians. It does not prove the general theorem.
"""
from pathlib import Path
from math import comb, log, e
from functools import lru_cache
import random, json, hashlib, time
import sympy as sp

ROOT = Path(__file__).resolve().parent
P = 1009


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def B(m, k):
    return sum(choose(m, a)*choose(m-1, k-1-a)*choose(k-2, a-1)
               for a in range(1, k))


def C(m, q, k):
    if not q:
        return B(m, k)
    return 2**q*sum(comb(q+j-1, j)*B(m, k-j) for j in range(k-1))


def mul(a, b):
    out = {}
    for u, v in a.items():
        for x, y in b.items():
            mon = tuple(ui+xi for ui, xi in zip(u, x))
            out[mon] = out.get(mon, 0)+v*y
    return out


def add(a, b):
    out = a.copy()
    for mon, value in b.items():
        out[mon] = out.get(mon, 0)+value
    return out


def power(a, n):
    out = {(0, 0, 0): 1}
    for _ in range(n):
        out = mul(out, a)
    return out


@lru_cache(None)
def bundle_h(q, degree):
    # Complete homogeneous classes, computed by adding line-bundle roots.
    roots = [{(0, 1, 0): 1, (0, 0, 1): 1}]+[{(1, 0, 0): 1}]*q
    values = [{(0, 0, 0): 1}]+[{} for _ in range(degree)]
    for root in roots:
        for i in range(1, degree+1):
            values[i] = add(values[i], mul(root, values[i-1]))
    return values[degree]


def coefficient_checks():
    H = {(1, 0, 0): 1}; U = {(0, 1, 0): 1}; V = {(0, 0, 1): 1}
    cases = 0; controls = 0; inequalities = 0
    for m in range(1, 11):
        base = mul(H, mul(power(add(H, U), m), power(add(H, V), m-1)))
        for q in range(7):
            for k in range(3, 11):
                integral = 2**q*mul(base, bundle_h(q, k-2)).get((k, m-1, m-1), 0)
                assert integral == C(m, q, k), (m, q, k, integral)
                cases += 1
                if m == 1 and q:
                    assert integral == 2**q*comb(q+k-3, k-2)
                    controls += 1
                for rho in [0.1, 0.25, 0.5, 0.75]:
                    bound = 2**(q-1)*rho**(-(k-1))*(1+2*rho)**(2*m-1)*(1-rho)**(-q)
                    assert integral <= bound*(1+1e-12)
                    inequalities += 1
    # Independently reduce the monic projective-bundle relation at exact roots.
    K = sp.Symbol('K'); rng = random.Random(26091617); relations = 0
    for q in range(7):
        for a in range(9):
            h, u, v = [rng.randrange(1, 8) for _ in range(3)]
            relation = sp.Poly((K-u-v)*(K-h)**q, K)
            remainder = sp.rem(sp.Poly(K**(q+a), K), relation)
            predicted = sum(value*h**mon[0]*u**mon[1]*v**mon[2]
                            for mon, value in bundle_h(q, a).items())
            assert remainder.nth(q) == predicted
            relations += 1
    return {'coefficient_identities': cases, 'm1_endpoint_controls': controls,
            'generating_function_bounds': inequalities, 'monic_relation_checks': relations}


def dot(a, b):
    return sum(x*y for x, y in zip(a, b)) % P


def affine(coef, vals):
    return (coef[0]+dot(coef[1:], vals)) % P


def rank(matrix):
    a = [[int(x) % P for x in row] for row in matrix]
    r = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][col], -1, P)
        a[r] = [v*inv % P for v in a[r]]
        for i in range(r+1, len(a)):
            c = a[i][col]
            if c:
                a[i] = [(x-c*y) % P for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def shared_adjoint_checks():
    rng = random.Random(26091618); cases = 0; squared = 0; corrupted = 0
    for trial in range(300):
        k = rng.randrange(3, 8); q = rng.randrange(1, 12); m = rng.randrange(2, 6)
        vals = [rng.randrange(P) for _ in range(k)]
        grads = [[int(i == j) for j in range(k)] for i in range(k)]
        local = []
        for j in range(q):
            aa = [rng.randrange(P) for _ in range(1+k+j)]
            bb = aa[:] if (trial+j) % 4 == 0 else [rng.randrange(P) for _ in aa]
            squared += int(aa == bb)
            av, bv = affine(aa, vals), affine(bb, vals)
            derivative = [(av*b+bv*a) % P for a, b in zip(aa[1:], bb[1:])]
            gradient = [sum(derivative[y]*grads[y][i] for y in range(k+j)) % P for i in range(k)]
            vals.append(av*bv % P); grads.append(gradient); local.append(derivative)
        while True:
            block = sp.Matrix([[rng.randrange(P) for _ in range(m-1)] for _ in range(m-1)])
            if int(block.det()) % P:
                break
        inv = block.inv_mod(P); cv = sp.Matrix([rng.randrange(P) for _ in range(m-1)])
        rv = sp.Matrix([[rng.randrange(P) for _ in range(m-1)]])
        sv = int((rv*inv*cv)[0]) % P
        mat = block.row_join(cv).col_join(rv.row_join(sp.Matrix([[sv]])))
        u = [int(x) % P for x in -rv*inv]+[1]
        v = [int(x) % P for x in -inv*cv]+[1]
        assert int(mat.det()) % P == 0
        adj = mat.adjugate(); minor = int(block.det()) % P
        assert all((int(adj[i, j])-minor*v[i]*u[j]) % P == 0 for i in range(m) for j in range(m))
        coefficients = [[[rng.randrange(P) for _ in range(k+q)] for _ in range(m)] for _ in range(m)]
        # Constants can always be chosen so A at the selected point is mat.
        ay = [sum(u[i]*coefficients[i][j][y]*v[j] for i in range(m) for j in range(m)) % P for y in range(k+q)]
        multipliers = ay[k:]
        for j in range(q-1, -1, -1):
            for h in range(j):
                multipliers[h] = (multipliers[h]+multipliers[j]*local[j][k+h]) % P
        reverse = [(ay[i]+sum(multipliers[j]*local[j][i] for j in range(q))) % P for i in range(k)]
        forward = [sum(int(adj[j, i])*sum(coefficients[i][j][y]*grads[y][x] for y in range(k+q))
                       for i in range(m) for j in range(m)) % P for x in range(k)]
        assert forward == [minor*x % P for x in reverse]
        wrong = [(ay[i]+sum(ay[k+j]*local[j][i] for j in range(q))) % P for i in range(k)]
        if q > 1 and wrong != reverse:
            corrupted += 1
        cases += 1
    assert corrupted > 240
    return {'random_shared_dags': cases, 'squaring_gates': squared,
            'omitted_reuse_corruptions_detected': corrupted, 'prime': P}


def local_incidence_checks():
    rng = random.Random(26091619); results = []
    for k, degree in [(3, 3), (4, 3), (3, 4), (4, 4), (3, 5), (4, 5), (3, 8)]:
        xs = list(sp.symbols(f'x0:{k}')); zs = []; Fs = []; zexprs = []; outputs = []
        for x in xs:
            powers = {1: x}; actual = {1: x}
            def make_power(a):
                if a in powers:
                    return powers[a]
                left = a//2; right = a-left
                al, ar = make_power(left), make_power(right)
                z = sp.Symbol(f'z{len(zs)}')
                zs.append(z); Fs.append(z-al*ar); zexprs.append(x**a); powers[a] = z
                return z
            outputs.append(make_power(degree))
        q = len(zs); f = sum(x**degree for x in xs)
        roots = {}
        for a in range(1, P):
            roots.setdefault(pow(a, degree, P), a)
        while True:
            point = [rng.randrange(1, P) for _ in range(k-1)]
            target = -sum(pow(a, degree, P) for a in point) % P
            if target in roots:
                point.append(roots[target]); break
        gradient = [degree*pow(a, degree-1, P) % P for a in point]
        hdiag = [degree*(degree-1)*pow(a, degree-2, P) % P for a in point]
        ell = [0]*(k-1)+[pow(point[-1], -1, P)]
        while True:
            dirs = []
            for _ in range(k-2):
                vec = [rng.randrange(P) for _ in range(k-1)]
                vec.append(-dot(vec, gradient[:-1])*pow(gradient[-1], -1, P) % P)
                dirs.append(vec)
            target_jac = [gradient, ell]+[[(d*h) % P for d, h in zip(direction, hdiag)] for direction in dirs]
            if rank(target_jac) == k:
                break
        u, v = sp.symbols('u v'); lambdas = list(sp.symbols(f'lam0:{q}'))
        A = sp.Matrix([[1, 1], [xs[0], sum(outputs)+xs[0]]])
        uv, vv = sp.Matrix([[u, 1]]), sp.Matrix([v, 1])
        variables = xs+zs+[u, v]+lambdas
        a = {y: (uv*A.diff(y)*vv)[0] for y in xs+zs}
        adjoint = [a[z]-sum(lam*sp.diff(F, z) for lam, F in zip(lambdas, Fs)) for z in zs]
        brackets = [a[x]-sum(lam*sp.diff(F, x) for lam, F in zip(lambdas, Fs)) for x in xs]
        equations = Fs+list(uv*A)+[(A*vv)[0]]+adjoint+[sum(di*bi for di, bi in zip(direction, brackets)) for direction in dirs]+[sum(c*x for c, x in zip(ell, xs))-1]
        assert len(equations) == len(variables) == k+2*q+2
        values = dict(zip(xs, point))
        values.update({z: int(expr.subs(values)) % P for z, expr in zip(zs, zexprs)})
        values.update({u: -point[0] % P, v: P-1})
        for j in range(q-1, -1, -1):
            constant = adjoint[j].subs({**values, lambdas[j]: 0})
            values[lambdas[j]] = int(constant) % P
        assert all(int(eq.subs(values)) % P == 0 for eq in equations)
        jacobian = [[int(sp.diff(eq, var).subs(values)) % P for var in variables] for eq in equations]
        rk = rank(jacobian)
        assert rk == len(variables)
        delta = degree*(degree-1)**(k-2)
        assert delta <= C(2, q, k)
        results.append({'k': k, 'degree': degree, 'q': q, 'm': 2,
                        'point': point, 'lifted_jacobian_rank': rk, 'variables': len(variables),
                        'target_polar_count': delta, 'hybrid_count': C(2, q, k)})
    return results


def main():
    start = time.monotonic()
    result = {'status': 'passed', 'coefficient_checks': coefficient_checks(),
              'shared_adjoints': shared_adjoint_checks(),
              'local_incidence_checks': local_incidence_checks(),
              'scope': 'Finite identities and local controls, not a proof of the asymptotic theorem or a novelty check.',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    result['seconds'] = time.monotonic()-start
    (ROOT/'CHECK_HYBRID_CHARGE.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
