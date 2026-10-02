"""Independent finite controls for the circuit-state projective-bundle count.

No asymptotic or novelty claim is inferred from these computations.
"""
from pathlib import Path
from math import comb, e
import json, hashlib, random, time
import sympy as sp
from check_hybrid_charge import B, mul, add, power, rank, P, dot

ROOT = Path(__file__).resolve().parent


def push(q, a):
    if a < 0:
        return 0
    return int(a == 0) if q == 0 else comb(q+a-1, a)


def exact_count(M, q, k):
    result = 0
    for i in range(M-q+1):
        for b in range(q+1):
            c = k-1-i-b
            if not 0 <= c <= M-1:
                continue
            tail = sum(comb(k-2, j)*push(q, j-c) for j in range(c, k-1))
            result += comb(M-q, i)*comb(q, b)*2**(q-b)*comb(M-1, c)*tail
    return result


def coefficient_checks():
    H = {(1, 0, 0): 1}; V = {(0, 1, 0): 1}; L = {(0, 0, 1): 1}
    twoV = {(0, 1, 0): 2}; identities = 0; bounds = 0; monotonic = 0
    for M in range(2, 10):
        for k in range(3, 11):
            previous = -1
            for q in range(M+1):
                raw = mul(H, mul(mul(power(add(H, V), M-q), power(add(H, twoV), q)),
                                 mul(power(add(L, H), M-1), power(add(L, V), k-2))))
                integral = sum(value*push(q, lm-M+1) for (hm, vm, lm), value in raw.items()
                               if hm == k and lm >= M-1 and vm+lm-M+1 == M-1)
                assert integral == exact_count(M, q, k), (M, q, k)
                if not q:
                    assert integral == B(M, k)
                else:
                    upper = 2**(q+k-2)*comb(q+k-3, k-2)*(comb(2*M-1, k-1) if k-1 <= 2*M-1 else 0)
                    assert integral <= upper
                    bounds += 1
                assert integral >= previous
                previous = integral; monotonic += 1; identities += 1
    # Check the quotient-convention sign and root multiplicities directly.
    z = sp.Symbol('z'); relations = 0
    for M in range(2, 10):
        for q in range(M+1):
            for a in range(7):
                v = 3
                relation = sp.Poly(z**(M-q)*(z-v)**q, z)
                reduced = sp.rem(sp.Poly(z**(M-1+a), z), relation)
                assert reduced.nth(M-1) == push(q, a)*v**a
                relations += 1
    # Repeated-squaring controls with the actual circuit-state count.
    squaring = []
    for k in [3, 4, 8, 16]:
        for a in range(1, 9):
            degree = 2**a; S = k*a+k-1; M = S+k+1; q = k*(a-1)
            delta = degree*(degree-1)**(k-2)
            count = exact_count(M, q, k)
            assert delta <= count
            squaring.append({'k': k, 'power_log2': a, 'S': S, 'M': M, 'q': q,
                             'polar_count': delta, 'incidence_count': count})
    return {'expanded_coefficient_identities': identities, 'upper_bounds': bounds,
            'monotonicity_checks': monotonic, 'monic_relation_checks': relations,
            'repeated_squaring_controls': squaring}


def evaluate_graph(k, operations, point):
    values = point[:]
    gradients = [[int(i == j) for j in range(k)] for i in range(k)]
    hessians = [[[0]*k for _ in range(k)] for _ in range(k)]
    for op, a, b in operations:
        av, bv = values[a], values[b]
        ag, bg = gradients[a], gradients[b]
        ah, bh = hessians[a], hessians[b]
        if op == '+':
            value = (av+bv) % P
            grad = [(x+y) % P for x, y in zip(ag, bg)]
            hess = [[(ah[i][j]+bh[i][j]) % P for j in range(k)] for i in range(k)]
        else:
            value = av*bv % P
            grad = [(x*bv+y*av) % P for x, y in zip(ag, bg)]
            hess = [[(ah[i][j]*bv+bh[i][j]*av+ag[i]*bg[j]+bg[i]*ag[j]) % P for j in range(k)] for i in range(k)]
        values.append(value); gradients.append(grad); hessians.append(hess)
    return values, gradients, hessians


def state_local_checks():
    rng = random.Random(26091620); cases = []; output_reuse_detected = 0
    for case in range(35):
        k = 3+case % 2
        operations = [('*', i, i) for i in range(k)]
        for j in range(5+case % 4):
            count = k+len(operations)
            aa, bb = rng.randrange(count), rng.randrange(count)
            operations.append(('+' if j % 3 == 0 else '*', aa, bb))
        q = sum(op == '*' and a >= k and b >= k for op, a, b in operations)
        s = k+len(operations); M = s+1
        point = [rng.randrange(1, P) for _ in range(k)]
        vals, grads, hessians = evaluate_graph(k, operations, point)
        while True:
            coeffs = [rng.randrange(P) for _ in range(s)]
            gradient = [sum(c*g[i] for c, g in zip(coeffs, grads)) % P for i in range(k)]
            hessian = [[sum(c*h[i][j] for c, h in zip(coeffs, hessians)) % P for j in range(k)] for i in range(k)]
            if gradient[-1] and rank(hessian) == k:
                break
        ell = [0]*(k-1)+[pow(point[-1], -1, P)]
        while True:
            dirs = []
            for _ in range(k-2):
                direction = [rng.randrange(P) for _ in range(k-1)]
                direction.append(-dot(direction, gradient[:-1])*pow(gradient[-1], -1, P) % P)
                dirs.append(direction)
            target_jac = [gradient, ell]+[[sum(direction[j]*hessian[j][i] for j in range(k)) % P for i in range(k)] for direction in dirs]
            if rank(target_jac) == k:
                break
        xs = list(sp.symbols(f'x0:{k}')); ws = list(sp.symbols(f'w0:{s}'))
        adjoints = list(sp.symbols(f'a0:{s}'))
        graph = [w-x for w, x in zip(ws[:k], xs)]
        for j, (op, a, b) in enumerate(operations):
            # A skew operand is replaced by its input label, matching the proof.
            if op == '+':
                expr = ws[a]+ws[b]
            elif a < k:
                expr = xs[a]*ws[b]
            elif b < k:
                expr = ws[a]*xs[b]
            else:
                expr = ws[a]*ws[b]
            graph.append(ws[k+j]-expr)
        output_value = dot(coeffs, vals)
        output = sum(c*w for c, w in zip(coeffs, ws))-output_value
        lagrangian = output+sum(a*G for a, G in zip(adjoints, graph))
        state_adjoint = [sp.diff(lagrangian, w) for w in ws]
        polars = [sum(direction[i]*sp.diff(lagrangian, xs[i]) for i in range(k)) for direction in dirs]
        equations = graph+[output]+state_adjoint+polars+[sum(c*x for c, x in zip(ell, xs))-1]
        variables = xs+ws+adjoints
        assert len(equations) == len(variables) == k+2*M-2
        values = dict(zip(xs, point)); values.update(dict(zip(ws, vals)))
        for j in range(s-1, -1, -1):
            constant = state_adjoint[j].subs({**values, adjoints[j]: 0})
            values[adjoints[j]] = -int(constant) % P
        assert all(int(eq.subs(values)) % P == 0 for eq in equations)
        # Independent forward jets agree with the implicit state adjoints.
        implicit = [int(sp.diff(lagrangian, x).subs(values)) % P for x in xs]
        assert implicit == gradient
        jacobian = [[int(sp.diff(eq, variable).subs(values)) % P for variable in variables] for eq in equations]
        rk = rank(jacobian)
        assert rk == len(variables)
        uses = [0]*s
        for op, a, b in operations:
            uses[a] += 1; uses[b] += 1
        output_reuse_detected += sum(uses[i] > 1 for i in range(k, s))
        cases.append({'k': k, 'state_count': s, 'M': M, 'non_skew_gates': q,
                      'lifted_variables': len(variables), 'lifted_jacobian_rank': rk})
    assert output_reuse_detected > 30
    return {'cases': cases, 'internal_states_with_multiple_uses': output_reuse_detected,
            'scope': 'Generic affine output levels test local isolation; these controls do not assert global smoothness.'}


def main():
    start = time.monotonic()
    result = {'status': 'passed', 'coefficients': coefficient_checks(),
              'state_local_checks': state_local_checks(), 'prime': P,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'dependency_sha256': hashlib.sha256((ROOT/'check_hybrid_charge.py').read_bytes()).hexdigest(),
              'scope': 'Finite controls, not an asymptotic proof or novelty certification.'}
    result['seconds'] = time.monotonic()-start
    (ROOT/'CHECK_NON_SKEW_TRADEOFF.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ['coefficients', 'state_local_checks']}, indent=2), flush=True)
    print(json.dumps({'coefficient_counts': {key: value for key, value in result['coefficients'].items() if key != 'repeated_squaring_controls'},
                      'local_cases': len(result['state_local_checks']['cases']),
                      'reused_states': result['state_local_checks']['internal_states_with_multiple_uses']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
