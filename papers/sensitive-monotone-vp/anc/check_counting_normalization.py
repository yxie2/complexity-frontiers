"""Exact expansions audit the profile-only counting normalizer."""
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import random
import time

ROOT = Path(__file__).resolve().parent
G = 4
N = 2 * G
ZERO = (0,) * N
SEED = 202609151330


def add(a, b):
    c = dict(a)
    for e, x in b.items():
        c[e] = c.get(e, F(0)) + x
    return {e: x for e, x in c.items() if x}


def mul(a, b):
    c = {}
    for e, x in a.items():
        for f, y in b.items():
            g = tuple(u + v for u, v in zip(e, f))
            c[g] = c.get(g, F(0)) + x * y
    return {e: x for e, x in c.items() if x}


def variable(j):
    e = list(ZERO)
    e[j] = 1
    return {tuple(e): F(1)}


def linearize(p):
    out = {}
    for e, x in p.items():
        key = tuple(int(a > 0) for a in e)
        out[key] = out.get(key, F(0)) + x
    return out


def expand(nodes):
    vals = []
    for node in nodes:
        if node[0] == 'v':
            vals.append(variable(node[1]))
        elif node[0] == 'c':
            vals.append({ZERO: node[1]} if node[1] else {})
        else:
            vals.append((add if node[0] == '+' else mul)(
                vals[node[1]], vals[node[2]]))
    return vals


def oracle_profiles(p):
    return tuple(frozenset(j for e in p for j in (2*i, 2*i+1) if e[j])
                 for i in range(G))


def extendable(p):
    prof = oracle_profiles(p)
    for e in p:
        for i, choices in enumerate(prof):
            present = sum(e[j] > 0 for j in (2*i, 2*i+1))
            if present > 1 or (len(choices) > 1 and present != 1):
                return False
    return True


def oracle_normalized(p):
    fixed = {next(iter(s)) for s in oracle_profiles(p) if len(s) == 1}
    out = {}
    for e, x in p.items():
        key = tuple(int(a > 0 and j not in fixed) for j, a in enumerate(e))
        out[key] = out.get(key, F(0)) + x
    return out


def normalize(nodes, omit_restoration=False):
    # No expanded polynomials or formal degrees enter this construction.
    out = [('c', F(0)), ('c', F(1))]
    mappings, profiles, nonzero = [], [], []
    empty = tuple(frozenset() for _ in range(G))
    variables = {}

    def var(j):
        if j not in variables:
            variables[j] = len(out)
            out.append(('v', j))
        return variables[j]

    def restore(index, labels):
        if omit_restoration:
            return index
        for j in labels:
            old = index
            label = var(j)
            index = len(out)
            out.append(('*', old, label))
        return index

    for node in nodes:
        op = node[0]
        if op == 'v':
            prof = list(empty)
            prof[node[1] // 2] = frozenset([node[1]])
            profiles.append(tuple(prof))
            mappings.append(1)
            nonzero.append(True)
            continue
        if op == 'c':
            profiles.append(empty)
            nonzero.append(bool(node[1]))
            mappings.append(len(out))
            out.append(node)
            continue
        l, r = node[1:]
        if op == '*' and not (nonzero[l] and nonzero[r]):
            profiles.append(empty); mappings.append(0); nonzero.append(False)
            continue
        if op == '+' and not (nonzero[l] and nonzero[r]):
            j = l if nonzero[l] else r
            profiles.append(profiles[j]); mappings.append(mappings[j])
            nonzero.append(nonzero[j])
            continue
        pl, pr = profiles[l], profiles[r]
        pv = tuple(a | b for a, b in zip(pl, pr))
        if op == '*':
            assert all(not a or not b or (a == b and len(a) == 1)
                       for a, b in zip(pl, pr))
            left, right = mappings[l], mappings[r]
        else:
            assert all(len(pv[i]) < 2 or (pl[i] and pr[i]) for i in range(G))
            left = restore(mappings[l], [
                next(iter(pl[i])) for i in range(G)
                if len(pv[i]) > 1 and len(pl[i]) == 1])
            right = restore(mappings[r], [
                next(iter(pr[i])) for i in range(G)
                if len(pv[i]) > 1 and len(pr[i]) == 1])
        mappings.append(len(out))
        out.append((op, left, right))
        profiles.append(pv); nonzero.append(True)
    output = restore(mappings[-1], [next(iter(s)) for s in profiles[-1] if len(s) == 1])
    gates = sum(node[0] in ('+', '*') for node in nodes)
    new_gates = sum(node[0] in ('+', '*') for node in out)
    assert new_gates <= (2*G+1)*gates+G
    return out, mappings, profiles, output, new_gates


def evaluate(p, bits):
    return sum(c for e, c in p.items()
               if all(not power or bits[j] for j, power in enumerate(e)))


def main():
    start = time.monotonic()
    rng = random.Random(SEED)
    checked = shared = cube_points = corrupted = 0
    for trial in range(400):
        nodes = [('v', j) for j in range(N)] + [
            ('c', x) for x in (F(0), F(1,2), F(1), F(2))]
        vals = expand(nodes)
        for _ in range(36):
            for attempt in range(200):
                l = rng.randrange(len(nodes))
                r = l if rng.randrange(3) == 0 else rng.randrange(len(nodes))
                op = rng.choice(('+', '*'))
                q = (add if op == '+' else mul)(vals[l], vals[r])
                if (len(q) <= 100 and max((sum(e) for e in q), default=0) <= 12
                        and extendable(q)):
                    nodes.append((op, l, r)); vals.append(q)
                    shared += int(op == '*' and l == r)
                    break
            else:
                raise AssertionError('Could not construct admissible random gate')
        # Complete every fixed or absent group at the chosen output.
        # Flexible groups are already mandatory by extendability.
        chosen = rng.choice([j for j, p in enumerate(vals) if p])
        current = chosen
        prof = oracle_profiles(vals[chosen])
        for i, choices in enumerate(prof):
            if len(choices) <= 1:
                j = next(iter(choices)) if choices else 2*i
                nodes.append(('*', current, j))
                vals.append(mul(vals[current], vals[j]))
                current = len(nodes)-1
        if current != len(nodes)-1:
            nodes.append(('*', current, N+2))
            vals.append(vals[current])
        original = vals[-1]
        assert all(sum(e[j] > 0 for j in (2*i, 2*i+1)) == 1
                   for e in original for i in range(G))
        compiled, mapping, profiles, output, _ = normalize(nodes)
        actual = expand(compiled)
        for i, p in enumerate(vals):
            assert profiles[i] == oracle_profiles(p)
            assert actual[mapping[i]] == oracle_normalized(p)
            checked += 1
        assert actual[output] == linearize(original)
        bad, _, _, bad_out, _ = normalize(nodes, omit_restoration=True)
        corrupted += int(expand(bad)[bad_out] != linearize(original))
        if trial < 40:
            for bits in product((0, 1), repeat=N):
                assert evaluate(original, bits) == evaluate(actual[output], bits)
                cube_points += 1

    # Formal degree 4*2^256; the compiler sees only constant-size profiles.
    nodes = [('v', j) for j in range(N)]
    outputs = []
    for i in range(G):
        powers = []
        for j in (2*i, 2*i+1):
            current = j
            for _ in range(256):
                nodes.append(('*', current, current))
                current = len(nodes)-1
            powers.append(current)
        nodes.append(('+', *powers)); outputs.append(len(nodes)-1)
    current = outputs[0]
    for j in outputs[1:]:
        nodes.append(('*', current, j)); current = len(nodes)-1
    compiled, _, _, output, new_gates = normalize(nodes)
    target = {ZERO: F(1)}
    for i in range(G):
        target = mul(target, add(variable(2*i), variable(2*i+1)))
    assert expand(compiled)[output] == target
    huge_original = expand(nodes)[-1]
    assert linearize(huge_original) == target
    assert max(sum(e) for e in huge_original) == 4*2**256

    # One-hot agreement does not suffice: this extra monomial is invisible there.
    extra = mul(variable(0), variable(1))
    for i in range(1, G):
        extra = mul(extra, variable(2*i))
    invalid = add(target, extra)
    for choices in product((0, 1), repeat=G):
        bits = [0]*N
        for i, choice in enumerate(choices):
            bits[2*i+choice] = 1
        assert evaluate(invalid, bits) == evaluate(target, bits)
    assert evaluate(invalid, [1]*N) != evaluate(target, [1]*N)
    assert not extendable(invalid)

    result = {
        'status': 'PASS', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'seed': SEED,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'manuscript_sha256': hashlib.sha256((ROOT.parent/'main.tex').read_bytes()).hexdigest(),
        'random_dags': 400, 'gate_profiles_and_exact_normalized_polynomials': checked,
        'self_shared_random_products': shared, 'entire_cube_points_checked': cube_points,
        'omitted_restoration_corruptions_rejected': corrupted,
        'large_degree_fixture': {
            'formal_degree': '4*2^256', 'output_monomials': 16,
            'original_gates': sum(node[0] in ('+', '*') for node in nodes),
            'normalized_gates': new_gates},
        'one_hot_only_generalization_rejected': True,
        'elapsed_seconds': time.monotonic()-start,
        'scope': 'Finite exact expansions audit the profile-only construction and reuse accounting. The universal normalization and lower bound are analytic proofs.'
    }
    (ROOT/'COUNTING_NORMALIZATION_CHECK.json').write_text(
        json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
