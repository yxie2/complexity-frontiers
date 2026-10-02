"""Finite controls for the generic-level shared rational-state proof."""
from pathlib import Path
from itertools import product
from math import comb
import hashlib
import json
import random
import time
import sympy as sp
from check_hybrid_charge import B, mul, add, power, rank, dot, P
from check_non_skew_tradeoff import exact_count, push

ROOT = Path(__file__).resolve().parent


def shifted_counts():
    H = {(1, 0, 0): 1}; V = {(0, 1, 0): 1}; L = {(0, 0, 1): 1}
    twiceV = {(0, 1, 0): 2}
    count = 0
    for M in range(2, 9):
        for q in range(M+1):
            for k in range(3, 10):
                raw = mul(mul(power(add(H, V), M-q), power(add(H, twiceV), q)),
                          mul(power(add(L, H), M-1), power(add(L, V), k-1)))
                integral = sum(value*push(q, lm-M+1) for (hm, vm, lm), value in raw.items()
                               if hm == k and lm >= M-1 and vm+lm-M+1 == M-1)
                assert integral == exact_count(M, q, k+1)
                if q == 0:
                    assert integral == B(M, k+1)
                else:
                    bound = 2**(q+k-1)*comb(q+k-2, k-1)*(comb(2*M-1, k) if k <= 2*M-1 else 0)
                    assert integral <= bound
                count += 1
    return count


def jets(k, operations, point):
    values = point[:]
    grads = [[int(i == j) for j in range(k)] for i in range(k)]
    hessians = [[[0]*k for _ in range(k)] for _ in range(k)]
    for op, a, b in operations:
        av, bv = values[a], values[b]
        ag, bg = grads[a], grads[b]
        ah, bh = hessians[a], hessians[b]
        if op == '+':
            value = (av+bv) % P
            grad = [(ag[i]+bg[i]) % P for i in range(k)]
            hessian = [[(ah[i][j]+bh[i][j]) % P for j in range(k)] for i in range(k)]
        elif op == '*':
            value = av*bv % P
            grad = [(ag[i]*bv+bg[i]*av) % P for i in range(k)]
            hessian = [[(ah[i][j]*bv+bh[i][j]*av+ag[i]*bg[j]+bg[i]*ag[j]) % P
                        for j in range(k)] for i in range(k)]
        else:
            if not bv:
                raise ZeroDivisionError
            inverse = pow(bv, -1, P)
            value = av*inverse % P
            grad = [(ag[i]-value*bg[i])*inverse % P for i in range(k)]
            hessian = [[(ah[i][j]-value*bh[i][j]-grad[i]*bg[j]-bg[i]*grad[j])*inverse % P
                        for j in range(k)] for i in range(k)]
        values.append(value); grads.append(grad); hessians.append(hessian)
    return values, grads, hessians


def local_incidence(k, operations, point, coefficients, check_corruption=True):
    vals, grads, hessians = jets(k, operations, point)
    s = len(vals)
    gradient = [sum(c*g[i] for c, g in zip(coefficients, grads)) % P for i in range(k)]
    hessian = [[sum(c*h[i][j] for c, h in zip(coefficients, hessians)) % P
                for j in range(k)] for i in range(k)]
    if not gradient[-1]:
        return None
    directions = []
    for i in range(k-1):
        direction = [0]*k
        direction[i] = 1
        direction[-1] = -gradient[i]*pow(gradient[-1], -1, P) % P
        directions.append(direction)
    target_jac = [gradient]+[[sum(v[j]*hessian[j][i] for j in range(k)) % P
                              for i in range(k)] for v in directions]
    if rank(target_jac) != k:
        return None
    xs = list(sp.symbols(f'x0:{k}'))
    ws = list(sp.symbols(f'w0:{s}'))
    multipliers = list(sp.symbols(f'a0:{s}'))
    graph = [w-x for w, x in zip(ws[:k], xs)]
    for j, (op, a, b) in enumerate(operations):
        if op == '+':
            equation = ws[k+j]-ws[a]-ws[b]
        elif op == '/':
            equation = ws[k+j]*ws[b]-ws[a]
        elif a < k:
            equation = ws[k+j]-xs[a]*ws[b]
        elif b < k:
            equation = ws[k+j]-ws[a]*xs[b]
        else:
            equation = ws[k+j]-ws[a]*ws[b]
        graph.append(equation)
    level = dot(coefficients, vals)
    output = sum(c*w for c, w in zip(coefficients, ws))-level
    lagrangian = output+sum(a*f for a, f in zip(multipliers, graph))
    state_adjoint = [sp.diff(lagrangian, w) for w in ws]
    polars = [sum(v[i]*sp.diff(lagrangian, xs[i]) for i in range(k)) for v in directions]
    equations = graph+[output]+state_adjoint+polars
    variables = xs+ws+multipliers
    assert len(equations) == len(variables) == k+2*s
    substitution = dict(zip(xs, point)); substitution.update(dict(zip(ws, vals)))
    pivots = []
    for j in range(s-1, -1, -1):
        pivot = int(sp.diff(state_adjoint[j], multipliers[j]).subs(substitution)) % P
        assert pivot
        constant = int(state_adjoint[j].subs({**substitution, multipliers[j]: 0})) % P
        substitution[multipliers[j]] = -constant*pow(pivot, -1, P) % P
        pivots.append(pivot)
    assert all(int(eq.subs(substitution)) % P == 0 for eq in equations)
    implicit = [int(sp.diff(lagrangian, x).subs(substitution)) % P for x in xs]
    assert implicit == gradient
    jacobian = [[int(sp.diff(eq, variable).subs(substitution)) % P for variable in variables]
                for eq in equations]
    assert rank(jacobian) == len(variables)
    corrupted = False
    if check_corruption:
        wrong = dict(zip(xs, point)); wrong.update(dict(zip(ws, vals)))
        for j in range(s-1, -1, -1):
            constant = int(state_adjoint[j].subs({**wrong, multipliers[j]: 0})) % P
            wrong[multipliers[j]] = -constant % P  # deliberately omit denominator pivot
        corrupted = any(int(eq.subs(wrong)) % P for eq in state_adjoint)
    uses = [0]*s
    for op, a, b in operations:
        uses[a] += 1; uses[b] += 1
    return {'k': k, 'states': s, 'incidence_jacobian_rank': len(variables),
            'division_gates': sum(op == '/' for op, _, _ in operations),
            'nonunit_division_pivots': sum(p != 1 for p in pivots),
            'reused_internal_states': sum(uses[j] > 1 for j in range(k, s)),
            'wrong_unit_pivot_rejected': bool(corrupted), 'level_mod_prime': level}


def random_local_controls():
    rng = random.Random(2609160331)
    cases = []
    for case in range(24):
        k = 3+case % 2
        operations = [('*', i, i) for i in range(k)]
        for j in range(7):
            size = k+len(operations)
            operations.append((['+', '*', '/'][j % 3], rng.randrange(size), rng.randrange(size)))
        while True:
            point = [rng.randrange(1, P) for _ in range(k)]
            coefficients = [rng.randrange(P) for _ in range(k+len(operations))]
            try:
                result = local_incidence(k, operations, point, coefficients)
            except ZeroDivisionError:
                continue
            if result is not None:
                break
        cases.append(result)
    assert sum(c['wrong_unit_pivot_rejected'] for c in cases) >= 20
    return cases


def canceled_pole_controls():
    cases = []
    for k in [3, 4]:
        operations = []
        cubes = []
        for i in range(k):
            square = k+len(operations); operations.append(('*', i, i))
            cube = k+len(operations); operations.append(('*', square, i))
            cubes.append(cube)
        f = cubes[0]
        for cube in cubes[1:]:
            new = k+len(operations); operations.append(('+', f, cube)); f = new
        square_f = k+len(operations); operations.append(('*', f, f))
        operations.append(('/', square_f, f))
        coefficients = [0]*(k+len(operations)); coefficients[-1] = 1
        result = local_incidence(k, operations, list(range(1, k+1)), coefficients)
        assert result is not None and result['level_mod_prime'] != 0
        result['polynomial_output'] = 'f^2/f=f, f=sum x_i^3'
        result['invalid_zero_level'] = 'division denominator is f, hence zero on all f=0'
        cases.append(result)
    return cases


def fermat_level_counts():
    rng = random.Random(16090331)
    cases = []
    for k in [3, 4]:
        for d in [3, 4, 7, 8]:
            q = d-1
            roots = [x for x in range(1, P) if pow(x, q, P) == 1]
            assert len(roots) == q
            while True:
                b = [rng.randrange(1, P) for _ in range(k-1)]
                coefficients = [(1+sum(pow(bi, d, P)*z for bi, z in zip(b, zs))) % P
                                for zs in product(roots, repeat=k-1)]
                if all(coefficients):
                    break
            assert len(coefficients) == q**(k-1)
            cases.append({'k': k, 'degree': d, 'direction_parameters': b,
                          'projective_points': len(coefficients),
                          'affine_points_over_algebraic_closure': d*len(coefficients),
                          'all_nonzero_level_coefficients': True,
                          'scope': 'q-th roots split in the base field; radial d-th roots are counted over its algebraic closure.'})
    return cases


def main():
    start = time.monotonic()
    result = {'status': 'passed', 'prime': P, 'shifted_coefficient_identities': shifted_counts(),
              'random_local_controls': random_local_controls(),
              'canceled_pole_controls': canceled_pole_controls(),
              'fermat_level_counts': fermat_level_counts(),
              'scope': 'Finite controls, not an asymptotic proof or novelty certification.',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'dependencies': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                               for name in ['check_hybrid_charge.py', 'check_non_skew_tradeoff.py']}}
    result['seconds'] = time.monotonic()-start
    (ROOT/'CHECK_RATIONAL_STATE_LEVEL.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ['random_local_controls', 'canceled_pole_controls', 'fermat_level_counts']}, indent=2))
    print(json.dumps({'random_cases': len(result['random_local_controls']),
                      'canceled_pole_cases': len(result['canceled_pole_controls']),
                      'fermat_count_cases': len(result['fermat_level_counts']),
                      'division_pivot_corruptions_rejected': sum(c['wrong_unit_pivot_rejected'] for c in result['random_local_controls'])}))


if __name__ == '__main__':
    main()
