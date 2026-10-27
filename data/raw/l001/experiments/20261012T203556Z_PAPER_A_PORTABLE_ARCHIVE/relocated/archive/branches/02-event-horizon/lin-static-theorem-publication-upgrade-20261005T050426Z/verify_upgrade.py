#!/usr/bin/env python3
"""Read-only verification of the static-theorem publication upgrade."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(relative: str):
    return json.loads((ROOT / relative).read_text())


bindings = json.loads((HERE / "BINDINGS.json").read_text())
checks: dict[str, bool] = {}

for item in bindings["files"]:
    path = ROOT / item["path"]
    checks[f"hash:{item['path']}"] = path.is_file() and sha256(path) == item["sha256"]

readiness = load(
    "branches/02-event-horizon/lin-theorem-causal-readiness-window-20261003T205314Z/RESULT.json"
)
checks["prior_theorem_packet_ready"] = (
    readiness.get("classification")
    == "NARROW_STATIC_THEOREM_DRAFT_READY__CAUSAL_EXPERIMENT_NOT_ADMITTED"
)

replay_terminal = load(
    "branches/02-event-horizon/lin-d1-independent-ode-replay-20261002T225837Z/TERMINAL.json"
)
replay_audit = load(
    "branches/02-event-horizon/lin-d1-independent-ode-replay-20261002T225837Z/POSTRUN_AUDIT.json"
)
checks["independent_d1_replay"] = (
    replay_terminal.get("status") == "SEALED_COMPLETE"
    and replay_terminal.get("classification")
    == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS"
    and replay_audit.get("status") == "PASS"
    and all(replay_audit.get("checks", {}).values())
)

global_result = load(
    "branches/02-event-horizon/lin-d1-global-first-event-uniqueness-r1-20261004T134600Z/output/RESULT.json"
)
global_audit = load(
    "branches/02-event-horizon/lin-d1-global-first-event-uniqueness-r1-20261004T134600Z/output/POSTRUN_AUDIT.json"
)
checks["global_first_event_uniqueness"] = (
    global_result.get("status") == "COMPLETE"
    and global_result.get("classification")
    == "GLOBAL_FIRST_EVENT_SIMULTANEOUS_WALL_ROOT_UNIQUE_ON_DECLARED_POSITIVE_CURVATURE_LAUNCH_INTERVAL"
    and global_result.get("coverage_audit", {}).get("exact_contiguous_cover") is True
    and global_result.get("coverage_audit", {}).get("certified_root_box_count") == 1
    and global_result.get("classification_counts", {}).get("FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED") == 706
    and global_result.get("classification_counts", {}).get("NEGATIVE_CURVATURE_EXCLUDED") == 19
    and global_audit.get("status") == "VERIFIED"
    and all(global_audit.get("checks", {}).values())
)

isolation = load(
    "branches/02-event-horizon/lin-d1-fixed-d-continuation-dimension-audit-r1-20261004T150137Z/output/RESULT.json"
)
isolation_audit = load(
    "branches/02-event-horizon/lin-d1-fixed-d-continuation-dimension-audit-r1-20261004T150137Z/output/POSTRUN_AUDIT.json"
)
checks["isolated_root"] = (
    isolation.get("status") == "COMPLETE"
    and isolation.get("classification")
    == "CERTIFIED_ISOLATED_D1_ROOT_NO_NONTRIVIAL_FIXED_D_CONTINUATION"
    and isolation["primary"]["jacobian_determinant_from_chain_rule"]["decimal_bounds"][0] > 0
    and isolation["independent"]["jacobian_determinant_from_chain_rule"]["decimal_bounds"][0] > 0
    and isolation_audit.get("status") == "VERIFIED"
    and all(isolation_audit.get("checks", {}).values())
)

d2a = load(
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json"
)
d2a_audit = load(
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/POSTRUN_AUDIT.json"
)
checks["fixed_separation_exclusion"] = (
    d2a.get("status") == "COMPLETE"
    and d2a.get("classification")
    == "FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE"
    and d2a.get("coverage_audit", {}).get("exact_contiguous_cover") is True
    and sum(d2a.get("classification_counts", {}).values()) == 693
    and d2a_audit.get("status") == "PASS"
)

gh = load(
    "branches/02-event-horizon/lin-d1-raw-gh-dynamical-qualification-20261005T000023Z/output/RESULT.json"
)
gh_audit = load(
    "branches/02-event-horizon/lin-d1-raw-gh-dynamical-qualification-20261005T000023Z/output/INDEPENDENT_AUDIT.json"
)
roundoff = load(
    "branches/02-event-horizon/lin-d1-raw-gh-dynamical-qualification-r2-roundoff-audit-20261005T004308Z/output/RESULT.json"
)
roundoff_audit = load(
    "branches/02-event-horizon/lin-d1-raw-gh-dynamical-qualification-r2-roundoff-audit-20261005T004308Z/output/INDEPENDENT_AUDIT.json"
)
checks["finite_resolution_gh_support"] = (
    gh.get("status") == "COMPLETE"
    and gh.get("raw_gh_extension", {}).get("passed") is True
    and all(gh.get("raw_gh_extension", {}).get("gates", {}).values())
    and gh_audit.get("classification") == "VERIFIED"
    and all(gh_audit.get("checks", {}).values())
    and roundoff.get("classification")
    == "D1_SCALAR_RESPONSE_PASS__FROZEN_AMPLITUDE_GATE_FALSE_FAILURE"
    and roundoff.get("calculation", {}).get("passed") is True
    and roundoff_audit.get("classification") == "VERIFIED"
    and all(roundoff_audit.get("checks", {}).values())
)

result = {
    "schema": "lin-static-theorem-publication-upgrade-verification-v1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks_passed": sum(checks.values()),
    "checks_total": len(checks),
    "checks": checks,
    "classification": (
        "STATIC_THEOREM_AUTHORITY_CHAIN_VERIFIED"
        if all(checks.values())
        else "STATIC_THEOREM_AUTHORITY_CHAIN_NOT_VERIFIED"
    ),
    "claim_boundary": (
        "Reduced static family and finite-resolution GH support only; no stability, "
        "dynamical selection, collapse, MOTS, event horizon, or child-universe inference."
    ),
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["status"] == "PASS" else 1)
