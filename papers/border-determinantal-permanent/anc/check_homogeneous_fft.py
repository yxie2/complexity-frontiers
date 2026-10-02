"""Paired-variable FFT: homogeneous, syntactically set-multilinear control."""
from pathlib import Path
import hashlib
import json
import random
from check_multilinear_fft import Circuit, P, independent_coefficients

ROOT = Path(__file__).resolve().parent


class PairedCircuit(Circuit):
    def __init__(self, pairs):
        super().__init__(2*pairs)
        self.groups = [1 << (i//2) for i in range(2*pairs)]
        self.checked_additions = 0
        self.checked_products = 0

    def constant(self, value):
        previous = len(self.nodes)
        result = super().constant(value)
        if len(self.nodes) != previous:
            self.groups.append(0)
        return result

    def is_constant(self, node, value):
        return self.nodes[node][0] == 'constant' and self.nodes[node][1] == value % P

    def gate(self, op, a, b):
        # Remove zero inputs before checking the strict syntactic model.
        if op == 'mul':
            if self.is_constant(a, 0) or self.is_constant(b, 0):
                return self.constant(0)
            if self.is_constant(a, 1):
                return b
            if self.is_constant(b, 1):
                return a
            assert not self.groups[a] & self.groups[b]
            self.checked_products += 1
        else:
            if self.is_constant(b, 0):
                return a
            if self.is_constant(a, 0):
                return b if op == 'add' else self.gate('mul', self.constant(-1), b)
            assert self.groups[a] == self.groups[b]
            self.checked_additions += 1
        result = super().gate(op, a, b)
        self.groups.append(self.groups[a] | self.groups[b])
        return result

    def coefficients(self, pairs):
        if len(pairs) == 1:
            i = pairs[0]
            return [2*i+1, 2*i]  # y_i + x_i z
        half = len(pairs)//2
        a = self.coefficients(pairs[:half])
        b = self.coefficients(pairs[half:])
        length = 2*len(pairs)
        root = pow(3, (P-1)//length, P)
        assert pow(root, length, P) == 1 and pow(root, length//2, P) != 1
        a += [self.constant(0)]*(length-len(a))
        b += [self.constant(0)]*(length-len(b))
        af = self.fft(a, root)
        bf = self.fft(b, root)
        product = [self.gate('mul', u, v) for u, v in zip(af, bf)]
        output = self.fft(product, pow(root, -1, P))
        inv = self.constant(pow(length, -1, P))
        return [self.gate('mul', inv, v) for v in output[:len(pairs)+1]]


def independent_paired(values):
    output = [1]
    for i in range(len(values)//2):
        x, y = values[2*i:2*i+2]
        old = output
        output = [0]*(len(old)+1)
        for j, value in enumerate(old):
            output[j] = (output[j]+y*value) % P
            output[j+1] = (output[j+1]+x*value) % P
    return output


def main():
    rng = random.Random(2609160345)
    cases = []
    comparisons = restriction_comparisons = 0
    for power in range(1, 9):
        n = 1 << power
        circuit = PairedCircuit(n)
        outputs = circuit.coefficients(list(range(n)))
        assert all(circuit.groups[v] == (1 << n)-1 for v in outputs)
        for trial in range(5):
            values = [rng.randrange(P) for _ in range(2*n)]
            # Include zero coordinates, which cannot be tested by dividing by y.
            if trial == 0:
                values[1] = 0
            evaluated = circuit.evaluate(values)
            assert [evaluated[v] for v in outputs] == independent_paired(values)
            comparisons += len(outputs)
            values[1::2] = [1]*n
            restricted = circuit.evaluate(values)
            assert [restricted[v] for v in outputs] == independent_coefficients(values[::2])
            restriction_comparisons += len(outputs)
        gates = sum(op not in ('input', 'constant') for op, _, _ in circuit.nodes)
        assert circuit.non_skew <= 2*n*power
        assert gates <= 20*n*(power+1)**2
        cases.append({'pairs': n, 'variables': 2*n, 'gates': gates,
                      'non_skew_gates': circuit.non_skew,
                      'output_homogeneous_degree': n,
                      'checked_same_group_additions': circuit.checked_additions,
                      'checked_disjoint_group_products': circuit.checked_products,
                      'affine_slice_score_lower_bound': (n-n//2+1)*(n//2-1)})
    result = {'status': 'passed', 'prime': P, 'cases': cases,
              'paired_coefficient_comparisons': comparisons,
              'affine_restriction_comparisons': restriction_comparisons,
              'scope': 'Explicit construction control; the uniform proof is in HOMOGENEOUS_MULTILINEAR_BARRIER.md.',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'dependency_sha256': hashlib.sha256((ROOT/'check_multilinear_fft.py').read_bytes()).hexdigest()}
    (ROOT/'CHECK_HOMOGENEOUS_FFT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
