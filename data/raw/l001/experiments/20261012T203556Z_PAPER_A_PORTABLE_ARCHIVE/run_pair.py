#!/usr/bin/env python3
"""Capture two sequential replays after independent approval of their layer."""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("layer", choices=("authority", "consolidation"))
    args = parser.parse_args()
    if Path.cwd().resolve() != Path("/private/tmp").resolve():
        raise ValueError("run from unrelated /private/tmp cwd")
    original = HERE / "archive"
    relocated = HERE / "relocated" / "archive"
    if any(p.is_symlink() for p in original.rglob("*")):
        raise ValueError("source archive symlink")
    if relocated.exists() and any(p.is_symlink() for p in relocated.rglob("*")):
        raise ValueError("relocated archive symlink")
    shutil.copytree(original, relocated, dirs_exist_ok=True)
    results = HERE / "runs"
    results.mkdir(exist_ok=True)
    for location, archive in (("primary", original), ("relocated", relocated)):
        command = [sys.executable, "-I", "-B", str(HERE / "replay.py"), "--layer", args.layer, "--archive", str(archive)]
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        before = time.monotonic()
        completed = subprocess.run(command, capture_output=True, timeout=150)
        elapsed = time.monotonic() - before
        stem = results / (args.layer + "_" + location)
        stem.with_suffix(".stdout.json").write_bytes(completed.stdout)
        stem.with_suffix(".stderr.txt").write_bytes(completed.stderr)
        metadata = {"command": command, "cwd": str(Path.cwd()), "started_utc": started, "elapsed_seconds": elapsed, "returncode": completed.returncode, "python_version": sys.version, "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(), "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(), "replay_sha256": hashlib.sha256((HERE / "replay.py").read_bytes()).hexdigest()}
        stem.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print(json.dumps({"layer": args.layer, "location": location, "returncode": completed.returncode, "elapsed_seconds": elapsed}))
        if completed.returncode:
            raise SystemExit(completed.returncode)

if __name__ == "__main__":
    main()
