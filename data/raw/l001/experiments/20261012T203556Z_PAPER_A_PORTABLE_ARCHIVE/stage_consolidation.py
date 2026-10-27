#!/usr/bin/env python3
"""Stage precisely the original consolidation verifier's saved-data closure."""
import ast
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "academic2-event-horizon"
ARCHIVE = HERE / "archive"
PREFIX = "branches/02-event-horizon/"
PACKET = "lin-d1-d2a-theorem-consolidation-20261002T175556Z"
MANIFEST_PACKETS = [
    "lin-physical-exterior-capture-window-20261001T194822Z",
    "lin-d1-validated-flow-prerequisite-20261001T212157Z",
    "lin-d1-validated-event-prerequisite-20261001T212800Z",
    "lin-d1-independent-audit-20261002T014828Z",
    "lin-d1-high-resolution-confirmation-20261002T015100Z",
    "lin-d2a-fixed-separation-cover-r1-20261002T083633Z",
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe(base, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("unsafe path: " + str(relative))
    target = base / relative
    if any(p.is_symlink() for p in [target, *target.parents]):
        raise ValueError("symlink: " + str(target))
    target.resolve().relative_to(base.resolve())
    return target

def main():
    verifier = safe(SOURCE, PACKET + "/verify_evidence.py")
    tree = ast.parse(verifier.read_text())
    expected = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXPECTED" for t in node.targets))
    requested = {}
    def add(relative, expected_hash, role):
        safe(ARCHIVE, relative)
        if relative in requested:
            previous = requested[relative]
            if expected_hash and previous["expected"] and expected_hash != previous["expected"]:
                raise ValueError("conflicting bindings")
            previous["expected"] = previous["expected"] or expected_hash
            previous["roles"].append(role)
        else:
            requested[relative] = {"expected": expected_hash, "roles": [role]}
    for relative, expected_hash in expected.items():
        add(relative, expected_hash, "original EXPECTED anchor; scripts hash only")
    for packet in MANIFEST_PACKETS:
        manifest = json.loads(safe(SOURCE, packet + "/MANIFEST.json").read_text())
        add(PREFIX + packet + "/MANIFEST.json", None, "original packet manifest")
        add(PREFIX + packet + "/TERMINAL.json", None, "terminal binding for original manifest")
        for relative, expected_hash in manifest["files"].items():
            safe(SOURCE / packet, relative)
            add(PREFIX + packet + "/" + relative, expected_hash, "manifest-bound bytes; contextual records and scripts are hash only")
    checkpoint_base = MANIFEST_PACKETS[-1] + "/output/checkpoints"
    checkpoints = sorted(safe(SOURCE, checkpoint_base).glob("checkpoint-*.json"))
    if len(checkpoints) != 86:
        raise ValueError("expected exactly 86 checkpoints")
    for checkpoint in checkpoints:
        add(PREFIX + checkpoint_base + "/" + checkpoint.name, None, "saved checkpoint content-address reconstruction")
    add(PREFIX + PACKET + "/verify_evidence.py", None, "original saved-evidence verification entrypoint")
    records = []
    for relative, specification in sorted(requested.items()):
        origin = Path(relative).relative_to("branches/02-event-horizon")
        source = safe(SOURCE, origin)
        target = safe(ARCHIVE, relative)
        before = digest(source)
        if specification["expected"] and before != specification["expected"]:
            raise ValueError("canonical source hash mismatch: " + relative)
        if target.exists() and digest(target) != before:
            raise ValueError("existing staged byte conflict: " + relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        after = digest(target)
        if before != after:
            raise ValueError("copy mismatch")
        records.append({"archive_path": relative, "origin_relative_to_experiments": "academic2-event-horizon/" + str(origin), "sha256": after, "bytes": target.stat().st_size, "roles": specification["roles"], "original_bound_sha256": specification["expected"]})
    manifest = {"schema": "paper-a-portable-archive-manifest/v1", "layer": "consolidation", "files": records, "file_count": len(records), "total_bytes": sum(x["bytes"] for x in records), "manifest_packets": MANIFEST_PACKETS, "checkpoint_count": len(checkpoints), "expected_anchor_count": len(expected), "copy_policy": "byte identical, regular files only, no symlink or legacy fallback"}
    (HERE / "CONSOLIDATION_ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"staged_files": len(records), "total_bytes": manifest["total_bytes"]}))

if __name__ == "__main__":
    main()
