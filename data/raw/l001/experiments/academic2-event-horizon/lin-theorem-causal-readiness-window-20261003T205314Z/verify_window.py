#!/usr/bin/env python3
"""Dependency-free verification of the Lin theorem-readiness window."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


WINDOW = Path(__file__).resolve().parent
RESEARCH_ROOT = WINDOW.parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def run_check(label: str, script: Path, expected: str) -> None:
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONNOUSERSITE": "1",
        }
    )
    completed = subprocess.run(
        [sys.executable, "-B", str(script)],
        cwd=RESEARCH_ROOT,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    require(completed.returncode == 0, f"{label} exited {completed.returncode}\n{completed.stdout}")
    require(expected in completed.stdout, f"{label} did not report {expected!r}\n{completed.stdout}")
    print(f"{label}=PASS")


def verify_local_manifest() -> None:
    manifest_path = WINDOW / "MANIFEST.json"
    if not manifest_path.exists():
        print("local_manifest=NOT_YET_SEALED")
        return

    manifest = load_json(manifest_path)
    require(isinstance(manifest, dict), "MANIFEST.json must be an object")
    files = manifest.get("files")
    require(isinstance(files, dict) and files, "MANIFEST.json files must be a nonempty object")
    for relative, record in files.items():
        require(isinstance(relative, str), "manifest path must be a string")
        require(isinstance(record, dict), f"manifest record is not an object: {relative}")
        path = WINDOW / relative
        require(path.is_file(), f"manifest file missing: {relative}")
        require(path.stat().st_size == record.get("bytes"), f"size mismatch: {relative}")
        require(sha256(path) == record.get("sha256"), f"hash mismatch: {relative}")

    terminal_path = WINDOW / "TERMINAL.json"
    require(terminal_path.is_file(), "sealed manifest exists without TERMINAL.json")
    terminal = load_json(terminal_path)
    require(isinstance(terminal, dict), "TERMINAL.json must be an object")
    require(
        terminal.get("manifest_sha256") == sha256(manifest_path),
        "TERMINAL.json does not bind MANIFEST.json",
    )
    result_path = WINDOW / "RESULT.json"
    require(
        terminal.get("result_sha256") == sha256(result_path),
        "TERMINAL.json does not bind RESULT.json",
    )
    require(terminal.get("status") == "COMPLETE", "terminal status is not COMPLETE")
    result = load_json(result_path)
    require(
        terminal.get("classification") == result.get("classification"),
        "terminal/result classification mismatch",
    )
    print(f"local_manifest=PASS files={len(files)}")


def main() -> int:
    required_json = [
        "AUTHORITY_BINDINGS.json",
        "FIGURE_PROVENANCE.json",
        "RESULT.json",
        "RUN_WINDOW.json",
        "THEOREM_INTERVALS_EXACT.json",
    ]
    for name in required_json:
        load_json(WINDOW / name)
        print(f"json_parse:{name}=PASS")

    result = load_json(WINDOW / "RESULT.json")
    require(isinstance(result, dict), "RESULT.json must be an object")
    require(
        result.get("classification")
        == "NARROW_STATIC_THEOREM_DRAFT_READY__CAUSAL_EXPERIMENT_NOT_ADMITTED",
        "unexpected RESULT.json classification",
    )
    require(
        result.get("static_manuscript_decision")
        == "GO_TO_NARROW_DRAFT_NOT_SUBMISSION_READY",
        "unexpected static manuscript decision",
    )
    require(
        result.get("causal_experiment_decision") == "NOT_ADMITTED",
        "unexpected causal experiment decision",
    )
    require(
        result.get("claim_boundary")
        == "Reduced static Einstein-scalar two-wall family at the declared exact parameter literals and launch domains only; no global uniqueness, parameter robustness, stability, dynamical selection, collapse, marginally trapped surface, event horizon, or baby universe.",
        "unexpected RESULT.json claim boundary",
    )
    require(
        result.get("verification", {}).get("sealed_parent_mutation") is False,
        "RESULT.json does not record sealed-parent preservation",
    )
    print("result_contract=PASS")

    required_documents = [
        "CLAIM_TO_EVIDENCE_MATRIX.md",
        "CROSS_PLATFORM_VERIFICATION.md",
        "DISCUSSION_AND_CONCLUSION_DRAFT.md",
        "FINAL_REPORT.md",
        "FORMAL_REDUCTION_LEMMA.md",
        "FUTURE_CAUSAL_ADMISSION_CONTRACT.md",
        "ISSUES_AND_RANKED_NEXT_STEPS.md",
        "INTRODUCTION_DRAFT.md",
        "INSPECTION_LEDGER.md",
        "JUNCTION_CONVENTION_AUDIT.md",
        "MANUSCRIPT_READINESS.md",
        "MANUSCRIPT_BLUEPRINT.md",
        "METHODS_CITATION_CHAIN.md",
        "NOVELTY_CITATION_CHAIN.md",
        "PARAMETER_PROVENANCE_AND_MOTIVATION.md",
        "PROOF_OBLIGATION_AUDIT.md",
        "PUBLIC_ARCHIVE_INVENTORY.md",
        "README.md",
        "REPRODUCIBILITY_COMMAND_MAP.md",
        "THEOREM_AND_PROOF_DRAFT.md",
        "THEOREM_AUTHORITY_TABLE.md",
    ]
    for name in required_documents:
        require((WINDOW / name).is_file(), f"required document missing: {name}")
    print(f"required_documents=PASS count={len(required_documents)}")

    figure_provenance = load_json(WINDOW / "FIGURE_PROVENANCE.json")
    require(isinstance(figure_provenance, dict), "FIGURE_PROVENANCE.json must be an object")
    for relative, record in figure_provenance["files"].items():
        path = WINDOW / relative
        require(path.is_file(), f"figure artifact missing: {relative}")
        require(path.stat().st_size == record["bytes"], f"figure artifact size mismatch: {relative}")
        require(sha256(path) == record["sha256"], f"figure artifact hash mismatch: {relative}")
    print(f"figure_provenance=PASS files={len(figure_provenance['files'])}")

    pycache = list(WINDOW.rglob("__pycache__"))
    require(not pycache, f"Python cache directories found: {pycache}")
    bytecode = list(WINDOW.rglob("*.pyc"))
    require(not bytecode, f"Python bytecode found: {bytecode}")
    print("window_cache_hygiene=PASS")

    run_check(
        "formal_reduction_identity",
        WINDOW / "reduction_identity_check.py",
        "FORMAL_REDUCTION_IDENTITY_CHECK=PASS",
    )
    run_check(
        "reconciled_authority",
        WINDOW / "verify_reconciled_authority.py",
        '"status": "PASS"',
    )
    run_check(
        "older_consolidated_evidence",
        RESEARCH_ROOT
        / "branches/02-event-horizon/lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py",
        "PASS",
    )

    verify_local_manifest()
    print("LIN_THEOREM_READINESS_WINDOW=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"LIN_THEOREM_READINESS_WINDOW=FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
