"""Check package hashes, then reproduce all eight finite verification suites."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
CHECKS = [
    ('check_polar_composition.py', 'CHECK_POLAR_COMPOSITION.json'),
    ('check_algebraic_transfer.py', 'CHECK_ALGEBRAIC_TRANSFER.json'),
    ('check_non_skew_tradeoff.py', 'CHECK_NON_SKEW_TRADEOFF.json'),
    ('check_rational_state_level.py', 'CHECK_RATIONAL_STATE_LEVEL.json'),
    ('check_homogeneous_fft.py', 'CHECK_HOMOGENEOUS_FFT.json'),
    ('check_column_coefficient_compression.py', 'COLUMN_COEFFICIENT_COMPRESSION_CHECKS.json'),
    ('check_improved_border_parameters.py', 'IMPROVED_BORDER_PARAMETER_CHECKS.json'),
    ('check_compressed_border_parameters.py', 'COMPRESSED_BORDER_PARAMETER_CHECKS.json'),
]


def normalized(value):
    return {k: v for k, v in value.items() if k != 'seconds'}


def main():
    if not __debug__:
        raise RuntimeError('Run Python without -O: these checks require assertions.')
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        path = (ROOT / item['path']).resolve()
        if ROOT not in path.parents:
            raise RuntimeError('A manifest path leaves the verification directory.')
        if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError(f'File integrity failure: {item["path"]}')
    print(f'Verified {len(manifest["files"])} file hashes.', flush=True)
    with tempfile.TemporaryDirectory(prefix='border-verification-') as directory:
        work = Path(directory)
        for path in ROOT.glob('*.py'):
            if path.name != Path(__file__).name:
                shutil.copyfile(path, work / path.name)
        for script, output in CHECKS:
            print(f'Running {script}', flush=True)
            result = subprocess.run([sys.executable, '-X', 'utf8', script], cwd=work,
                                    encoding='utf-8', capture_output=True, timeout=600)
            if result.returncode:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                raise RuntimeError(f'{script} failed ({result.returncode}).')
            actual = json.loads((work / output).read_text(encoding='utf-8'))
            expected = json.loads((ROOT / 'results' / output).read_text(encoding='utf-8'))
            if normalized(actual) != normalized(expected):
                raise RuntimeError(f'Result mismatch: {output}')
            print('  PASS; supplied result reproduced (runtime ignored).', flush=True)
    print('All eight finite suites passed. Uniform proofs are in the manuscript.', flush=True)


if __name__ == '__main__':
    main()
