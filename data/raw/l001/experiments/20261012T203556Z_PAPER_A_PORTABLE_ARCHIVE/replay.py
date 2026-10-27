#!/usr/bin/env python3
"""Verify staged bytes and run only an explicitly selected original verifier."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYERS = {
    "authority": ("AUTHORITY_ARTIFACT_MANIFEST.json", "branches/02-event-horizon/lin-static-theorem-publication-upgrade-20261005T050426Z/verify_upgrade.py"),
    "consolidation": ("CONSOLIDATION_ARTIFACT_MANIFEST.json", "branches/02-event-horizon/lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py"),
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", choices=LAYERS, default="authority")
    parser.add_argument("--archive", type=Path, default=HERE / "archive")
    args = parser.parse_args()
    archive = args.archive.absolute()
    manifest_name, entrypoint = LAYERS[args.layer]
    manifest = json.loads((HERE / manifest_name).read_text())
    for record in manifest["files"]:
        relative = Path(record["archive_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("unsafe manifest path")
        target = archive / relative
        if any(p.is_symlink() for p in [target, *target.parents]):
            raise ValueError("symlink forbidden")
        target.resolve().relative_to(archive.resolve())
        if hashlib.sha256(target.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("archive hash mismatch: " + str(relative))
    completed = subprocess.run([sys.executable, "-I", "-B", str(archive / entrypoint)], capture_output=True, text=True, timeout=120, cwd=Path.cwd())
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    print(completed.stdout, end="")
    raise SystemExit(completed.returncode)

if __name__ == "__main__":
    main()
