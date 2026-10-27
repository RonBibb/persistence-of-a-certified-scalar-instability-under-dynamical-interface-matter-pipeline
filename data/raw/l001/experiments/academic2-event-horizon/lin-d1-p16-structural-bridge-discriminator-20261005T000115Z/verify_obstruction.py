#!/usr/bin/env python3
"""Read-only discriminator for the sealed D1 and P16 evidence."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import numpy as np


ROOT = Path("/Users/ronbibb/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research")
OUT = Path(__file__).resolve().parent / "RESULT.json"

SOURCES = {
    "d1_evidence_index": (
        ROOT / "branches/02-event-horizon/lin-d1-d2a-theorem-consolidation-20261002T175556Z/EVIDENCE_INDEX.json",
        "5219b74087747188ba6dcf3185a0d99e228cfcc0a0053489a44cfea396796ad5",
    ),
    "d1_isolation": (
        ROOT / "branches/02-event-horizon/lin-d1-fixed-d-continuation-dimension-audit-r1-20261004T150137Z/output/RESULT.json",
        "f7880e846f248633a547723d1f7e82a7fa9f799d20bfd85b0de01ca4d4ca1faa",
    ),
    "direct_join": (
        ROOT / "branches/02-event-horizon/lin-d1-to-cauchy-boundary-jet-assessment-r1-20261004T154600Z/output/RESULT.json",
        "c44bfed0b06db45d076f74be6c2821961c64736d88c4d34d79de30709e2e94d5",
    ),
    "p16_anchors_json": (
        ROOT / "branches/01-horizon-core/boundary-compatibility-20261001T093524Z/preflight/AUTHENTIC_DRIVER_ANCHORS.json",
        "ccbe12800fa774d9a0d059c57d5cd9802849d21cb4b6eafedec8489762285f39",
    ),
    "p16_anchors_npz": (
        ROOT / "branches/01-horizon-core/boundary-compatibility-20261001T093524Z/preflight/AUTHENTIC_DRIVER_ANCHORS.npz",
        "042de167680b524a220dbc8a1fe3fa7b199fccc332dc12432fae28630809c1be",
    ),
    "p16_latest_boundary": (
        ROOT / "branches/01-horizon-core/coupled-boundary-hour-20261004T195819Z/results/SPATIAL_CROSS.json",
        "35bd9b678aae24cd046959b0a568497b1a51c76417e3f82a8110f3c5e064c152",
    ),
    "d1_gh_report": (
        ROOT / "branches/02-event-horizon/lin-d1-gh-well-balance-discriminator-20261004T203750Z/FINAL_REPORT.md",
        "dee11093489890bb7ab2fd6dae900374f6223d40b9d6a9280620a1746d94ed67",
    ),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_decimal_json(path: Path):
    with path.open() as stream:
        return json.load(stream, parse_float=Decimal)


def plain(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


def main() -> None:
    bindings = []
    for role, (path, expected) in SOURCES.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"hash mismatch for {role}: {actual} != {expected}")
        bindings.append({"role": role, "path": str(path), "sha256": actual})

    evidence = load_decimal_json(SOURCES["d1_evidence_index"][0])
    isolation = load_decimal_json(SOURCES["d1_isolation"][0])
    direct = load_decimal_json(SOURCES["direct_join"][0])
    anchors = load_decimal_json(SOURCES["p16_anchors_json"][0])
    boundary = load_decimal_json(SOURCES["p16_latest_boundary"][0])

    d1_params = evidence["model"]["parameters_as_exact_binary64_literals"]
    d1_lambda_b = Decimal(d1_params["lambda_b"])
    p16_lambda_b = anchors["background"]["retuned_bare_tension_b"]
    action_literal_gap = abs(d1_lambda_b - p16_lambda_b)

    d1_D_lo, d1_D_hi = map(Decimal, direct["D1_proper_separation"]["decimal_bounds"])
    p16_D0 = Decimal(direct["P16_original_metadata_separation"]["decimal_bounds"][0])
    p16_background_D = anchors["background"]["proper_separation"]
    gap_to_D0 = d1_D_lo - p16_D0
    gap_to_archived_background = d1_D_lo - p16_background_D
    if gap_to_D0 <= 0 or gap_to_archived_background <= 0:
        raise RuntimeError("proper-length intervals are not disjoint in the expected order")

    with np.load(SOURCES["p16_anchors_npz"][0]) as archive:
        q0 = np.asarray(archive["q0"])
    q0_hash = hashlib.sha256(q0.tobytes(order="C")).hexdigest()
    expected_q0_hash = anchors["arrays"]["q0"]["sha256"]
    if q0_hash != expected_q0_hash:
        raise RuntimeError(f"q0 array hash mismatch: {q0_hash} != {expected_q0_hash}")
    chi = q0[..., 8]
    chi_min = float(np.min(chi))
    chi_max = float(np.max(chi))
    chi_range = chi_max - chi_min
    chi_nonzero_count = int(np.count_nonzero(chi))
    chi_largest_adjacent_change = float(
        max(np.max(np.abs(np.diff(chi, axis=0))), np.max(np.abs(np.diff(chi, axis=1))))
    )
    if not (chi_range > 0 and chi_nonzero_count > 0 and chi_largest_adjacent_change > 0):
        raise RuntimeError("P16 chi is not certified nonconstant by the bound array")

    pass_count = int(direct["technical_gates"]["P16_full_declared_wall_jet_pass_count"])
    comparison_count = int(direct["technical_gates"]["P16_full_declared_wall_jet_comparison_count"])
    if (pass_count, comparison_count) != (32, 72):
        raise RuntimeError("the preserved direct-comparison count changed")

    primary_det = list(map(Decimal, isolation["primary"]["jacobian_determinant_from_chain_rule"]["decimal_bounds"]))
    independent_det = list(map(Decimal, isolation["independent"]["jacobian_determinant_from_chain_rule"]["decimal_bounds"]))
    if primary_det[0] <= 0 or independent_det[0] <= 0:
        raise RuntimeError("D1 isolation determinant no longer excludes zero")
    d2a_lower_bound = Decimal(evidence["d2a_exclusion"]["uniform_positive_route_residual_vector_linf_lower_bound"].split("/")[0]) / Decimal(evidence["d2a_exclusion"]["uniform_positive_route_residual_vector_linf_lower_bound"].split("/")[1])

    wall_gate = Decimal("1e-8")
    lower_wall = Decimal(boundary["endpoints"][0]["raw_position_wall_max"])
    upper_wall = Decimal(boundary["endpoints"][1]["raw_position_wall_max"])
    if boundary["global_initial_data_obtained"] or lower_wall <= wall_gate or upper_wall <= wall_gate:
        raise RuntimeError("latest P16 endpoint/global status differs from the bound result")

    gh_text = SOURCES["d1_gh_report"][0].read_text()
    gh_pending = "RAW_GH_TWO_LEVEL_GATE_PENDING" in gh_text
    if not gh_pending:
        raise RuntimeError("D1 raw-GH qualification not found")

    result = {
        "schema": "lin-d1-p16-structural-bridge-discriminator-v1",
        "status": "COMPLETE",
        "classification": "NO_INVARIANT_PRESERVING_JOIN_FOR_EXISTING_D1_AND_P16_LINEAGES",
        "bindings": bindings,
        "fixed_evidence": {
            "direct_wall_jet_checks": {"passed": pass_count, "total": comparison_count},
            "action_literal": {
                "D1_lambda_b": str(d1_lambda_b),
                "P16_lambda_b": str(p16_lambda_b),
                "absolute_gap": str(action_literal_gap),
                "exact_same_action_literal": action_literal_gap == 0,
            },
            "proper_wall_distance": {
                "D1_interval": [str(d1_D_lo), str(d1_D_hi)],
                "P16_line_D0": str(p16_D0),
                "P16_archived_background_value": str(p16_background_D),
                "minimum_gap_to_D0": str(gap_to_D0),
                "minimum_gap_to_archived_background": str(gap_to_archived_background),
                "disjoint": True,
            },
            "collapse_scalar": {
                "D1": "identically zero by the certified reduced model",
                "P16_q0_sha256": q0_hash,
                "P16_minimum": chi_min,
                "P16_maximum": chi_max,
                "P16_range": chi_range,
                "P16_nonzero_node_count": chi_nonzero_count,
                "P16_largest_adjacent_change": chi_largest_adjacent_change,
                "P16_nonconstant": True,
            },
            "static_family": {
                "D1_isolation_primary_determinant": [str(x) for x in primary_det],
                "D1_isolation_independent_determinant": [str(x) for x in independent_det],
                "fixed_D0_residual_linf_lower_bound": str(d2a_lower_bound),
                "scope": "fixed D1 reduced action, positive curvature, declared launch domain",
            },
            "endpoint_readiness": {
                "P16_lower_position_wall_residual": str(lower_wall),
                "P16_upper_position_wall_residual": str(upper_wall),
                "gate": str(wall_gate),
                "P16_global_initial_data_obtained": False,
                "D1_equilibrium_preserving_formulation_observed": True,
                "D1_raw_GH_two_level_gate_pending": gh_pending,
            },
        },
        "transformation_audit": {
            "coordinate_reparameterization": "blocked by disjoint invariant proper wall lengths",
            "orientation": "may exchange walls but preserves their proper separation and scalar range",
            "regular_field_normalization": "cannot map a nonconstant P16 scalar field to D1 chi identically zero",
            "gauge_or_source_reference": "can explain source-trace differences but cannot change the physical invariants above",
            "fixed_model_static_continuation": "blocked locally by the nonzero D1 Jacobian determinant and at D0 by the scoped D2A cover",
            "already_derived_complete_solution_family": "absent from the bound evidence",
        },
        "scope": {
            "established": "the two sealed endpoints are not equivalent and no already-derived complete family joins them",
            "not_established": "universal impossibility of a new dynamical family or a new D1-based collapse construction",
        },
        "minimum_lawful_successor": {
            "name": "D1-fixed-action second-order collapse-scalar tangent test",
            "reason": "for a canonical scalar about chi=0, its stress first enters at quadratic order in a declared amplitude",
            "requirements": [
                "keep the exact D1 action, walls, chart, gates, and proper-distance definition fixed",
                "declare one small amplitude epsilon and one transported normalized scalar shape before evaluation",
                "solve the order-epsilon-squared Hamiltonian, momentum, wall, axis, gauge, and outer-boundary system including the radion response",
                "test the linearized/second-order boundary operator and its cokernel independently",
                "if solvable, validate a small nonzero-epsilon family; do not call it P16 or an ancestry bridge",
            ],
        },
    }
    OUT.write_text(json.dumps(plain(result), indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"], "result": str(OUT)}, sort_keys=True))


if __name__ == "__main__":
    main()

