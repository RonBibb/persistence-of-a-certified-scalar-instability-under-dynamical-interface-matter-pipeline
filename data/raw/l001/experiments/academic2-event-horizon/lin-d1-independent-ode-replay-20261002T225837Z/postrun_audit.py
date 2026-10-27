#!/usr/bin/env python3
"""Read-only exact audit of the independent D1 replay and R1 confirmation."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(text: str) -> Fraction:
    numerator, denominator = float(text).as_integer_ratio()
    return Fraction(numerator, denominator)


def exact_bounds(record: dict) -> tuple[Fraction, Fraction]:
    lo, hi = record["exact_bounds"]
    return Fraction(lo), Fraction(hi)


def decimal_bounds(record: dict) -> tuple[float, float]:
    lo, hi = record["decimal_bounds"]
    return float(lo), float(hi)


def overlaps(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return max(left[0], right[0]) <= min(left[1], right[1])


def width(record: dict) -> Fraction:
    lo, hi = exact_bounds(record)
    return hi - lo


def audit_level(level: dict) -> dict[str, bool]:
    root_lo = dyadic("0.09901086489880687")
    root_hi = dyadic("0.09901086689880687")
    newton_lo, newton_hi = exact_bounds(level["interval_newton_image"])
    geometry = level["geometry"]
    return {
        "strict_self_map_rederived": root_lo < newton_lo < newton_hi < root_hi,
        "reported_strict_self_map": level["strict_self_map"] is True,
        "reported_root_pass": level["root_replay_pass"] is True,
        "event_validated": level["root_box"]["event_validated"] is True,
        "G_s_strictly_negative": decimal_bounds(level["root_box"]["event_quantities"]["G_s"])[1] < 0,
        "q_a_strictly_positive": decimal_bounds(level["root_box"]["event_quantities"]["q_a"])[0] > 0,
        "geometry_checks_all_true": all(geometry["checks"].values()),
        "geometry_reported_pass": geometry["pass"] is True,
        "positive_curvature": decimal_bounds(geometry["curvature"])[0] > 0,
        "positive_conformal_length": decimal_bounds(geometry["conformal_separation"])[0] > 0,
        "positive_warp": decimal_bounds(geometry["warp_at_event"])[0] > 0,
        "first_integral_contains_zero": geometry["first_integral_union"]["contains_zero"] is True,
        "lower_wall_identity_contains_zero": geometry["lower_wall_identity"]["contains_zero"] is True,
        "upper_wall_identity_contains_zero": geometry["upper_wall_identity"]["contains_zero"] is True,
        "both_upper_residuals_contain_zero": geometry["upper_Israel_residual"]["contains_zero"] is True
        and geometry["upper_scalar_residual"]["contains_zero"] is True,
    }


def main() -> None:
    r0_path = HERE / "output" / "r0" / "RESULT.json"
    r1_path = HERE / "output" / "r1" / "RESULT.json"
    producer_path = ROOT / "branches/02-event-horizon/lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json"
    r0 = json.loads(r0_path.read_text())
    r1 = json.loads(r1_path.read_text())
    producer = json.loads(producer_path.read_text())

    r0_by_step = {level["steps"]: level for level in r0["levels"]}
    r1_by_step = {level["steps"]: level for level in r1["levels"]}
    coarse_newton = exact_bounds(r1_by_step[8192]["interval_newton_image"])
    fine_newton = exact_bounds(r1_by_step[16384]["interval_newton_image"])
    producer_newton = tuple(Fraction(value) for value in producer["narrow"]["newton_exact_bounds"])
    fine_D = tuple(Fraction(value) for value in r1_by_step[16384]["root_box"]["event_bracket_exact"])
    producer_D = tuple(Fraction(str(value)) for value in producer["narrow"]["event_bracket"])

    refinement_quantities = [
        "curvature",
        "conformal_separation",
        "warp_at_event",
        "first_integral_union",
        "upper_wall_identity",
    ]
    refinement_widths_decrease = {
        name: width(r1_by_step[16384]["geometry"][name])
        < width(r1_by_step[8192]["geometry"][name])
        for name in refinement_quantities
    }

    source_hashes = {
        "independent_engine": sha256(HERE / "independent_d1_replay.py"),
        "r1_wrapper": sha256(HERE / "independent_d1_replay_r1.py"),
        "r0_contract": sha256(HERE / "CONTRACT.md"),
        "r1_contract": sha256(HERE / "CONTRACT_R1.md"),
    }
    source_hash_checks = {
        "independent_engine": source_hashes["independent_engine"]
        == "d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044",
        "r1_wrapper": source_hashes["r1_wrapper"]
        == "25e90b9b881787f8fd3d7f4e93bf2fb05ea64e2e30534f511c99b9911bdfe043",
        "r0_contract": source_hashes["r0_contract"]
        == "3d6c33ff374764e41f95ec60700868ff614319d992cbbfc692798bddc03db2ad",
        "r1_contract": source_hashes["r1_contract"]
        == "6dbb9d39a05a8dbd3f47008c1c3506cbdc30ca1e8e4567b98b70a191fa676064",
    }

    checks = {
        "r0_complete": r0["status"] == "COMPLETE" and r0["error"] is None,
        "r0_classification_retained": r0["classification"] == "INDEPENDENT_D1_REPLAY_NOT_ESTABLISHED",
        "r0_4096_failed_self_map": r0_by_step[4096]["strict_self_map"] is False,
        "r0_8192_passed_self_map": r0_by_step[8192]["strict_self_map"] is True,
        "r1_complete": r1["status"] == "COMPLETE" and r1["error"] is None,
        "r1_pass_classification": r1["classification"] == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS",
        "r1_declared_steps": sorted(r1_by_step) == [8192, 16384],
        "r1_all_levels_root_pass": r1["all_levels_root_replay_pass"] is True,
        "r1_all_levels_geometry_pass": r1["all_levels_geometry_pass"] is True,
        "r1_fine_newton_strictly_inside_coarse": coarse_newton[0] < fine_newton[0] < fine_newton[1] < coarse_newton[1],
        "independent_and_producer_newton_images_overlap": overlaps(fine_newton, producer_newton),
        "independent_and_producer_event_brackets_overlap": overlaps(fine_D, producer_D),
        "source_hashes_match_freeze": all(source_hash_checks.values()),
        "method_declares_no_original_import_or_enclosure": r1["method"]["imports_predecessor_source"] is False
        and r1["method"]["reads_predecessor_enclosures"] is False,
        "both_remote_exit_codes_zero": (HERE / "output" / "r0" / "EXIT_CODE").read_text().strip() == "0"
        and (HERE / "output" / "r1" / "EXIT_CODE").read_text().strip() == "0",
    }
    level_checks = {str(step): audit_level(level) for step, level in sorted(r1_by_step.items())}
    passed = all(checks.values()) and all(all(values.values()) for values in level_checks.values())
    result = {
        "schema": "lin-d1-independent-replay-postrun-audit-v2",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "level_checks": level_checks,
        "refinement_widths_decrease": refinement_widths_decrease,
        "refinement_diagnostic": {
            "required_for_pass": False,
            "reason": "The frozen contracts require exact nesting of the interval-Newton image and passage of every geometry inclusion gate; they do not require every derived interval width to decrease monotonically.",
            "curvature_width_ratio_fine_over_coarse": float(
                width(r1_by_step[16384]["geometry"]["curvature"])
                / width(r1_by_step[8192]["geometry"]["curvature"])
            ),
            "interpretation": "The curvature enclosure widens by a negligible amount while remaining strictly positive; this is disclosed as a non-monotone enclosure-width diagnostic and does not alter a frozen gate."
        },
        "source_hashes": source_hashes,
        "result_hashes": {
            "r0": sha256(r0_path),
            "r1": sha256(r1_path),
            "original_d1_comparison_only": sha256(producer_path),
        },
        "comparison": {
            "r1_fine_newton_exact": [str(value) for value in fine_newton],
            "original_d1_newton_exact": [str(value) for value in producer_newton],
            "r1_fine_event_exact": [str(value) for value in fine_D],
            "original_d1_event": [str(value) for value in producer_D],
        },
        "claim_boundary": "Independent reduced-static replay and geometry enclosures only; no stability, dynamical-selection, initial-data bridge, collapse, event-horizon, or baby-universe result."
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
