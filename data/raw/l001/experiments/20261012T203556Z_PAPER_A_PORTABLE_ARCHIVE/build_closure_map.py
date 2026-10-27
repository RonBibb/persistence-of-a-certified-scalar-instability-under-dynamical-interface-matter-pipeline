#!/usr/bin/env python3
"""Inventory selected paper claims against the two staged replay closures."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
PRIOR = SOURCE / "20261012T192834Z_PAPER_A_STATIC_CONTRIBUTION" / "CLAIM_EVIDENCE.json"

STATUS = {
    "A1": ("REDUCTION_TEXT_HASH_BOUND", "Reduction lemma is staged and hash-checked; derivation is not symbolically reconstructed. Exact-model provenance index is available as documentary evidence only."),
    "A2": ("PARTIAL_SAVED_PROOF_RECONSTRUCTION", "Saved D1 Newton inclusion and refinement nesting are reconstructed. Independent ODE and 726-box global uniqueness are authority records only; no flow or global-cover proof reconstruction."),
    "A3": ("AUTHORITY_RECORD_REPLAY_ONLY", "Saved determinant lower bounds and audit status are checked by the authority verifier. Determinant chain-rule calculation is not reconstructed."),
    "A4": ("SAVED_EXACT_COVER_RECONSTRUCTED", "693-box adjacency, classifications and uniform residual-vector floor are reconstructed from saved exact endpoints; 86 checkpoint addresses are reconstructed. ODE enclosures are not regenerated."),
    "A5": ("DOCUMENTARY_ONLY_NOT_REPLAYED", "Selected tension result, integrity record and terminal are available offline. Recursive producer inputs, failed predecessors and proof reconstruction remain outside this archive."),
    "A6": ("DOCUMENTARY_ONLY_NOT_REPLAYED", "Selected central-mode acceptance, producer result, audit and report are available offline. Recursive spectral closure and proof reconstruction remain outside this archive."),
    "A7": ("INTERPRETIVE_CLAIM_NOT_REPLAYED", "Interpretive significance is not a verifier claim; integrated statement and saved novelty text are available offline. Conventional literature review remains pending."),
}

def main():
    prior = json.loads(PRIOR.read_text())
    manifest_paths = [HERE / (layer + "_ARTIFACT_MANIFEST.json") for layer in ("AUTHORITY", "CONSOLIDATION", "DOCUMENTARY")]
    staged = {}
    replay_inputs = set()
    for path in manifest_paths:
        for record in json.loads(path.read_text())["files"]:
            key = record["origin_relative_to_experiments"]
            if not path.name.startswith("DOCUMENTARY"):
                replay_inputs.add(key)
            if key in staged and staged[key]["sha256"] != record["sha256"]:
                raise ValueError("conflicting layer manifests")
            staged[key] = record
    sources = {}
    for key, record in prior["sources"].items():
        relative = Path(record["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("unsafe source")
        source = SOURCE / relative
        if any(p.is_symlink() for p in [source, *source.parents]):
            raise ValueError("source symlink")
        source.resolve().relative_to(SOURCE.resolve())
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        copied = staged.get(str(relative))
        sources[key] = {"canonical_relative_to_experiments": str(relative), "canonical_sha256_at_inventory": digest, "staged": copied is not None, "read_by_executed_proof_layer": str(relative) in replay_inputs, "archive_path": copied["archive_path"] if copied else None, "staged_sha256_matches_source": copied["sha256"] == digest if copied else None, "role": record["role"]}
    claims = []
    for claim in prior["claims"]:
        status, meaning = STATUS[claim["id"]]
        claims.append({"id": claim["id"], "selected_claim": claim["claim"], "status_in_this_archive": status, "executed_scope": meaning, "evidence_keys": claim["evidence"], "staged_evidence_keys": [k for k in claim["evidence"] if sources[k]["staged"]], "unstaged_evidence_keys": [k for k in claim["evidence"] if not sources[k]["staged"]], "depends_on": claim["depends_on"]})
    result = {
        "schema": "paper-a-selected-claim-closure/v1",
        "scope": "Metadata closure inventory only; no additional scientific verifier or producer execution",
        "prior_claim_map_relative_to_experiments": str(PRIOR.relative_to(SOURCE)),
        "prior_claim_map_sha256": hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        "claim_count": len(claims), "sources": sources, "claims": claims,
        "archive_union_file_count": len(staged),
        "archive_union_bytes": sum(r["bytes"] for r in staged.values()),
        "full_selected_paper_proof_archive_complete": False,
        "linux_replay_executed": False,
        "numerical_producer_executed": False,
        "remaining_dependencies": [
            "Exact-model provenance index is staged; its recursively bound lower-tension constructor/N65 inputs remain to be packaged",
            "Independent D1 terminal and audit are staged; Arb producer, frozen parameters, failed r0 and accepted r1 records and pinned Python/python-flint/FLINT-Arb environment remain to be packaged",
            "Global first-event result and audit are staged; producer import closure and executable exact 726-box audit remain to be packaged and reviewed",
            "Isolation result and audit are staged; producer/audit import closure and exact chain-rule determinant reconstruction remain to be packaged and reviewed",
            "D2A saved-cover closure is replayed; full producer import/input closure and independent integration replication remain separate tasks if that assurance is sought",
            "Tension result/integrity/terminal are staged; recursive bound inputs, original 4096-step failure, historical raw failure and producer/audit environment remain to be packaged",
            "Central-mode final acceptance, producer result, independent audit and report are staged; physical equation derivation and recursively bound imported code/checkpoints remain to be packaged",
            "Upgraded theorem and saved novelty text are staged; conventional citation verification and bibliography integration remain",
            "Fresh approved macOS and Linux producer-replay plans with pinned environments; Linux execution excluded in this round",
            "Integrated manuscript, supplement, figures and manuscript-level review",
        ],
    }
    (HERE / "CLAIM_CLOSURE_MAP.json").write_text(json.dumps(result, indent=2) + "\n")
    union = {"schema": "paper-a-archive-union/v1", "files": sorted(staged.values(), key=lambda r: r["archive_path"]), "file_count": len(staged), "total_bytes": sum(r["bytes"] for r in staged.values())}
    (HERE / "ARCHIVE_UNION_MANIFEST.json").write_text(json.dumps(union, indent=2) + "\n")
    print(json.dumps({"claims": len(claims), "archive_files": len(staged), "archive_bytes": union["total_bytes"]}))

if __name__ == "__main__":
    main()
