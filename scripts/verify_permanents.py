"""Verify the permanent papers and reproduce their archived finite checks."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ('three-by-four-permanents', 'prime-size-permanents')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(name):
    paper = ROOT / 'papers' / name
    artifacts = json.loads((paper / 'ARTIFACTS.json').read_text(encoding='utf-8'))
    for item in artifacts['files']:
        path = paper / item['path']
        require(path.stat().st_size == item['bytes'], f"Wrong size: {path}")
        require(digest(path.read_bytes()) == item['sha256'], f"Wrong hash: {path}")
    expected = {item['path']: item for item in artifacts['review_archive_members']}
    with ZipFile(paper / 'review_package.zip') as archive:
        require(archive.testzip() is None, 'Corrupt review archive')
        require(len(archive.namelist()) == len(expected), 'Duplicate or extra archive entries')
        require(set(archive.namelist()) == set(expected), 'Unexpected archive contents')
        for member, item in expected.items():
            path = PurePosixPath(member)
            require(not path.is_absolute() and '..' not in path.parts, 'Unsafe archive path')
            require(path.parts[0] == artifacts['archive_root'], 'Wrong archive root')
            data = archive.read(member)
            require(len(data) == item['bytes'] and digest(data) == item['sha256'],
                    f'Archive member differs: {member}')
            filename = path.name
            if filename == 'main.pdf':
                counterpart = paper / 'paper.pdf'
            elif filename == 'main.tex':
                counterpart = paper / 'main.tex'
            elif filename != 'README.md':
                counterpart = paper / 'anc' / filename
            else:
                continue  # The portable package has its own build instructions.
            require(data == counterpart.read_bytes(), f'Archive and repository differ: {member}')
    print(f'PASS {name}: artifact and review-package integrity', flush=True)
    expected_result = json.loads((paper / 'anc/verification_results.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='permanent-check-') as directory:
        temporary = Path(directory)
        shutil.copytree(paper / 'anc', temporary / 'anc', ignore=shutil.ignore_patterns('__pycache__'))
        subprocess.run([sys.executable, '-X', 'utf8', str(temporary / 'anc/verify.py')],
                       cwd=temporary / 'anc', check=True, timeout=300)
        actual = json.loads((temporary / 'anc/verification_results.json').read_text(encoding='utf-8'))
        require(actual == expected_result, f'Computed results differ for {name}')
    print(f'PASS {name}: all finite results match the archived records', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('papers', nargs='*', help='Paper folders to verify; default: both')
    args = parser.parse_args()
    requested = args.papers or list(PAPERS)
    for name in requested:
        if name not in PAPERS:
            parser.error(f'Unknown paper {name!r}; choose from {", ".join(PAPERS)}')
        verify(name)
    print('Finite checks supplement the written proofs; they do not establish peer review or novelty.')


if __name__ == '__main__':
    main()
