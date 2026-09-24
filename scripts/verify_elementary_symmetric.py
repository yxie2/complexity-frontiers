"""Verify the elementary-symmetric artifacts and reproduce the finite checks."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'papers/elementary-symmetric-loci'
CHECKS = (
    ('check_elementary_modular_dimensions.py', ['--groebner'], 'ELEMENTARY_MODULAR_DIMENSION_CHECKS.json'),
    ('probe_elementary_higher_orders.py', ['--groebner'], 'ELEMENTARY_HIGHER_ORDER_CHECKS.json'),
    ('check_elementary_translation.py', [], 'ELEMENTARY_TRANSLATION_CHECKS.json'),
    ('check_elementary_local_structure.py', [], 'ELEMENTARY_LOCAL_STRUCTURE_CHECKS.json'),
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-only', action='store_true',
                        help='Check packaged bytes without rerunning computations.')
    args = parser.parse_args()
    manifest = json.loads((PAPER / 'ARTIFACTS.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        path = (PAPER / item['path']).resolve()
        require(path.is_relative_to(PAPER.resolve()), 'Invalid manifest path')
        data = path.read_bytes()
        require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                f"Artifact mismatch: {item['path']}")
    with ZipFile(PAPER / 'arxiv_submission.zip') as archive:
        require(archive.namelist() == ['main.tex'], 'Unexpected arXiv archive contents')
        require(archive.testzip() is None, 'Corrupt arXiv archive')
        require(archive.read('main.tex') == (PAPER / 'main.tex').read_bytes(),
                'Archive source differs from repository source')
    print('PASS elementary-symmetric-loci: artifact and archive integrity', flush=True)
    if args.integrity_only:
        return
    with tempfile.TemporaryDirectory(prefix='elementary-symmetric-check-') as directory:
        working = Path(directory) / 'anc'
        shutil.copytree(PAPER / 'anc', working,
                        ignore=shutil.ignore_patterns('__pycache__'))
        for script, options, report in CHECKS:
            subprocess.run([sys.executable, '-X', 'utf8', script, *options],
                           cwd=working, check=True, timeout=300)
            expected = json.loads((PAPER / 'anc' / report).read_text(encoding='utf-8'))
            actual = json.loads((working / report).read_text(encoding='utf-8'))
            # Runtime is the only nonreproducible field. Source hashes are compared.
            expected.pop('seconds', None)
            actual.pop('seconds', None)
            require(actual == expected, f'Computed results differ: {report}')
            print(f'PASS {report}: reproduced all archived results', flush=True)
    print('Finite checks supplement the written proofs; they do not establish peer review or novelty.')


if __name__ == '__main__':
    main()
