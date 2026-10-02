"""Check Newton-paper artifacts and replay the five exact verification programs."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from zipfile import ZipFile
import argparse
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'papers/sharp-newton-cancellation'
CHECKS = [
    ('verify_sharp_six.py', 'SHARP_SIX_VERIFICATION.json'),
    ('verify_unit_six.py', 'UNIT_SIX_VERIFICATION.json'),
    ('verify_unit10_examples.py', 'UNIT10_EXAMPLES_VERIFICATION.json'),
    ('verify_positive_control.py', 'CERTIFICATE_POSITIVE_CONTROL.json'),
    ('verify_families.py', 'FAMILIES_VERIFICATION.json'),
]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def portable_path(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and '..' not in path.parts and '\\' not in name,
            'Unsafe relative path: ' + name)
    return path


def canonical(result):
    return {key: value for key, value in result.items() if key not in ('at', 'seconds')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-only', action='store_true')
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run without -O or -OO: exact checks use assertions.')
    manifest = json.loads((PAPER / 'ARTIFACTS.json').read_bytes())
    listed = set()
    for row in manifest['files']:
        path = portable_path(row['path'])
        require(row['path'] not in listed, 'Duplicate manifest member')
        listed.add(row['path'])
        data = (PAPER / path).read_bytes()
        require(len(data) == row['bytes'] and sha256(data).hexdigest() == row['sha256'],
                'Artifact mismatch: ' + row['path'])
    expected_core = {'main.tex', 'paper.pdf', 'README.md', 'CITATION.cff', 'LICENSE.md',
                     'arxiv_submission.zip', 'verification.zip', 'verification_results.json'}
    require({n for n in listed if not n.startswith('anc/')} == expected_core,
            'Incomplete core artifact set')
    ancillary = {n.removeprefix('anc/'): (PAPER / n).read_bytes() for n in listed if n.startswith('anc/')}
    with ZipFile(PAPER / 'verification.zip') as archive:
        require(archive.testzip() is None, 'Corrupt verification archive')
        require(len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate archive members')
        require(set(archive.namelist()) == set(ancillary), 'Code archive does not match browsable code')
        for name, data in ancillary.items():
            portable_path(name)
            require(archive.read(name) == data, 'Code archive mismatch: ' + name)
    with ZipFile(PAPER / 'arxiv_submission.zip') as archive:
        require(archive.testzip() is None, 'Corrupt source archive')
        require(sorted(archive.namelist()) == ['anc/README.txt', 'anc/verification.zip', 'main.tex'],
                'Unexpected source archive contents')
        require(archive.read('main.tex') == (PAPER / 'main.tex').read_bytes(), 'LaTeX archive mismatch')
        require(archive.read('anc/verification.zip') == (PAPER / 'verification.zip').read_bytes(),
                'Embedded verification archive mismatch')
    code_manifest = json.loads(ancillary['MANIFEST.json'])
    require({row['path'] for row in code_manifest['files']} | {'MANIFEST.json'} == set(ancillary),
            'Incomplete code manifest')
    for row in code_manifest['files']:
        data = ancillary[row['path']]
        require(len(data) == row['bytes'] and sha256(data).hexdigest() == row['sha256'],
                'Code manifest mismatch: ' + row['path'])
    baseline = json.loads((PAPER / 'verification_results.json').read_bytes())
    require(baseline['status'] == 'PASS', 'Archived verification failed')
    require([(r['script'], r['report']) for r in baseline['checks']] == CHECKS,
            'Unexpected archived check set')
    for row in baseline['checks']:
        require(row['result']['status'] == 'PASS', 'Archived check failed: ' + row['script'])
    print('PASS: artifact hashes, source archive, and all 1005 ancillary files', flush=True)
    if args.integrity_only:
        return
    with tempfile.TemporaryDirectory(prefix='newton-cancellation-checks-') as temporary:
        working = Path(temporary) / 'verification'
        working.mkdir()
        for name, data in ancillary.items():
            path = working / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        subprocess.run([sys.executable, '-I', '-S', '-B', '-X', 'utf8', 'verify.py'],
                       cwd=working, check=True, timeout=540)
        for row in baseline['checks']:
            actual = json.loads((working / row['report']).read_bytes())
            require(canonical(actual) == row['result'], 'Reproduced result differs: ' + row['script'])
            print('PASS: archived result reproduced for ' + row['script'], flush=True)
    print('PASS: all five checks reproduced without modifying the archived files.', flush=True)


if __name__ == '__main__':
    main()
