"""Exact implementation controls for the standard multilinear FFT circuit."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parent
P = 65537


class Circuit:
    def __init__(self, n):
        self.nodes = [('input', i, None) for i in range(n)]
        self.supports = [1 << i for i in range(n)]
        self.constants = {}
        self.non_skew = 0
        self.disjoint_products = 0

    def constant(self, value):
        value %= P
        if value not in self.constants:
            self.constants[value] = len(self.nodes)
            self.nodes.append(('constant', value, None))
            self.supports.append(0)
        return self.constants[value]

    def gate(self, op, a, b):
        if op == 'mul':
            assert not self.supports[a] & self.supports[b]
            self.disjoint_products += 1
            if all(self.nodes[c][0] not in ('input', 'constant') for c in (a, b)):
                self.non_skew += 1
        index = len(self.nodes)
        self.nodes.append((op, a, b))
        self.supports.append(self.supports[a] | self.supports[b])
        return index

    def fft(self, array, root):
        if len(array) == 1:
            return array
        even = self.fft(array[::2], root*root % P)
        odd = self.fft(array[1::2], root*root % P)
        half = len(array)//2
        output = [None]*len(array)
        power = 1
        for j in range(half):
            value = self.gate('mul', self.constant(power), odd[j])
            output[j] = self.gate('add', even[j], value)
            output[j+half] = self.gate('sub', even[j], value)
            power = power*root % P
        return output

    def coefficients(self, inputs):
        if len(inputs) == 1:
            return [self.constant(1), inputs[0]]
        half = len(inputs)//2
        a = self.coefficients(inputs[:half])
        b = self.coefficients(inputs[half:])
        length = 2*len(inputs)
        root = pow(3, (P-1)//length, P)
        assert pow(root, length, P) == 1 and pow(root, length//2, P) != 1
        a += [self.constant(0)]*(length-len(a))
        b += [self.constant(0)]*(length-len(b))
        af = self.fft(a, root)
        bf = self.fft(b, root)
        product = [self.gate('mul', u, v) for u, v in zip(af, bf)]
        output = self.fft(product, pow(root, -1, P))
        inv = self.constant(pow(length, -1, P))
        return [self.gate('mul', inv, value) for value in output[:len(inputs)+1]]

    def evaluate(self, values):
        evaluated = []
        for op, a, b in self.nodes:
            if op == 'input':
                value = values[a]
            elif op == 'constant':
                value = a
            elif op == 'add':
                value = evaluated[a]+evaluated[b]
            elif op == 'sub':
                value = evaluated[a]-evaluated[b]
            else:
                value = evaluated[a]*evaluated[b]
            evaluated.append(value % P)
        return evaluated


def independent_coefficients(values):
    output = [1]
    for value in values:
        output.append(0)
        for j in range(len(output)-1, 0, -1):
            output[j] = (output[j]+value*output[j-1]) % P
    return output


def main():
    rng = random.Random(2609160310)
    cases = []
    comparisons = 0
    for power in range(1, 9):
        n = 1 << power
        circuit = Circuit(n)
        outputs = circuit.coefficients(list(range(n)))
        for _ in range(5):
            values = [rng.randrange(P) for _ in range(n)]
            evaluated = circuit.evaluate(values)
            actual = [evaluated[v] for v in outputs]
            expected = independent_coefficients(values)
            assert actual == expected
            comparisons += len(actual)
        uses = Counter()
        for op, a, b in circuit.nodes:
            if op not in ('input', 'constant'):
                uses[a] += 1
                uses[b] += 1
        gates = sum(op not in ('input', 'constant') for op, _, _ in circuit.nodes)
        assert circuit.non_skew <= 2*n*power
        assert gates <= 20*n*(power+1)**2
        cases.append({'n': n, 'gates': gates, 'non_skew_gates': circuit.non_skew,
                      'checked_disjoint_products': circuit.disjoint_products,
                      'maximum_fanout': max(uses.values()),
                      'coefficient_trials': 5,
                      'slice_score_lower_bound': (n-n//2+1)*(n//2-1)})
    result = {'status': 'passed', 'prime': P, 'cases': cases,
              'coefficient_comparisons': comparisons,
              'scope': 'Controls for a standard construction, not proof of novelty or asymptotic inference.',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'CHECK_MULTILINEAR_FFT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
