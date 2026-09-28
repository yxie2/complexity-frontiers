"""Verify the Gram-paper artifacts and reproduce all four finite checks."""
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
PAPER = ROOT / 'papers/gram-singularity-thresholds'
CHECKS = (
    ('check_gram_fourier_arithmetic.py', 'gram_fourier_arithmetic_checks.json'),
    ('check_direct_gram_counts.py', 'direct_gram_count_checks.json'),
    ('check_odd_gram_first_jets.py', 'odd_gram_first_jet_checks.json'),
    ('check_valuation_strata.py', 'valuation_strata_checks.json'),
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_archive(name, expected):
    with ZipFile(PAPER / name) as archive:
        require(archive.testzip() is None, f'Corrupt archive: {name}')
        require(len(archive.namelist()) == len(set(archive.namelist())),
                f'Duplicate archive entries: {name}')
        require(set(archive.namelist()) == set(expected),
                f'Unexpected archive contents: {name}')
        for path, data in expected.items():
            require(archive.read(path) == data,
                    f'Archive bytes differ: {name}/{path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-only', action='store_true',
                        help='Check distributed files without rerunning computations.')
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run without -O: the finite checkers use assertions.')
    manifest = json.loads((PAPER / 'ARTIFACTS.json').read_text(encoding='utf-8'))
    listed = set()
    for item in manifest['files']:
        path = (PAPER / item['path']).resolve()
        require(path.is_relative_to(PAPER.resolve()), 'Invalid manifest path')
        require(item['path'] not in listed, 'Duplicate manifest path')
        listed.add(item['path'])
        data = path.read_bytes()
        require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                f"Artifact mismatch: {item['path']}")
    required = {'main.tex', 'paper.pdf', 'README.md', 'CITATION.cff', 'LICENSE.md',
                'anc/README.md', 'anc/SHA256SUMS.txt', 'arxiv_submission.zip',
                'review_bundle.zip', 'gram_verification_code.zip'}
    required.update('anc/' + name for pair in CHECKS for name in pair)
    require(required == listed, 'Incomplete or unexpected artifact manifest')

    ancillary = {path.relative_to(PAPER).as_posix(): path.read_bytes()
                 for path in (PAPER / 'anc').iterdir() if path.is_file()}
    source_files = {'main.tex': (PAPER / 'main.tex').read_bytes(), **ancillary}
    check_archive('arxiv_submission.zip', source_files)
    check_archive('gram_verification_code.zip', ancillary)
    with ZipFile(PAPER / 'review_bundle.zip') as archive:
        expected = {**source_files, 'paper.pdf': (PAPER / 'paper.pdf').read_bytes(),
                    'README.md': archive.read('README.md')}
        sums = ''.join(f'{digest(data)}  {name}\n'
                       for name, data in sorted(expected.items())).encode('utf-8')
        expected['SHA256SUMS.txt'] = sums
    check_archive('review_bundle.zip', expected)
    for line in (PAPER / 'anc/SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        checksum, name = line.split('  ', 1)
        require(digest(ancillary['anc/' + name]) == checksum,
                f'Ancillary checksum mismatch: {name}')
    for script, report in CHECKS:
        result = json.loads((PAPER / 'anc' / report).read_text(encoding='utf-8'))
        require(result['status'] == 'PASS', f'Archived check failed: {report}')
        require(result['producer_sha256'] == digest((PAPER / 'anc' / script).read_bytes()),
                f'Producer hash mismatch: {report}')
    print('PASS gram-singularity-thresholds: artifact and archive integrity', flush=True)
    if args.integrity_only:
        return

    with tempfile.TemporaryDirectory(prefix='gram-singularity-checks-') as directory:
        working = Path(directory) / 'anc'
        shutil.copytree(PAPER / 'anc', working,
                        ignore=shutil.ignore_patterns('__pycache__'))
        for script, report in CHECKS:
            subprocess.run([sys.executable, '-X', 'utf8', script],
                           cwd=working, check=True, timeout=600)
            expected = json.loads((PAPER / 'anc' / report).read_text(encoding='utf-8'))
            actual = json.loads((working / report).read_text(encoding='utf-8'))
            # Elapsed time is the only nonreproducible field.
            expected.pop('seconds', None)
            actual.pop('seconds', None)
            require(actual == expected, f'Computed results differ: {report}')
            print(f'PASS {report}: reproduced all archived results', flush=True)
    print('Finite checks supplement the manuscript proofs; they do not establish peer review or novelty.')


if __name__ == '__main__':
    main()
