#!/usr/bin/env python3
"""Mechanically stage the frozen authority chain; never execute its verifier."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "academic2-event-horizon"
PACKET = "lin-static-theorem-publication-upgrade-20261005T050426Z"
ARCHIVE = HERE / "archive"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe(base, relative):
    path = base / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(relative)
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("symlink: " + str(path))
    path.resolve().relative_to(base.resolve())
    return path

def main():
    bindings = json.loads((SOURCE / PACKET / "BINDINGS.json").read_text())
    records = []
    requested = [(x["path"], x["sha256"], x["role"]) for x in bindings["files"]]
    requested += [(f"branches/02-event-horizon/{PACKET}/{name}", None, "original verification entrypoint" if name.endswith(".py") else "original binding record") for name in ("verify_upgrade.py", "BINDINGS.json")]
    for relative, expected, role in requested:
        origin = Path(relative).relative_to("branches/02-event-horizon")
        source = safe(SOURCE, origin)
        target = safe(ARCHIVE, relative)
        before = digest(source)
        if expected and before != expected:
            raise ValueError("canonical source hash mismatch: " + relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        after = digest(target)
        if before != after:
            raise ValueError("copy mismatch: " + relative)
        records.append({"archive_path": relative, "origin_relative_to_experiments": "academic2-event-horizon/" + str(origin), "sha256": after, "bytes": target.stat().st_size, "role": role, "original_bound_sha256": expected})
    manifest = {"schema": "paper-a-portable-archive-manifest/v1", "layer": "authority", "files": records, "file_count": len(records), "total_bytes": sum(x["bytes"] for x in records), "copy_policy": "byte identical, regular files only, no symlink or legacy fallback"}
    (HERE / "AUTHORITY_ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"staged_files": len(records), "total_bytes": manifest["total_bytes"]}))

if __name__ == "__main__":
    main()
