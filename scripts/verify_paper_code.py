"""Reproduce the orthogonal-frame and symmetric-determinant finite checks."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CHECKS = {
    'orthogonal-frame-varieties': [
        (name + '.py', name + '.json') for name in (
            'orthogonal_basis_veronese',
            'six_by_six_canonical_controls',
            'triangular_frame_controls',
            'orthogonal_transverse_chart',
            'orthogonal_threshold_density',
        )
    ],
    'symmetric-determinant-apolarity': [
        ('verify_apolarity.py', 'verification_results.json'),
    ],
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paper', nargs='?', choices=['all', *CHECKS], default='all')
    parser.add_argument('--integrity-only', action='store_true')
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run without -O: the checkers use assertions.')
    selected = CHECKS if args.paper == 'all' else {args.paper: CHECKS[args.paper]}
    for slug, checks in selected.items():
        paper = ROOT / 'papers' / slug
        manifest = json.loads((paper / 'ARTIFACTS.json').read_text(encoding='utf-8'))
        for name, record in manifest['files'].items():
            path = (paper / name).resolve()
            require(path.is_relative_to(paper.resolve()), f'Invalid artifact path: {name}')
            data = path.read_bytes()
            require(len(data) == record['bytes'] and
                    hashlib.sha256(data).hexdigest() == record['sha256'],
                    f'Artifact mismatch: {slug}/{name}')
        required = ['main.tex', 'anc/README.md', 'anc/PROVENANCE.json']
        required += ['anc/' + name for pair in checks for name in pair]
        require(all(name in manifest['files'] for name in required),
                f'Incomplete artifact manifest: {slug}')
        print(f'PASS {slug}: artifact integrity', flush=True)
        if args.integrity_only:
            continue
        with tempfile.TemporaryDirectory(prefix=slug + '-checks-') as directory:
            working = Path(directory)
            shutil.copyfile(paper / 'main.tex', working / 'main.tex')
            shutil.copytree(paper / 'anc', working / 'anc',
                            ignore=shutil.ignore_patterns('__pycache__'))
            for script, report in checks:
                subprocess.run([sys.executable, '-X', 'utf8', script],
                               cwd=working / 'anc', check=True, timeout=300)
                expected = json.loads((paper / 'anc' / report).read_text(encoding='utf-8'))
                actual = json.loads((working / 'anc' / report).read_text(encoding='utf-8'))
                expected.pop('seconds', None)
                actual.pop('seconds', None)
                require(actual == expected, f'Results differ: {slug}/{report}')
                print(f'PASS {slug}/{script}: all archived results reproduced', flush=True)
    print('Finite checks supplement the written proofs; they do not prove the all-size theorems.')


if __name__ == '__main__':
    main()
