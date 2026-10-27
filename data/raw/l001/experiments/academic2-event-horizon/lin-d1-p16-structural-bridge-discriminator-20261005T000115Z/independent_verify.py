#!/usr/bin/env python3
"""Independent post-run audit for the bounded D1--P16 discriminator."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "RESULT.json"
AUDIT = ROOT / "POSTRUN_AUDIT.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


result = json.loads(RESULT.read_text(encoding="utf-8"))

binding_checks = []
for binding in result["bindings"]:
    path = Path(binding["path"])
    observed = sha256(path)
    binding_checks.append(
        {
            "role": binding["role"],
            "expected": binding["sha256"],
            "observed": observed,
            "pass": observed == binding["sha256"],
        }
    )

fixed = result["fixed_evidence"]
d1_lo, d1_hi = map(Decimal, fixed["proper_wall_distance"]["D1_interval"])
p16_d0 = Decimal(fixed["proper_wall_distance"]["P16_line_D0"])
p16_bg = Decimal(fixed["proper_wall_distance"]["P16_archived_background_value"])
lambda_gap = abs(
    Decimal(fixed["action_literal"]["D1_lambda_b"])
    - Decimal(fixed["action_literal"]["P16_lambda_b"])
)

npz_path = Path(next(b["path"] for b in result["bindings"] if b["role"] == "p16_anchors_npz"))
with np.load(npz_path) as arrays:
    q0 = arrays["q0"]
chi = q0[..., 8]

independent_checks = {
    "all_parent_hashes_match": all(item["pass"] for item in binding_checks),
    "action_literals_are_distinct": lambda_gap == Decimal("6.38E-13") and lambda_gap != 0,
    "proper_length_intervals_are_disjoint": p16_d0 < d1_lo and p16_bg < d1_lo,
    "collapse_scalar_is_nonconstant": float(np.ptp(chi)) > 0.0,
    "collapse_scalar_is_nonzero": int(np.count_nonzero(chi)) == chi.size,
    "direct_join_is_incomplete": fixed["direct_wall_jet_checks"] == {"passed": 32, "total": 72},
    "d1_isolation_determinants_exclude_zero": (
        Decimal(fixed["static_family"]["D1_isolation_primary_determinant"][0]) > 0
        and Decimal(fixed["static_family"]["D1_isolation_independent_determinant"][0]) > 0
    ),
    "p16_endpoint_is_not_global_initial_data": not fixed["endpoint_readiness"]["P16_global_initial_data_obtained"],
    "scope_does_not_claim_universal_no_go": "universal impossibility" in result["scope"]["not_established"],
}

status = "VERIFIED" if all(independent_checks.values()) else "FAILED"
audit = {
    "schema": "lin-d1-p16-structural-bridge-postrun-audit-v1",
    "status": status,
    "result_sha256": sha256(RESULT),
    "binding_checks": binding_checks,
    "independent_checks": independent_checks,
}
AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": status, "audit": str(AUDIT)}))
raise SystemExit(0 if status == "VERIFIED" else 1)
