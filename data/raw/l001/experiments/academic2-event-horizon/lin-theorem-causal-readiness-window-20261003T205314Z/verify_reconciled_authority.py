#!/usr/bin/env python3
"""Read-only verification of the reconciled D1/D2A theorem authority."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
BINDINGS_PATH = HERE / "AUTHORITY_BINDINGS.json"
EXACT_PATH = HERE / "THEOREM_INTERVALS_EXACT.json"


def digest(path):
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def interval_zero_distance(bounds):
    lo, hi = (Fraction(value) for value in bounds)
    if lo > 0:
        return lo
    if hi < 0:
        return -hi
    return Fraction(0)


checks = []


def require(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


bindings = load(BINDINGS_PATH)
declared_root = Path(bindings["research_root"])
portable_root = HERE.parents[2]
root = declared_root if declared_root.is_dir() else portable_root
require("research_root.available", root.is_dir())
require("research_root.portable_layout", (root / "RESEARCH_MAP.md").is_file())


def verify_binding_tree(node, prefix="bindings"):
    if isinstance(node, dict):
        for key, value in node.items():
            verify_binding_tree(value, f"{prefix}.{key}")
    elif (
        isinstance(node, list)
        and len(node) == 2
        and isinstance(node[0], str)
        and isinstance(node[1], str)
        and len(node[1]) == 64
    ):
        path = root / node[0]
        require(f"{prefix}.exists", path.is_file())
        require(f"{prefix}.sha256", digest(path) == node[1])


verify_binding_tree(bindings)

d1_binding = bindings["static_theorem"]["independent_d1_replay"]
d1_terminal = load(root / d1_binding["terminal"][0])
d1_audit = load(root / d1_binding["audit"][0])
d1_result = load(root / d1_binding["result"][0])

require("d1.terminal.sealed", d1_terminal["status"] == "SEALED_COMPLETE")
require("d1.terminal.classification", d1_terminal["classification"] == d1_binding["classification"])
require("d1.terminal.manifest_link", d1_terminal["manifest_sha256"] == d1_binding["manifest"][1])
require("d1.terminal.audit_link", d1_terminal["postrun_audit_sha256"] == d1_binding["audit"][1])
require("d1.terminal.result_link", d1_terminal["r1_result_sha256"] == d1_binding["result"][1])
require("d1.audit.pass", d1_audit["status"] == "PASS")
require("d1.audit.result_link", d1_audit["result_hashes"]["r1"] == d1_binding["result"][1])
require("d1.audit.all_checks", all(d1_audit["checks"].values()))
require("d1.result.complete", d1_result["status"] == "COMPLETE")
require("d1.result.classification", d1_result["classification"] == d1_binding["classification"])
require("d1.result.root_levels", d1_result["all_levels_root_replay_pass"] is True)
require("d1.result.geometry_levels", d1_result["all_levels_geometry_pass"] is True)
require("d1.result.nested_newton", d1_result["fine_newton_image_strictly_inside_coarse_image"] is True)
require("d1.result.step_inventory", sorted(level["steps"] for level in d1_result["levels"]) == [8192, 16384])
require("d1.result.each_level", all(level["strict_self_map"] and level["root_replay_pass"] and level["geometry"]["pass"] for level in d1_result["levels"]))

d2_binding = bindings["static_theorem"]["d2a_fixed_separation_exclusion"]
d2_terminal = load(root / d2_binding["terminal"][0])
d2_audit = load(root / d2_binding["audit"][0])
d2_result = load(root / d2_binding["result"][0])

require("d2.terminal.complete", d2_terminal["status"] == "COMPLETE")
require("d2.terminal.classification", d2_terminal["classification"] == d2_binding["classification"])
require("d2.terminal.manifest_link", d2_terminal["manifest_sha256"] == d2_binding["manifest"][1])
require("d2.audit.pass", d2_audit["status"] == "PASS")
require("d2.audit.result_link", d2_audit["result_sha256"] == d2_binding["result"][1])
require("d2.audit.cover", d2_audit["exact_contiguous_cover_reproduced"] is True)
require("d2.audit.addresses", d2_audit["all_checkpoint_content_addresses_verified"] is True)
require("d2.audit.no_worker", d2_audit["live_worker_after_completion"] is False)
require("d2.result.complete", d2_result["status"] == "COMPLETE")
require("d2.result.classification", d2_result["classification"] == d2_binding["classification"])
require("d2.result.cover", d2_result["coverage_audit"]["exact_contiguous_cover"] is True)
require("d2.result.endpoints", d2_result["coverage_audit"]["first_exact_endpoint"] == "0" and d2_result["coverage_audit"]["last_exact_endpoint"] == "3602879701896397/36028797018963968")
require("d2.result.box_count", d2_result["terminal_box_count"] == 693)
require("d2.result.no_unresolved", d2_result["unresolved"] == [])
require("d2.result.classification_count_sum", sum(d2_result["classification_counts"].values()) == d2_result["terminal_box_count"])

d2_boxes = d2_result["terminal_boxes"]
d2_counts = {}
d2_classifications_rederived = True
d2_margins = []
for index, box in enumerate(d2_boxes):
    classification = box["classification"]
    d2_counts[classification] = d2_counts.get(classification, 0) + 1
    record = box["record"]
    if classification == "NEGATIVE_CURVATURE_EXCLUDED":
        d2_classifications_rederived &= Fraction(record["curvature_exact_bounds"][1]) < 0
        continue
    g_distance = interval_zero_distance(record["G_exact_bounds"])
    h_distance = interval_zero_distance(record["scalar_residual_exact_bounds"])
    d2_margins.append((max(g_distance, h_distance), index, box))
    if classification == "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO":
        d2_classifications_rederived &= g_distance > 0 and h_distance > 0
    elif classification == "UPPER_ISRAEL_EXCLUDED":
        d2_classifications_rederived &= g_distance > 0 and h_distance == 0
    elif classification == "UPPER_SCALAR_EXCLUDED":
        d2_classifications_rederived &= g_distance == 0 and h_distance > 0
    else:
        d2_classifications_rederived = False

d2_exact_cover = bool(d2_boxes) and Fraction(d2_boxes[0]["a_exact_bounds"][0]) == 0
for left, right in zip(d2_boxes, d2_boxes[1:]):
    d2_exact_cover &= Fraction(left["a_exact_bounds"][1]) == Fraction(right["a_exact_bounds"][0])
d2_exact_cover &= Fraction(d2_boxes[-1]["a_exact_bounds"][1]) == Fraction(3602879701896397, 36028797018963968)

minimum_margin, minimum_index, minimum_box = min(d2_margins, key=lambda item: item[0])
require("d2.direct.counts", d2_counts == d2_result["classification_counts"])
require("d2.direct.classifications", d2_classifications_rederived)
require("d2.direct.cover", d2_exact_cover)
require("d2.direct.uniform_floor", minimum_margin > Fraction(77, 10000))

old_binding = bindings["static_theorem"]["older_consolidation"]
old_terminal = load(root / old_binding["terminal"][0])
require("old_consolidation.complete", old_terminal["status"] == "COMPLETE")
require("old_consolidation.classification", old_terminal["classification"] == old_binding["classification"])

exact = load(EXACT_PATH)
require("exact.schema", exact["schema"] == "lin-reconciled-theorem-interval-authority-v1")
require("exact.self_source.d1", exact["source_sha256"]["d1_independent_result"] == d1_binding["result"][1])
require("exact.self_source.d2", exact["source_sha256"]["d2a_result"] == d2_binding["result"][1])
require("exact.self_source.d2_audit", exact["source_sha256"]["d2a_postrun_audit"] == d2_binding["audit"][1])

fine = next(level for level in d1_result["levels"] if level["steps"] == 16384)
fine_exact = exact["d1_independent_16384"]
require("exact.d1.newton", fine_exact["interval_newton"]["exact_bounds"] == fine["interval_newton_image"]["exact_bounds"])
require("exact.d1.proper_separation", fine_exact["proper_separation"]["exact_bounds"] == fine["root_box"]["event_bracket_exact"])
require("exact.d1.q_prime", fine_exact["q_prime"]["exact_bounds"] == fine["root_box"]["event_quantities"]["q_a"]["exact_bounds"])
for field in (
    "curvature",
    "conformal_separation",
    "first_integral_union",
    "global_warp_enclosure",
    "lower_wall_identity",
    "upper_wall_identity",
    "warp_at_event",
):
    require(f"exact.d1.{field}", fine_exact[field]["exact_bounds"] == fine["geometry"][field]["exact_bounds"])

d2_exact = exact["d2a_fixed_separation"]
require("exact.d2.counts", d2_exact["classification_counts"] == d2_result["classification_counts"])
require("exact.d2.box_count", d2_exact["terminal_box_count"] == d2_result["terminal_box_count"])
require("exact.d2.no_unresolved", d2_exact["unresolved_box_count"] == len(d2_result["unresolved"]))
require("exact.d2.cover", d2_exact["exact_contiguous_cover"] == d2_result["coverage_audit"]["exact_contiguous_cover"])
require("exact.d2.launch_domain", d2_exact["launch_domain_exact"] == [d2_result["coverage_audit"]["first_exact_endpoint"], d2_result["coverage_audit"]["last_exact_endpoint"]])
require("exact.d2.D0", d2_exact["D0_exact"] == str(Fraction.from_float(float(d2_result["frozen_design"]["D0_decimal_promoted_as_binary64_dyadic"]))))
require("exact.d2.floor", d2_exact["uniform_positive_route_residual_vector_linf_lower_bound"] == d2_audit["uniform_positive_route_residual_vector_linf_lower_bound"])
minimum_record = d2_exact["rederived_minimum_positive_route_linf_lower_bound"]
require("exact.d2.minimum_floor", minimum_record["exact"] == str(minimum_margin))
require(
    "exact.d2.minimum_floor_location",
    minimum_record["terminal_box_zero_based_index"] == minimum_index
    and minimum_record["a_exact_bounds"] == minimum_box["a_exact_bounds"]
    and minimum_record["classification"] == minimum_box["classification"],
)

d0 = Fraction(d2_exact["D0_exact"])
contrast = exact["derived_separation_contrast"]
for label, separation_bounds in (
    ("original_32768", exact["d1_original_32768"]["proper_separation"]["exact_bounds"]),
    ("independent_16384", fine_exact["proper_separation"]["exact_bounds"]),
):
    dlo, dhi = (Fraction(value) for value in separation_bounds)
    require(
        f"exact.contrast.{label}.difference",
        contrast[label]["D_minus_D0_exact_bounds"] == [str(dlo - d0), str(dhi - d0)],
    )
    require(
        f"exact.contrast.{label}.ratio",
        contrast[label]["D_over_D0_exact_bounds"] == [str(dlo / d0), str(dhi / d0)],
    )

output = {
    "schema": "lin-reconciled-authority-verification-v1",
    "status": "PASS",
    "checks_passed": len(checks),
    "bound_files_verified": sum(1 for name in checks if name.endswith(".sha256")),
    "declared_research_root": str(declared_root),
    "resolved_research_root": str(root),
    "portable_root_fallback_used": root != declared_root,
    "d1_classification": d1_result["classification"],
    "d2_classification": d2_result["classification"],
    "claim_boundary": exact["claim_boundary"],
}
print(json.dumps(output, indent=2, sort_keys=True))
