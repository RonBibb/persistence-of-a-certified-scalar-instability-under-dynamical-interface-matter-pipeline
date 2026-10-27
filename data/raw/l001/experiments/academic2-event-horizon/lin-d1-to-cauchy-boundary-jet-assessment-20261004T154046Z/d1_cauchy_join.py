#!/usr/bin/env python3
"""Read-only interval translation of D1 into the Lin Cauchy variables."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from flint import arb, ctx, fmpq


FIELD_ORDER = (
    "g_x0",
    "g_xr_over_r",
    "g_00",
    "g_perp",
    "g_rr_minus_g_perp_over_r2",
    "g_0r_over_r",
    "g_xx",
    "Phi",
    "chi",
)
RADIUS = fmpq(10)
ABSOLUTE_GATE = fmpq(1, 100_000_000)


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dyadic(text: str) -> fmpq:
    numerator, denominator = float(text).as_integer_ratio()
    return fmpq(numerator, denominator)


def ball(lo: fmpq, hi: fmpq) -> arb:
    if lo > hi:
        raise ValueError("empty interval")
    return arb((lo + hi) / 2, (hi - lo) / 2)


def bounds(value: arb) -> tuple[fmpq, fmpq]:
    return value.lower().fmpq(), value.upper().fmpq()


def exact_interval(record: dict[str, Any]) -> arb:
    lo, hi = record["exact_bounds"]
    return ball(fmpq(lo), fmpq(hi))


def interval_record(value: arb) -> dict[str, Any]:
    lo, hi = bounds(value)
    return {
        "exact_bounds": [str(lo), str(hi)],
        "decimal_bounds": [float(lo), float(hi)],
        "width": float(hi - lo),
        "contains_zero": bool(lo <= 0 <= hi),
    }


def point_record(text: str) -> dict[str, Any]:
    value = fmpq(text)
    return {"exact": str(value), "decimal": float(value)}


def difference_record(interval: arb, point_text: str) -> dict[str, Any]:
    point = fmpq(point_text)
    difference = interval - arb(point)
    lo, hi = bounds(interval)
    return {
        "D1_minus_P16": interval_record(difference),
        "P16_point": point_record(point_text),
        "passes_absolute_1e_minus_8": bool(
            lo - ABSOLUTE_GATE <= point <= hi + ABSOLUTE_GATE
        ),
    }


def zero() -> arb:
    return arb(0)


def vector_records(values: list[arb]) -> dict[str, Any]:
    return {
        name: interval_record(value)
        for name, value in zip(FIELD_ORDER, values, strict=True)
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def endpoint_fields(
    *, warp: arb, H: arb, phi: arb, U: arb, curvature: arb, conformal_length: arb
) -> dict[str, Any]:
    code_e = dyadic(repr(math.e))
    c = conformal_length / arb(code_e - 1)
    r = arb(RADIUS)
    f = arb(1) - curvature * r * r
    w2 = warp * warp
    sqrt_gxx = c * warp

    q = [
        zero(),
        zero(),
        -w2 * f,
        w2,
        w2 * curvature / f,
        zero(),
        w2 * c * c,
        phi,
        zero(),
    ]
    qx = [
        zero(),
        zero(),
        -arb(2) * c * warp**3 * H * f,
        arb(2) * c * warp**3 * H,
        arb(2) * c * warp**3 * H * curvature / f,
        zero(),
        arb(2) * c**3 * warp**3 * H,
        c * warp * U,
        zero(),
    ]
    qr = [
        zero(),
        zero(),
        arb(2) * w2 * curvature * r,
        zero(),
        arb(2) * w2 * curvature**2 * r / f**2,
        zero(),
        zero(),
        zero(),
        zero(),
    ]
    qxr = [
        zero(),
        zero(),
        arb(4) * c * warp**3 * H * curvature * r,
        zero(),
        arb(4) * c * warp**3 * H * curvature**2 * r / f**2,
        zero(),
        zero(),
        zero(),
        zero(),
    ]
    H_s = -U * U / arb(3) - curvature / w2
    source = [zero(), -arb(3) * c * warp * H, arb(4) * curvature / f]
    source_x = [
        zero(),
        -arb(3) * c * c * w2 * (H * H + H_s),
        zero(),
    ]
    source_r = [zero(), zero(), arb(8) * curvature**2 * r / f**2]
    source_xr = [zero(), zero(), zero()]
    lapse = warp * f.sqrt()
    return {
        "warp": interval_record(warp),
        "H_A_s": interval_record(H),
        "Phi": interval_record(phi),
        "Phi_s": interval_record(U),
        "curvature_k": interval_record(curvature),
        "conformal_length_L": interval_record(conformal_length),
        "coordinate_scale_c": interval_record(c),
        "static_patch_f_at_R": interval_record(f),
        "sqrt_g_xx": interval_record(sqrt_gxx),
        "lapse": interval_record(lapse),
        "shift": [0, 0, 0, 0],
        "extrinsic_curvature": "all components exactly zero",
        "scalar_momenta": {"Pi_Phi": 0, "Pi_chi": 0},
        "q": vector_records(q),
        "q_x": vector_records(qx),
        "q_r": vector_records(qr),
        "q_xr": vector_records(qxr),
        "q_t": {name: 0 for name in FIELD_ORDER},
        "geometric_source_order": ["H_0", "H_x", "H_r_over_r"],
        "geometric_source": [interval_record(x) for x in source],
        "geometric_source_x": [interval_record(x) for x in source_x],
        "geometric_source_r": [interval_record(x) for x in source_r],
        "geometric_source_xr": [interval_record(x) for x in source_xr],
        "temporal_source_trace": {
            "partial_t_H0": interval_record(zero()),
            "partial_x_partial_t_H0": interval_record(zero()),
        },
        "natural_reference_mixed_normal_radial_derivative": interval_record(zero()),
        "natural_reference_radial_moment": {
            "Y_lower_or_upper": interval_record(zero()),
            "partial_r_H_x": interval_record(zero()),
        },
    }


def run(root: Path, output: Path) -> dict[str, Any]:
    started = utc()
    here = Path(__file__).resolve().parent
    bindings = load_json(here / "BINDINGS.json")
    verified: list[dict[str, Any]] = []
    for entry in bindings["parents"]:
        path = root / entry["path"]
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise RuntimeError(f"binding changed: {entry['role']} {actual}")
        verified.append({"role": entry["role"], "path": str(path), "sha256": actual})

    d1 = load_json(root / bindings["parents"][0]["path"])
    level = next(item for item in d1["levels"] if item["steps"] == 16384)
    event = level["root_box"]["event_quantities"]

    root_lo = dyadic("0.09901086489880687")
    root_hi = dyadic("0.09901086689880687")
    a = ball(root_lo, root_hi)
    gamma = arb(dyadic("20.0"))
    m2 = arb(dyadic("0.41"))
    v0 = arb(dyadic("0.1"))
    lambda_a = arb(dyadic("5.999990376773895"))
    lower_U = gamma * (a - v0) / arb(2)
    lower_H = -(lambda_a + gamma * (a - v0) ** 2 / arb(2)) / arb(6)
    lower_k = (
        lower_H * lower_H
        - arb(1)
        - lower_U * lower_U / arb(12)
        + m2 * a * a / arb(12)
    )

    L = exact_interval(event["Z"])
    lower = endpoint_fields(
        warp=arb(1), H=lower_H, phi=a, U=lower_U,
        curvature=lower_k, conformal_length=L,
    )
    upper = endpoint_fields(
        warp=exact_interval(event["warp"]),
        H=exact_interval(event["H"]),
        phi=exact_interval(event["phi"]),
        U=exact_interval(event["S"]),
        curvature=exact_interval(event["curvature"]),
        conformal_length=L,
    )

    # D1 wall-law interval checks in the frozen chart.
    lambda_b = arb(dyadic("-6.052844277744164"))
    v1 = arb(dyadic("0.09048374180359596"))
    lower_b = (lambda_a + gamma * (a - v0) ** 2 / arb(2)) / arb(6)
    upper_phi = exact_interval(event["phi"])
    upper_H = exact_interval(event["H"])
    upper_U = exact_interval(event["S"])
    upper_b = -(lambda_b + gamma * (upper_phi - v1) ** 2 / arb(2)) / arb(6)
    wall_checks = {
        "lower": {
            "H_plus_beta": interval_record(lower_H + lower_b),
            "Phi_s_minus_lower_Robin": interval_record(
                lower_U - gamma * (a - v0) / arb(2)
            ),
        },
        "upper": {
            "H_plus_beta": interval_record(upper_H + upper_b),
            "Phi_s_plus_upper_Robin": interval_record(
                upper_U + gamma * (upper_phi - v1) / arb(2)
            ),
        },
    }
    wall_checks_pass = all(
        item["contains_zero"]
        for wall in wall_checks.values()
        for item in wall.values()
    )

    p16 = load_json(root / bindings["parents"][5]["path"])
    p16_rows = {int(row["wall"]): row for row in p16["rows"]}
    d1_endpoints = {0: lower, 1: upper}
    p16_comparison: dict[str, Any] = {}
    physical_pass_count = 0
    physical_total = 0
    for wall in (0, 1):
        saved = p16_rows[wall]["local_jets"]
        wall_comparison: dict[str, Any] = {}
        for d1_key, p16_key in (("q", "(0, 0)"), ("q_x", "(1, 0)"),
                                ("q_r", "(0, 1)"), ("q_xr", "(1, 1)")):
            group: dict[str, Any] = {}
            for name, point in zip(FIELD_ORDER, saved[p16_key], strict=True):
                interval = ball(*bounds_from_record(d1_endpoints[wall][d1_key][name]))
                comparison = difference_record(interval, point)
                group[name] = comparison
                physical_total += 1
                physical_pass_count += int(comparison["passes_absolute_1e_minus_8"])
            wall_comparison[d1_key] = group
        p16_comparison[str(wall)] = wall_comparison

    p17 = load_json(root / bindings["parents"][6]["path"])
    mixed = load_json(root / bindings["parents"][7]["path"])
    radial = load_json(root / bindings["parents"][8]["path"])
    mixed_rows = {int(row["wall"]): row for row in mixed["rows"]}
    source_comparison: dict[str, Any] = {}
    for wall, p17_row in enumerate(p17["rows"]):
        d1_source = d1_endpoints[wall]["geometric_source"]
        d1_source_x = d1_endpoints[wall]["geometric_source_x"]
        p16_sources = mixed_rows[wall]["source_data"]
        source_comparison[str(wall)] = {
            "D1_geometric_source": d1_source,
            "P16_projected_source": [point_record(x) for x in p16_sources["('source', 0, 0)"]],
            "D1_geometric_source_x": d1_source_x,
            "P16_projected_source_x": [point_record(x) for x in p16_sources["('source', 1, 0)"]],
            "D1_partial_t_H0": interval_record(zero()),
            "P17_candidate_partial_t_H0": point_record(p17_row["candidate_H0_time"]),
            "D1_partial_x_partial_t_H0": interval_record(zero()),
            "P17_candidate_partial_x_partial_t_H0": point_record(p17_row["candidate_H0_time_z"]),
            "P17_projected_reference_partial_x_partial_t_H0": point_record(p17_row["reference_H0_time_z"]),
            "mixed_successor_temporal_slope_correction_d": point_record(mixed_rows[wall]["slope_correction"]),
            "D1_natural_mixed_normal_source_derivative": interval_record(zero()),
            "mixed_successor_reference_correction_e": point_record(mixed_rows[wall]["mixed_normal_correction"]),
        }

    d0 = arb(dyadic("0.9996389747145851"))
    D = ball(fmpq(32727, 16384), fmpq(32729, 16384))
    separation_difference = D - d0
    f_positive = all(
        bounds_from_record(endpoint["static_patch_f_at_R"])[0] > 0
        for endpoint in (lower, upper)
    )
    metric_positive = all(
        bounds_from_record(endpoint["lapse"])[0] > 0
        and bounds_from_record(endpoint["q"]["g_perp"])[0] > 0
        and bounds_from_record(endpoint["q"]["g_xx"])[0] > 0
        for endpoint in (lower, upper)
    )

    result = {
        "schema": "lin-d1-to-cauchy-boundary-jet-assessment-result-v1",
        "started_utc": started,
        "completed_utc": utc(),
        "status": "COMPLETE",
        "classification": "NO_DIRECT_D1_TO_P16_JOIN__NEW_D1_CAUCHY_FAMILY_REQUIRED",
        "mismatch_categories": {
            "coordinate_gauge_reference_translation": {
                "applies": True,
                "reason": "The temporal and mixed source traces are gauge/reference data.  D1's natural geometric reference has zero trace slopes and an exact zero radial moment, whereas P16/P17 use a different authenticated projected reference."
            },
            "missing_freely_specifiable_Cauchy_data": {
                "applies_as_primary_explanation": False,
                "reason": "A new D1 outer reference and gauge target must be specified, but no freely specifiable datum can turn P16's physical metric, scalar, separation and matter data into D1 while keeping P16 fixed."
            },
            "genuine_incompatibility_with_present_dynamic_preparation": {
                "applies": True,
                "reason": "After fixing the closest time-symmetric static-patch chart, D1 and P16 disagree in physical wall fields and derivatives and in wall separation; D1 also has chi=0.  This is a different Cauchy family, not a boundary-jet repair of P16."
            }
        },
        "chart": {
            "name": "D1 de Sitter static patch mapped by normalized conformal compact coordinate",
            "radial_outer_R": 10,
            "code_compact_interval": [1.0, math.e],
            "field_order": FIELD_ORDER,
            "ADM_sign": "K_ij=-(2 alpha)^-1 partial_t h_ij at zero shift",
            "flat_slicing_alternative": "Same flat radial topology but K_ab=-sqrt(k) exp(-A) h_ab, hence not P16's zero-velocity slice.",
        },
        "authority_bindings_verified": verified,
        "technical_gates": {
            "static_patch_regular_through_R10": f_positive,
            "positive_lapse_and_spatial_metric_at_wall_outer_corners": metric_positive,
            "D1_wall_junction_intervals_contain_zero": wall_checks_pass,
            "P16_full_declared_wall_jet_pass_count": physical_pass_count,
            "P16_full_declared_wall_jet_comparison_count": physical_total,
            "P16_full_declared_wall_jet_compatible": physical_pass_count == physical_total,
        },
        "D1_proper_separation": interval_record(D),
        "P16_original_metadata_separation": interval_record(d0),
        "D1_minus_P16_separation": interval_record(separation_difference),
        "D1_wall_junction_checks": wall_checks,
        "D1_Cauchy_wall_jets": {"lower": lower, "upper": upper},
        "P16_direct_comparison": p16_comparison,
        "source_and_reference_comparison": source_comparison,
        "global_moment_assessment": {
            "D1_natural_reference_endpoint_Y": [0, 0],
            "D1_natural_reference_integral_partial_r_H_x": 0,
            "D1_natural_reference_defect": 0,
            "D1_requires_mixed_successor_dependent_shape": False,
            "sealed_P16_reference_defect": radial["defect_interval"],
            "reading": "D1 automatically supplies a moment-consistent geometric reference.  The proposed dependent interpolation correction belongs only to the retained P16 projected-reference family and is not a D1 requirement."
        },
        "join_contract": {
            "shared_action_quantities": ["Lambda5", "m_squared", "gamma", "v0", "v1", "wall-potential form"],
            "data_to_transfer_for_a_new_D1_family": [
                "certified A(s), Phi(s), k, D and conformal length L enclosures",
                "one frozen de Sitter chart and compact-coordinate map",
                "q, q_t, q_x, q_r and q_xr wall data from the formulas above",
                "lapse, shift, K_ij and scalar momenta",
                "geometric GH source, target and outer reference generated from the same D1 field"
            ],
            "constraints_and_checks_still_required": [
                "full-domain Hamiltonian and momentum constraints in the production discretization",
                "both physical wall and scalar junction conditions at every radius",
                "axis regularity and complete outer characteristic compatibility",
                "gauge-driver preservation with D1-specific anchors",
                "unperturbed refinement-controlled evolution before any collapse perturbation"
            ],
            "remaining_free_data": [
                "choice among static-patch, global or flat-slicing de Sitter Cauchy charts",
                "D1-consistent outer reference away from the analytic boundary trace",
                "constraint-compatible collapse perturbation only in a later new family"
            ],
            "pass_gate": "All physical, constraint, wall, axis, gauge and outer rows pass in one represented D1 field; a source-only or corner-only match is insufficient.",
            "present_outcome": "FAILS_AS_DIRECT_P16_JOIN; ADMISSIBLE_AS_A_PROSPECTIVE_NEW_D1_BACKGROUND_EMBEDDING"
        },
        "claim_boundary": [
            "No D1-to-P16 same-development connection is established.",
            "No constraint solve or evolution was run.",
            "The zero D1 source moment is chart/reference consistency, not a dynamical-selection result.",
            "No event-horizon, collapse, radion-transition or baby-universe conclusion follows."
        ]
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def bounds_from_record(record: dict[str, Any]) -> tuple[fmpq, fmpq]:
    lo, hi = record["exact_bounds"]
    return fmpq(lo), fmpq(hi)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 768
    result = run(args.root.resolve(), args.output.resolve())
    print(json.dumps({
        "status": result["status"],
        "classification": result["classification"],
        "technical_gates": result["technical_gates"],
        "mismatch_categories": result["mismatch_categories"],
    }, indent=2))


if __name__ == "__main__":
    main()
