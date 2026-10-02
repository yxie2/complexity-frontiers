"""Check the border-determinantal release and reproduce its eight finite suites."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from zipfile import ZipFile
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'papers/border-determinantal-permanent'
SOURCES = {'main.tex', 'parameter_bounds.tex', 'coefficient_compression.tex',
           'non_skew_appendix.tex', 'rational_state_appendix.tex'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def portable_path(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and '..' not in path.parts and '\\' not in name,
            'Unsafe relative path: ' + name)
    return path


def check_manifest(manifest, read):
    listed = set()
    for item in manifest['files']:
        name = item['path']
        portable_path(name)
        require(name not in listed, 'Duplicate manifest member: ' + name)
        listed.add(name)
        data = read(name)
        require(len(data) == item['bytes'] and sha256(data).hexdigest() == item['sha256'],
                'Artifact mismatch: ' + name)
    return listed


def archive_names(archive):
    names = archive.namelist()
    require(len(names) == len(set(names)), 'Duplicate archive members')
    for name in names:
        portable_path(name)
    require(archive.testzip() is None, 'Corrupt archive')
    return set(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-only', action='store_true')
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run without -O or -OO: the checkers use assertions.')
    manifest = json.loads((PAPER / 'ARTIFACTS.json').read_bytes())
    listed = check_manifest(manifest, lambda name: (PAPER / name).read_bytes())
    core = SOURCES | {'paper.pdf', 'README.md', 'CITATION.cff', 'LICENSE.md',
                      'arxiv_submission.zip', 'release_package.zip',
                      'release_README.txt', 'submission_metadata.json'}
    require({n for n in listed if not n.startswith('anc/')} == core,
            'Incomplete core artifact set')
    ancillary = {n.removeprefix('anc/') for n in listed if n.startswith('anc/')}
    code_manifest = json.loads((PAPER / 'anc/MANIFEST.json').read_bytes())
    code_files = check_manifest(code_manifest, lambda name: (PAPER / 'anc' / name).read_bytes())
    require(code_files | {'MANIFEST.json'} == ancillary, 'Incomplete code manifest')
    with ZipFile(PAPER / 'arxiv_submission.zip') as archive:
        require(archive_names(archive) == SOURCES, 'Unexpected arXiv source archive contents')
        for name in SOURCES:
            require(archive.read(name) == (PAPER / name).read_bytes(), 'Source mismatch: ' + name)
    with ZipFile(PAPER / 'release_package.zip') as archive:
        names = archive_names(archive)
        release_manifest = json.loads(archive.read('MANIFEST.json'))
        release_files = check_manifest(release_manifest, archive.read)
        require(release_files | {'MANIFEST.json'} == names, 'Incomplete release manifest')
        mapping = {f'paper/{name}': name for name in SOURCES}
        mapping.update({'paper/superquadratic_border_determinantal.pdf': 'paper.pdf',
                        'README.txt': 'release_README.txt',
                        'submission_metadata.json': 'submission_metadata.json'})
        mapping.update({f'verification/{name}': f'anc/{name}' for name in ancillary})
        require(set(mapping) == release_files, 'Unexpected release archive contents')
        for original, browsable in mapping.items():
            require(archive.read(original) == (PAPER / browsable).read_bytes(),
                    'Release archive mismatch: ' + original)
    print(f'PASS: {len(listed)} artifact hashes, both archives, and the portable code manifest.',
          flush=True)
    if not args.integrity_only:
        subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8',
                        str(PAPER / 'anc/run_verification.py')],
                       check=True, timeout=900)


if __name__ == '__main__':
    main()
