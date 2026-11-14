#!/usr/bin/env python3
"""Check collected bytes, not scientific predicates. Python 3.11+, stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = root / 'data/raw/paper-a-20261114/DATA_MANIFEST.json'
    data = json.loads(manifest.read_text())
    failures = []
    checked = 0
    for relative, expected in data['files'].items():
        p = root / relative
        if not p.resolve().is_relative_to(root):
            failures.append({'path': relative, 'reason': 'outside package'})
            continue
        if not p.is_file():
            failures.append({'path': relative, 'reason': 'missing'})
            continue
        with p.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        checked += 1
        if actual != expected['sha256'] or p.stat().st_size != expected['bytes']:
            failures.append({'path': relative, 'reason': 'identity mismatch; check Git LFS hydration'})
    result = {'pass': not failures, 'files_checked': checked, 'failures': failures,
              'scope': 'File identity only; no producer, interval solve or scientific revalidation executed.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
