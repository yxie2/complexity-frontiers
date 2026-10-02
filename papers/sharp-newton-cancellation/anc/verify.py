"""Validate the ancillary manifest and run all five exact checks."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CHECKS = ['verify_sharp_six.py', 'verify_unit_six.py', 'verify_unit10_examples.py',
          'verify_positive_control.py', 'verify_families.py']

def main():
    if not __debug__:
        raise RuntimeError('Run without Python optimization flags.')
    manifest = json.loads((HERE / 'MANIFEST.json').read_bytes())
    names = set()
    for row in manifest['files']:
        name = row['path']
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in names:
            raise ValueError('Invalid or duplicate manifest path: ' + name)
        names.add(name)
        raw = (HERE / path).read_bytes()
        if len(raw) != row['bytes'] or sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Manifest mismatch: ' + name)
    print('Manifest: PASS (' + str(len(names)) + ' files)', flush=True)
    results = []
    for name in CHECKS:
        command = 'import runpy,sys;sys.path.insert(0,' + repr(str(HERE)) + ');runpy.run_path(' + repr(str(HERE / name)) + ',run_name="__main__")'
        result = subprocess.run([sys.executable, '-I', '-S', '-B', '-X', 'utf8', '-c', command],
                                cwd=HERE, capture_output=True, text=True, encoding='utf8')
        (HERE / (name + '.log')).write_text(result.stdout + result.stderr, encoding='utf8')
        if result.returncode:
            print(result.stdout + result.stderr)
            raise RuntimeError(name + ' failed')
        results.append({'checker': name, 'sha256': sha256((HERE / name).read_bytes()).hexdigest(), 'status': 'PASS'})
        print(name + ': PASS', flush=True)
    report = {'status': 'PASS', 'manifest_sha256': sha256((HERE / 'MANIFEST.json').read_bytes()).hexdigest(), 'checks': results}
    (HERE / 'VERIFICATION.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')

if __name__ == '__main__':
    main()
