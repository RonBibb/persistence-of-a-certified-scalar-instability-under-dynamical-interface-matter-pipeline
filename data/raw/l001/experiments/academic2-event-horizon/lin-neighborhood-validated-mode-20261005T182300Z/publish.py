"""Seal the one authorized full-neighborhood result after independent acceptance."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "lin-neighborhood-validated-mode-20261005T182300Z"
GUARD = "2c83c19c3db530b475b59cbffcde1d22db86e90a72cbeb4070b76fdc3aaf07cf"
EXPECTED = "NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_ON_STATIC_PARAMETER_NEIGHBORHOOD"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text())


def write(name, data):
    path = ROOT / name
    with path.open("x") as stream:
        json.dump(data, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    path.chmod(0o444)


def main():
    if ROOT.name != NAME:
        raise RuntimeError("Publication target is not this capsule")
    for name in ("RESULT.json", "TERMINAL.json", "MANIFEST.json"):
        if (ROOT / name).exists():
            raise RuntimeError("Publication already exists: " + name)
    B = read("BINDINGS.json")
    R = read("output/RESULT.json")
    A = read("INDEPENDENT_AUDIT.json")
    guard = sha(ROOT / "BINDINGS.json")
    assert guard == GUARD == R["guard"] == A["guard"]
    assert guard == read("FREEZE_RECORD.json")["binding_sha256"]
    assert A["audit_pass"]
    assert A["classification_independently_derived"] == R["classification"] == EXPECTED
    assert A["result_sha256"] == sha(ROOT / "output/RESULT.json")
    assert A["terminal_sha256"] == sha(ROOT / "output/TERMINAL.json")
    assert A["audit_source_sha256"] == sha(ROOT / "postrun_audit.py")
    T = read("output/TERMINAL.json")
    assert T["guard"] == guard and T["status"] == "COMPLETE"
    assert T["result_sha256"] == sha(ROOT / "output/RESULT.json")
    assert not (ROOT / "output/FAILURE.json").exists()
    assert R["endpoint_certificate"] and R["uniform_separation_certificate"]
    assert len(R["tasks"]) == 6
    assert all(t["status"] == "COMPLETE" for t in R["tasks"])
    assert sum(t["cells"] for t in R["tasks"]) == 73683
    assert R["config"] == B["config"]
    assert B["config"]["scope"] == "EVERY_PARAMETER_PAIR_IN_COMPLETE_CERTIFIED_STATIC_BOX"
    for name, expected in (B["source"] | B["review_sources"]).items():
        assert sha(ROOT / name) == expected, name
    for entry in B["inputs"].values():
        assert sha(ROOT / entry["path"]) == entry["sha256"], entry["path"]
    required = ["POSTRUN_REVIEW.md", "INDEPENDENT_AUDIT.json", "RESULT_REPORT.md"]
    assert all((ROOT / name).is_file() for name in required)
    now = datetime.now(timezone.utc).isoformat()
    final = {
        "status": "COMPLETE",
        "classification": R["classification"],
        "independently_accepted": True,
        "evidence_class": "INTERVAL_CERTIFIED_MODE_EXISTENCE_FOR_EVERY_PARAMETER_PAIR_IN_STATIC_NEIGHBORHOOD",
        "guard": guard,
        "sealed_utc": now,
        "physical_run_seconds": R["elapsed_seconds"],
        "parameter_box_exact": B["config"]["parameter_box"],
        "static_root_tube_exact": B["config"]["A"],
        "upper_wall_interval_exact": B["config"]["D"],
        "mu_open_interval_exact": B["config"]["mu"],
        "quantifier": "FOR_EVERY_FIXED_PARAMETER_PAIR_EXISTS_AT_LEAST_ONE_MODE_ON_ITS_SAME_EXACT_STATIC_BACKGROUND",
        "validated_cells": sum(t["cells"] for t in R["tasks"]),
        "checkpoint_count": A["checkpoint_count"],
        "central_predecessor": "../lin-central-validated-mode-r1-20261005T172800Z",
        "static_neighborhood_parent": "../lin-static-parameter-neighborhood-r2-20261005T120100Z",
        "artifacts": {name: sha(ROOT / name) for name in [
            "output/RESULT.json", "output/TERMINAL.json", *required, "postrun_audit.py"]},
        "limits": [
            "exact previously certified two-parameter neighborhood only",
            "not one common eigenvalue, eigenvalue uniqueness, lowest mode, or a full spectrum",
            "no smooth global eigenbranch selection claimed",
            "not nonlinear fate, causal admission, or initial-data/P16 identification",
            "declared canonical scalar and pure-potential two-wall model only",
            "linear mode sign does not choose expansion versus contraction"],
        "successor_launched": False,
        "active_scientific_computation": False,
    }
    write("RESULT.json", final)
    write("TERMINAL.json", {
        "status": "COMPLETE", "classification": R["classification"], "guard": guard,
        "result_sha256": sha(ROOT / "RESULT.json"),
        "audit_sha256": sha(ROOT / "INDEPENDENT_AUDIT.json"), "utc": now})
    files = {}
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.json":
            if path.suffix == ".pyc" or "__pycache__" in path.parts:
                raise RuntimeError("Unintended cache in packet")
            files[str(path.relative_to(ROOT))] = {
                "sha256": sha(path), "bytes": path.stat().st_size}
    write("MANIFEST.json", {
        "schema": "whole-file-seal-v1", "sealed_utc": now,
        "file_count": len(files), "files": files})
    for rel, entry in files.items():
        assert sha(ROOT / rel) == entry["sha256"]
        (ROOT / rel).chmod(0o444)
    print(json.dumps({
        "status": "SEALED", "classification": R["classification"],
        "verified_files": len(files), "result_sha256": sha(ROOT / "RESULT.json"),
        "manifest_sha256": sha(ROOT / "MANIFEST.json")}, indent=2))


if __name__ == "__main__":
    main()
