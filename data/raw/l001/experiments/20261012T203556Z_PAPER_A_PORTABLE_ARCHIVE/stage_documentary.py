#!/usr/bin/env python3
"""Add selected paper records for offline reading, without proof execution."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
ARCHIVE = HERE / "archive"
PRIOR = "20261012T192834Z_PAPER_A_STATIC_CONTRIBUTION"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe(base, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("unsafe path")
    path = base / relative
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("symlink")
    path.resolve().relative_to(base.resolve())
    return path

def main():
    prior = json.loads(safe(SOURCE, PRIOR + "/CLAIM_EVIDENCE.json").read_text())
    existing = {}
    for layer in ("AUTHORITY", "CONSOLIDATION"):
        for record in json.loads((HERE / (layer + "_ARTIFACT_MANIFEST.json")).read_text())["files"]:
            existing[record["origin_relative_to_experiments"]] = record
    requested = [(key, record["path"], record.get("sha256"), record["role"]) for key, record in prior["sources"].items()]
    requested += [("prior_claim_map", PRIOR + "/CLAIM_EVIDENCE.json", None, "original selected claim evidence map"), ("prior_contribution", PRIOR + "/CONTRIBUTION.md", None, "original paper-facing contribution")]
    records = []
    for key, origin, expected, role in requested:
        source = safe(SOURCE, origin)
        before = digest(source)
        if expected and before != expected:
            raise ValueError("prior selected binding mismatch: " + key)
        reused = origin in existing
        relative = existing[origin]["archive_path"] if reused else "documentary/evidence/" + origin
        target = safe(ARCHIVE, relative)
        if reused:
            if digest(target) != before:
                raise ValueError("staged byte conflict")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        after = digest(target)
        if before != after:
            raise ValueError("copy mismatch")
        records.append({"evidence_key": key, "archive_path": relative, "origin_relative_to_experiments": origin, "sha256": after, "bytes": target.stat().st_size, "role": role, "original_bound_sha256": expected, "reused_from_executed_layer": reused, "documentary_inclusion_is_not_proof_replay": True})
    result = {"schema": "paper-a-documentary-manifest/v1", "layer": "documentary", "files": records, "selected_source_count": len(prior["sources"]), "file_count": len(records), "new_file_count": sum(not r["reused_from_executed_layer"] for r in records), "total_bytes": sum(r["bytes"] for r in records), "scope": "Offline selected-claim reading only; no new scientific verification or recursive producer closure"}
    (HERE / "DOCUMENTARY_ARTIFACT_MANIFEST.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"selected_source_count": result["selected_source_count"], "files": result["file_count"], "new_files": result["new_file_count"]}))

if __name__ == "__main__":
    main()
