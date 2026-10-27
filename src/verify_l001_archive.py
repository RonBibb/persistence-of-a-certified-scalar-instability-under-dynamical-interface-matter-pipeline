#!/usr/bin/env python3
"""Verify relocated L001 bytes without importing or executing any producer."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    archive = args.data_dir.resolve(strict=True)
    manifest = json.loads(args.manifest.read_text())
    failures = []
    expected = set()
    total_bytes = 0
    for row in manifest["files"]:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Manifest path escapes archive: " + str(relative))
        if row["path"] in expected:
            raise ValueError("Duplicate manifest path: " + row["path"])
        expected.add(row["path"])
        path = archive / relative
        if not path.is_file() or path.is_symlink():
            failures.append({"path": row["path"], "error": "missing_or_not_regular"})
            continue
        total_bytes += path.stat().st_size
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            failures.append({"path": row["path"], "error": "content_mismatch"})
    actual = {str(p.relative_to(archive)) for p in archive.rglob("*") if p.is_file()}
    unexpected = sorted(actual - expected)
    # Git represents files and their parents, but cannot represent empty directories.
    # Keep the complete historical directory inventory without treating an absent
    # empty directory as lost evidence in a fresh checkout.
    required_directories = {
        str(parent)
        for name in expected
        for parent in Path(name).parents
        if str(parent) != "."
    }
    missing_directories = [d for d in sorted(required_directories) if not (archive / d).is_dir()]
    absent_empty_directories = [
        d for d in manifest["directories"]
        if d not in required_directories and not (archive / d).is_dir()
    ]
    passed = not failures and not unexpected and not missing_directories
    passed = passed and len(expected) == manifest["file_count"]
    passed = passed and total_bytes == manifest["bytes"]
    result = {
        "pass_status": passed,
        "files_checked": len(expected),
        "bytes_checked": total_bytes,
        "manifest_sha256": digest(args.manifest),
        "failures": failures,
        "unexpected_files": unexpected,
        "missing_directories": missing_directories,
        "unrepresented_empty_directories": absent_empty_directories,
        "scientific_producers_executed": 0,
        "scope": "Relocated record identity only; no mathematical or interval-trajectory regeneration.",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
