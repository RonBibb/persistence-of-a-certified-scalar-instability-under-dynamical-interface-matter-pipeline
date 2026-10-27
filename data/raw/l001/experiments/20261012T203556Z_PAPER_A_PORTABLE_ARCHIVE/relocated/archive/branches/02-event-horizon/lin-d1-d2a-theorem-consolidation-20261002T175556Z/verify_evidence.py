#!/usr/bin/env python3
"""Independent read-only verifier for the D1/D2A consolidation packet."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


EXPECTED = {
    "branches/02-event-horizon/lin-physical-exterior-capture-window-20261001T194822Z/TERMINAL.json": "741d458676a8309a0f1ad0ae96fcdd822f406d950e108ce291366aff9150cda5",
    "branches/02-event-horizon/lin-d1-validated-flow-prerequisite-20261001T212157Z/TERMINAL.json": "0b559edc6f1ec9fe5bba78a0f31812aa773ad393f1040a7efc92c51844452f3d",
    "branches/02-event-horizon/lin-d1-validated-event-prerequisite-20261001T212800Z/TERMINAL.json": "cf752fba7c0ebfef4ab427ba6335f76bf38a2c79a1a2e6ccccef4ef77ac36b15",
    "branches/02-event-horizon/lin-d1-validated-sensitivity-newton-20261002T012953Z/validated_sensitivity_newton.py": "9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653",
    "branches/02-event-horizon/lin-d1-validated-sensitivity-newton-r1-20261002T014500Z/validated_sensitivity_newton_r1.py": "c388b3bd1e616f38dfa9a27be9d74cbe1de0b618386749e32fbc8a2de48896f3",
    "branches/02-event-horizon/lin-d1-independent-audit-20261002T014828Z/TERMINAL.json": "d8a5848c11949651f1997a4df67c6fe776f394ed32279f1f5d490188e9f03f56",
    "branches/02-event-horizon/lin-d1-high-resolution-confirmation-20261002T015100Z/TERMINAL.json": "914416d98779fc468f61629b8afdda7fb8d7251acc33b7cf42db929272e78f9d",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-20261002T020000Z/TERMINAL.json": "1f43d6d6887308d2b6d4ccb0360ce5d3cfb48439f3bac5fc9a07a600253e0ef7",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/d2a_validated_cover_r1.py": "b0110bbb5f5bdda9a69d9958dfba050389db4c375b3d9187e8d706f1be8a3691",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/BINDINGS.json": "92e613848d8ebf542b035ea65559dc700ac8ad96bdb2a41f8a00a53ec347c935",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/PREFLIGHT.json": "0163ef25fc8a42ec68b0019c71be558b25af79ab40baf1f4c331974cdcfa9173",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json": "eb16a5e4bb027aaf598f954bdd48d51611a1c48ffc7669afabb6b3f3a3dea8a5",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/TERMINAL_CHECKPOINT.json": "79e9b26f4a88cdc6e525ebdc567612af8e102c859ae797ff88575f7f72c5a77a",
    "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/TERMINAL.json": "47b35e77299a5b150d4c4f86a2ba1648654484c61ddd8b71235138d1cfddda5b",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def verify_manifest(directory: Path) -> dict:
    manifest_path = directory / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    mismatches = []
    for relative, expected in manifest["files"].items():
        actual = sha256(directory / relative)
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
    terminal = json.loads((directory / "TERMINAL.json").read_text())
    manifest_hash = sha256(manifest_path)
    terminal_manifest_hash = terminal.get("manifest_sha256")
    if terminal_manifest_hash is None:
        terminal_manifest_hash = terminal.get("integrity", {}).get("manifest_sha256")
    return {
        "directory": str(directory.relative_to(ROOT)),
        "files_checked": len(manifest["files"]),
        "file_mismatches": mismatches,
        "manifest_sha256": manifest_hash,
        "terminal_manifest_binding_matches": terminal_manifest_hash == manifest_hash,
        "terminal_manifest_binding_field_found": terminal_manifest_hash is not None,
    }


def interval_zero_distance(bounds: list[str]) -> Fraction:
    lo, hi = map(Fraction, bounds)
    if lo <= 0 <= hi:
        return Fraction(0)
    return min(abs(lo), abs(hi))


def main() -> None:
    hash_checks = []
    for relative, expected in EXPECTED.items():
        actual = sha256(ROOT / relative)
        hash_checks.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "matches": actual == expected,
            }
        )

    manifest_checks = [
        verify_manifest(
            ROOT
            / "branches/02-event-horizon/lin-physical-exterior-capture-window-20261001T194822Z"
        ),
        verify_manifest(
            ROOT
            / "branches/02-event-horizon/lin-d1-validated-flow-prerequisite-20261001T212157Z"
        ),
        verify_manifest(
            ROOT
            / "branches/02-event-horizon/lin-d1-validated-event-prerequisite-20261001T212800Z"
        ),
        verify_manifest(ROOT / "branches/02-event-horizon/lin-d1-independent-audit-20261002T014828Z"),
        verify_manifest(ROOT / "branches/02-event-horizon/lin-d1-high-resolution-confirmation-20261002T015100Z"),
        verify_manifest(ROOT / "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z"),
    ]

    d1 = load_json(
        "branches/02-event-horizon/lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json"
    )
    d1_audit = load_json(
        "branches/02-event-horizon/lin-d1-independent-audit-20261002T014828Z/RESULT.json"
    )
    inclusion = load_json(
        "branches/02-event-horizon/lin-d1-independent-audit-20261002T014828Z/INCLUSION_CERTIFICATES.json"
    )
    narrow_box = list(map(Fraction, inclusion["boxes"]["narrow"]))
    narrow_image = list(map(Fraction, d1["narrow"]["newton_exact_bounds"]))
    prior_narrow = next(
        list(map(Fraction, item["bounds"]))
        for item in inclusion["images"]
        if item["steps"] == 16384 and item["box"] == "narrow"
    )
    d1_checks = {
        "status_complete": d1["status"] == "COMPLETE",
        "classification_matches": d1["classification"]
        == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS",
        "step_count_32768": d1["producer_step_count"] == 32768,
        "precision_768_bits": d1["arb_precision_bits"] == 768,
        "both_frozen_boxes_reported_strict_self_maps": d1[
            "both_frozen_boxes_strict_self_maps"
        ]
        is True,
        "narrow_exact_image_strictly_inside_frozen_box": narrow_box[0]
        < narrow_image[0]
        < narrow_image[1]
        < narrow_box[1],
        "narrow_32768_image_strictly_inside_16384_image": prior_narrow[0]
        < narrow_image[0]
        < narrow_image[1]
        < prior_narrow[1],
        "transverse_G_s_negative": d1["narrow"]["G_s_bounds"][1] < 0,
        "implicit_h_prime_excludes_zero": d1["narrow"]["h_prime_bounds"][0] > 0,
        "independent_formula_audit_pass": d1_audit["status"] == "PASS"
        and all(d1_audit["symbolic"].values()),
        "audit_scope_is_not_independent_ode_replay": "not an independent ODE"
        in d1_audit["scope"],
    }

    d2 = load_json(
        "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json"
    )
    d2_audit = load_json(
        "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/POSTRUN_AUDIT.json"
    )
    boxes = d2["terminal_boxes"]
    exact_cover = bool(boxes) and Fraction(boxes[0]["a_exact_bounds"][0]) == 0
    for left, right in zip(boxes, boxes[1:]):
        exact_cover = exact_cover and Fraction(left["a_exact_bounds"][1]) == Fraction(
            right["a_exact_bounds"][0]
        )
    exact_cover = exact_cover and Fraction(boxes[-1]["a_exact_bounds"][1]) == Fraction(
        3602879701896397, 36028797018963968
    )

    classification_rederived = True
    uniform_floor = True
    floor = Fraction(77, 10000)
    for box in boxes:
        record = box["record"]
        classification = box["classification"]
        if classification == "NEGATIVE_CURVATURE_EXCLUDED":
            classification_rederived &= Fraction(record["curvature_exact_bounds"][1]) < 0
            continue
        g_distance = interval_zero_distance(record["G_exact_bounds"])
        h_distance = interval_zero_distance(record["scalar_residual_exact_bounds"])
        uniform_floor &= max(g_distance, h_distance) > floor
        if classification == "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO":
            classification_rederived &= g_distance > 0 and h_distance > 0
        elif classification == "UPPER_ISRAEL_EXCLUDED":
            classification_rederived &= g_distance > 0 and h_distance == 0
        elif classification == "UPPER_SCALAR_EXCLUDED":
            classification_rederived &= g_distance == 0 and h_distance > 0
        else:
            classification_rederived = False

    counts = dict(Counter(box["classification"] for box in boxes))
    checkpoint_dir = ROOT / (
        "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/"
        "output/checkpoints"
    )
    checkpoint_files = sorted(checkpoint_dir.glob("checkpoint-*.json"))
    checkpoint_addresses = True
    for path in checkpoint_files:
        payload = json.loads(path.read_text())
        canonical = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
        checkpoint_addresses &= (
            path.stem.removeprefix("checkpoint-") == hashlib.sha256(canonical).hexdigest()
        )
    d2_checks = {
        "status_complete": d2["status"] == "COMPLETE",
        "classification_matches": d2["classification"]
        == "FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE",
        "terminal_box_count_693": len(boxes) == d2["terminal_box_count"] == 693,
        "classification_counts_reproduced": counts == d2["classification_counts"],
        "classifications_rederived_from_exact_intervals": classification_rederived,
        "exact_contiguous_cover_rederived": exact_cover,
        "unresolved_empty": d2["unresolved"] == [],
        "uniform_residual_vector_floor_gt_0_0077_rederived": uniform_floor,
        "postrun_audit_pass": d2_audit["status"] == "PASS",
        "postrun_result_hash_matches": d2_audit["result_sha256"]
        == sha256(
            ROOT
            / "branches/02-event-horizon/lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json"
        ),
        "immutable_checkpoint_count_86": len(checkpoint_files) == 86,
        "checkpoint_content_addresses_rederived": checkpoint_addresses,
    }

    all_pass = (
        all(item["matches"] for item in hash_checks)
        and all(not item["file_mismatches"] for item in manifest_checks)
        and all(item["terminal_manifest_binding_matches"] for item in manifest_checks)
        and all(d1_checks.values())
        and all(d2_checks.values())
    )
    report = {
        "schema": "d1-d2a-consolidation-independent-verification-v1",
        "status": "PASS" if all_pass else "FAIL",
        "root": str(ROOT),
        "hash_checks": hash_checks,
        "manifest_checks": manifest_checks,
        "d1_checks": d1_checks,
        "d2a_checks": d2_checks,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
