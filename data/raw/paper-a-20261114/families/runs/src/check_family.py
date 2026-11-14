"""Exact-rational gate evaluation for the controls and the family sub-boxes.

Every predicate is decided from the exact rational bounds that the interval
producers print, with Python Fractions; no floating-point threshold decision
is used.  Gate kinds:
  IMPLEMENTATION  missing record, crash, incomplete status for a non-inequality
                  reason, binding, consumption or hash mismatch;
  PREDICATE       a certificate inequality that was evaluated (or enforced by
                  a frozen abort label, ABORT_PREDICATE) and did not hold;
  DEPENDENT       not evaluated because a prerequisite job or gate failed;
  NOT_RUN         the job was never started (launch cutoff, or no record).
A sub-box that fails is "not certified"; that is never read as a counterexample.

usage: check_family.py controls STAGE ARCHIVED_REFS OUT_JSON
       check_family.py family   STAGE ARCHIVED_REFS BOXES_JSON OUT_DIR
"""
import hashlib
import json
import os
import sys
from fractions import Fraction as Q

V0 = Q(3602879701896397, 36028797018963968)
M2 = Q(7385903388887613, 18014398509481984)
GAMMA = Q(20)
ARCHIVED_PHASE = [Q(577838035, 536870912), Q(577858823, 536870912)]
ARCHIVED_D = [Q(32727, 16384), Q(32729, 16384)]
SLACK = 1 - Q(1, 2**600)
PHASE_CODE = {
    "test1_phase_v3.py": "9f2da0122d8f411365c8703f12d1342c8c70da83b79a1976dd80824c9864d816",
    "engine/primary_interval.py": "b4201caa2934905b0a2de198cd6eba2c2d08131a0d496d8da76ac3dc3c8c92d2",
    "engine/independent_interval.py": "260150e6371209bc3eac1834e7be2c97b4d7e582338cd567c82843a4f44efbeb",
}
BG_CODE = {
    "validated_sensitivity_newton.py": "9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653",
    "confirm_32768.py": "98d17ad555c7012266debe9e406fab02eae6db6b57dbe41c53dc635c66e7fe09",
    "independent_d1_replay.py": "d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044",
    "independent_d1_replay_r1.py": "25e90b9b881787f8fd3d7f4e93bf2fb05ea64e2e30534f511c99b9911bdfe043",
}
HALF3 = Q(3, 2)
# Frozen abort labels.  A producer or driver abort whose message contains one of
# these is an inequality the method could not establish; anything else,
# including every unlisted message, is an implementation failure.
ABORT_PREDICATE = (
    "Picard enclosure did not self-contain", "no zero-containing event cell",
    "Picard enclosure failed after", "no upper-Israel zero-containing cell",
    "PHASE_BOX_CONTAINS_ORIGIN", "AMBIGUOUS_PHASE_LIFT", "PHASE_DISCONNECTED", "END_OUTSIDE_CHART",
    "EVENT_OUTSIDE_CHART", "NONFINITE", "'WARP'", "LOWER_BACKGROUND_PREMISES", "ZERO_HESSIAN_LAUNCH",
    "PHASE_BELOW_AUXILIARY", "MASSLESS_OR_COUNT_UNRESOLVED", "MASSLESS_THRESHOLD_CONTACT",
    "Primary Picard inclusion failed", "Independent Picard box did not strictly contain its image",
    "Lower normalization singular", "Independent lower normalization denominator contains zero",
)


def abort_kind(message):
    text = message or ""
    return "PREDICATE" if any(label in text for label in ABORT_PREDICATE) else "IMPLEMENTATION"


def load(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def dyadic(text):
    n, d = float(text).as_integer_ratio()
    return Q(n, d)


def pair(values):
    return Q(values[0]), Q(values[1])


def inside_or_equal(new, old):
    """True when new equals old exactly or lies strictly inside it."""
    nl, nh = new
    ol, oh = old
    return (nl == ol and nh == oh) or (ol < nl and nh < oh)


def strictly_contains(outer, inner):
    return outer[0] < inner[0] and inner[1] < outer[1]


class Gates:
    def __init__(self):
        self.rows = []

    def add(self, name, ok, kind, detail=None):
        self.rows.append({"gate": name, "pass": bool(ok), "kind": kind, "detail": detail})
        return bool(ok)

    def failed(self):
        return [row for row in self.rows if not row["pass"]]


def code_hashes_ok(job_dir, table):
    out = {}
    for rel, expected in table.items():
        path = os.path.join(job_dir, rel)
        out[rel] = os.path.exists(path) and sha256(path) == expected
    return out


def job_state(job_dir):
    """ran / not_run / dependent, from the runner's exec.json."""
    record = load(os.path.join(job_dir, "exec.json"))
    if record is None:
        return "not_run", None
    if record.get("status") == "SKIPPED":
        if record.get("reason") == "LAUNCH_CUTOFF_REACHED":
            return "not_run", record
        return "dependent", record
    return "ran", record


def consumption_gates(gates, label, record, job, calls_key, expected_calls):
    consumption = record.get("consumption") or {}
    gates.add(f"{label}_consumption_calls", consumption.get(calls_key) == expected_calls, "IMPLEMENTATION",
              consumption.get(calls_key))
    plo, phi = pair(record["parameter_ball_exact_bounds"])
    radius = (phi - plo) / 2
    if job["param"] == "v1":
        observed = consumption.get("min_radius_h")
        ok = observed is not None and Q(observed) >= (GAMMA / 2) * radius * SLACK
        gates.add(f"{label}_v1_ball_consumed_every_call", ok, "IMPLEMENTATION", observed)
    else:
        observed = consumption.get("min_radius_G")
        ok = observed is not None and Q(observed) >= radius / 6 * SLACK
        gates.add(f"{label}_lambda_b_ball_consumed_every_call", ok, "IMPLEMENTATION", observed)


def check_primary(gates, record, job, steps=32768):
    """Returns (usable_for_phase, summary or None)."""
    if not gates.add("P1_record_present", record is not None, "IMPLEMENTATION"):
        return False, None
    gates.add("P1_job_matches_frozen_spec", record.get("job") == job, "IMPLEMENTATION")
    lo, hi = Q(job["lo"]), Q(job["hi"])
    plo, phi = pair(record["parameter_ball_exact_bounds"])
    gates.add("P2_parameter_ball_outward", plo <= lo and hi <= phi, "IMPLEMENTATION")
    box = (dyadic(job["A_lo"]), dyadic(job["A_hi"]))
    gates.add("P3_frozen_box", pair(record["box_exact_dyadic_bounds"]) == box, "IMPLEMENTATION")
    result = record["producer_result"]
    if result.get("status") != "COMPLETE":
        gates.add("P4_status_complete", False, abort_kind(result.get("error")), result.get("error"))
        return False, None
    gates.add("P4_status_complete", True, "IMPLEMENTATION")
    consumption_gates(gates, "R1_primary", record, job, "event_quantity_calls", 2 * steps)
    rows = result["all_results"]
    if not gates.add("P4_single_family_row", len(rows) == 1 and rows[0]["box_name"] == "family"
                     and rows[0]["steps"] == steps, "IMPLEMENTATION"):
        return False, None
    row = rows[0]
    gates.add("P4_classification", result["classification"] == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS",
              "PREDICATE", result["classification"])
    for key in ("event_validated", "hprime_excludes_zero", "Gs_strictly_negative", "zero_cells_contiguous",
                "positive_before", "negative_after"):
        gates.add(f"P4_box_{key}", row["box_event"][key] is True, "PREDICATE")
    for key in ("event_validated", "zero_cells_contiguous", "positive_before", "negative_after"):
        gates.add(f"P4_centre_{key}", row["center_event"][key] is True, "PREDICATE")
    gates.add("P4_strict_self_map", row["strict_self_map"] is True, "PREDICATE")
    gates.add("P4_qualified_newton", row["qualified_newton_inclusion"] is True, "PREDICATE")
    image = row["interval_newton_image"]
    if not gates.add("P5_newton_image_present", image is not None, "PREDICATE"):
        return False, None
    nlo, nhi = pair(image["exact_bounds"])
    gates.add("P5_newton_image_strictly_inside_box", box[0] < nlo and nhi < box[1], "PREDICATE",
              image["exact_bounds"])
    first, last = row["box_event"]["event_cell_indices"]
    cfirst, clast = row["center_event"]["event_cell_indices"]
    gates.add("P6_box_bracket_has_both_sign_regions", first >= 1 and last <= steps - 2, "PREDICATE", [first, last])
    gates.add("P6_centre_bracket_has_both_sign_regions", cfirst >= 1 and clast <= steps - 2, "PREDICATE",
              [cfirst, clast])
    bracket = pair(row["box_event"]["event_bracket"])
    gates.add("P6_bracket_inside_open_interval", 0 < bracket[0] < bracket[1] < 2, "PREDICATE")
    usable = (result["classification"] == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS"
              and row["qualified_newton_inclusion"] is True)
    return usable, {"newton": (nlo, nhi), "bracket": bracket, "row": row}


def check_independent(gates, record, job, steps=8192):
    if not gates.add("I1_record_present", record is not None, "IMPLEMENTATION"):
        return None
    gates.add("I1_job_matches_frozen_spec", record.get("job") == job, "IMPLEMENTATION")
    lo, hi = Q(job["lo"]), Q(job["hi"])
    plo, phi = pair(record["parameter_ball_exact_bounds"])
    gates.add("I2_parameter_ball_outward", plo <= lo and hi <= phi, "IMPLEMENTATION")
    box = (dyadic(job["A_lo"]), dyadic(job["A_hi"]))
    gates.add("I1_common_frozen_box", pair(record["box_exact_dyadic_bounds"]) == box, "IMPLEMENTATION")
    result = record["engine_result"]
    if result.get("status") != "COMPLETE":
        gates.add("I3_status_complete", False, abort_kind(result.get("error")), result.get("error"))
        return None
    gates.add("I3_status_complete", True, "IMPLEMENTATION")
    consumption_gates(gates, "R2_independent", record, job, "upper_quantity_calls", 2 * steps)
    levels = result["levels"]
    if not gates.add("I3_single_level", len(levels) == 1 and levels[0]["steps"] == steps, "IMPLEMENTATION"):
        return None
    level = levels[0]
    centre = level["center"]["event_quantities"]
    radius = (phi - plo) / 2
    if job["param"] == "v1":
        width = Q(centre["h"]["exact_bounds"][1]) - Q(centre["h"]["exact_bounds"][0])
        gates.add("R3_independent_centre_h_width_shows_v1_ball", width >= GAMMA * radius * SLACK, "IMPLEMENTATION")
    else:
        width = Q(centre["G"]["exact_bounds"][1]) - Q(centre["G"]["exact_bounds"][0])
        gates.add("R3_independent_centre_G_width_shows_lambda_b_ball", width >= radius / 3 * SLACK, "IMPLEMENTATION")
    gates.add("I3_classification", result["classification"] == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS",
              "PREDICATE", result["classification"])
    gates.add("I3_root_replay_pass", level["root_replay_pass"] is True, "PREDICATE")
    gates.add("I3_strict_self_map", level["strict_self_map"] is True, "PREDICATE")
    for key, value in level["geometry"]["checks"].items():
        gates.add(f"I3_geometry_{key}", value is True, "PREDICATE")
    image = level["interval_newton_image"]
    if not gates.add("I4_newton_image_present", image is not None, "PREDICATE"):
        return None
    nlo, nhi = pair(image["exact_bounds"])
    gates.add("I4_newton_image_strictly_inside_box", box[0] < nlo and nhi < box[1], "PREDICATE",
              image["exact_bounds"])
    first, last = level["root_box"]["event_cells"]
    cfirst, clast = level["center"]["event_cells"]
    gates.add("I5_box_bracket_has_both_sign_regions", first >= 1 and last <= steps - 2, "PREDICATE", [first, last])
    gates.add("I5_centre_bracket_has_both_sign_regions", cfirst >= 1 and clast <= steps - 2, "PREDICATE",
              [cfirst, clast])
    quantities = level["root_box"]["event_quantities"]
    return {"newton": (nlo, nhi), "k": pair(level["geometry"]["curvature"]["exact_bounds"]),
            "T_b": pair(quantities["S"]["exact_bounds"]), "Phi_b": pair(quantities["phi"]["exact_bounds"]),
            "q_a": pair(quantities["q_a"]["exact_bounds"]),
            "bracket": pair(level["root_box"]["event_bracket_exact"])}


def check_geometry(gates, job, independent):
    box_hi = dyadic(job["A_hi"])
    gates.add("G2_T_a_negative", box_hi < V0, "PREDICATE", str(box_hi))
    gates.add("G4_m2_positive_so_Q_positive", M2 > 0, "PREDICATE")
    if independent is None:
        gates.add("G1_G3_require_independent_enclosures", False, "DEPENDENT")
        return
    gates.add("G1_k_positive", independent["k"][0] > 0, "PREDICATE", [str(x) for x in independent["k"]])
    gates.add("G3_T_b_positive", independent["T_b"][0] > 0, "PREDICATE", [str(x) for x in independent["T_b"]])


def check_phase(gates, phase_dir, primary, usable, reference_model):
    if not usable:
        gates.add("F0_phase_requires_usable_primary_background", False, "DEPENDENT")
        return None
    state, record = job_state(phase_dir)
    if state == "dependent":
        gates.add("F0_phase_job_skipped_despite_usable_primary", False, "IMPLEMENTATION", record.get("reason"))
        return None
    hashes = code_hashes_ok(phase_dir, PHASE_CODE)
    gates.add("F2_phase_code_byte_identical", all(hashes.values()), "IMPLEMENTATION", hashes)
    binding = load(os.path.join(phase_dir, "inputs", "central_bindings.json"))
    if not gates.add("F1_binding_present", binding is not None, "IMPLEMENTATION"):
        return None
    gates.add("F1_binding_A_is_primary_newton_image", pair(binding["config"]["A"]) == primary["newton"],
              "IMPLEMENTATION")
    gates.add("F1_binding_D_is_primary_event_bracket", pair(binding["config"]["D"]) == primary["bracket"],
              "IMPLEMENTATION")
    gates.add("F1_binding_model_equals_archived", binding["model_exact"] == reference_model, "IMPLEMENTATION")
    out = os.path.join(phase_dir, "test1_v3")
    failure = load(os.path.join(out, "FAILURE.json"))
    if failure is not None:
        gates.add("F6_driver_abort", False, abort_kind(failure.get("error")), failure.get("error"))
        return None
    result = load(os.path.join(out, "RESULT.json"))
    if not gates.add("F3_result_present", result is not None, "IMPLEMENTATION"):
        return None
    gates.add("F3_status", result.get("status") == "COMPLETE_PENDING_INDEPENDENT_AUDIT", "IMPLEMENTATION")
    gates.add("F3_no_additional_tachyon", result.get("additional_tachyons") == 0, "PREDICATE")
    phases = {}
    for name, steps in (("primary", 8192), ("independent", 16384)):
        engine = result["engines"].get(name)
        if not gates.add(f"F3_{name}_present", engine is not None and engine["steps"] == steps, "IMPLEMENTATION"):
            continue
        gates.add(f"F3_{name}_checks_pass", engine["checks_pass"] is True, "PREDICATE")
        gates.add(f"F3_{name}_no_additional_tachyon", engine["additional_tachyons"] == 0, "PREDICATE")
        gates.add(f"F3_{name}_massless_root_excluded", engine["massless_root_excluded"] is True, "PREDICATE")
        lo, hi = pair(engine["phase_over_pi"]["bounds"])
        gates.add(f"F4_{name}_phase_strictly_in_(1,3/2)", 1 < lo and hi < HALF3, "PREDICATE",
                  engine["phase_over_pi"]["bounds"])
        gates.add(f"F5_{name}_k_positive", pair(engine["k"]["bounds"])[0] > 0, "PREDICATE")
        gates.add(f"F5_{name}_Tprime_a_positive", pair(engine["Tp_a"]["bounds"])[0] > 0, "PREDICATE")
        phases[name] = (lo, hi)
    return phases


def trace_summary(phase_dir):
    summary = {}
    for name in ("primary", "independent"):
        trace = load(os.path.join(phase_dir, "test1_v3", f"{name}_trace.json"))
        if trace is None:
            continue
        kinds = {}
        low = high = None
        for row in trace:
            kinds[row["chart"]] = kinds.get(row["chart"], 0) + 1
            if row["cell"] == 0:
                continue
            a, b = Q(row["arc_over_pi"][0]), Q(row["arc_over_pi"][1])
            low = a if low is None else min(low, a)
            high = b if high is None else max(high, b)
        summary[name] = {"chart_counts": kinds,
                         "charts_on_cells_ge_1": sorted({row["chart"] for row in trace if row["cell"] >= 1}),
                         "arc_over_pi_hull_cells_ge_1": [str(low), str(high)],
                         "note": "launch cell 0 excluded; angles are outward 2^-40 roundings of whole-cell charts"}
    return summary


def subbox(stage, job, family, index, frozen, reference_model):
    tag = f"{family}_{index:02d}"
    gates = Gates()
    dirs = {kind: os.path.join(stage, "jobs", f"{kind}_{tag}") for kind in ("bgp", "bgi", "ph")}
    states = {kind: job_state(path)[0] for kind, path in dirs.items()}
    gates.add("S0_primary_code_byte_identical", all(code_hashes_ok(dirs["bgp"], {
        k: BG_CODE[k] for k in ("validated_sensitivity_newton.py", "confirm_32768.py")}).values()), "IMPLEMENTATION")
    gates.add("S0_independent_code_byte_identical", all(code_hashes_ok(dirs["bgi"], {
        "independent_d1_replay.py": BG_CODE["independent_d1_replay.py"]}).values()), "IMPLEMENTATION")
    gates.add("S0_primary_wrapper_matches_freeze", all(code_hashes_ok(dirs["bgp"], {
        k: frozen[k] for k in ("fam_bg_primary.py", "boot.py")}).values()), "IMPLEMENTATION")
    gates.add("S0_independent_wrapper_matches_freeze", all(code_hashes_ok(dirs["bgi"], {
        k: frozen[k] for k in ("fam_bg_independent.py", "boot.py")}).values()), "IMPLEMENTATION")
    gates.add("S0_phase_boot_matches_freeze", all(code_hashes_ok(dirs["ph"], {
        "boot.py": frozen["boot.py"]}).values()), "IMPLEMENTATION")
    primary_record = load(os.path.join(dirs["bgp"], "stdout.json")) if states["bgp"] == "ran" else None
    independent_record = load(os.path.join(dirs["bgi"], "stdout.json")) if states["bgi"] == "ran" else None
    if states["bgp"] == "not_run":
        gates.add("P0_primary_not_run", False, "NOT_RUN")
        usable, primary = False, None
    else:
        usable, primary = check_primary(gates, primary_record, job)
    if states["bgi"] == "not_run":
        gates.add("I0_independent_not_run", False, "NOT_RUN")
        independent = None
    else:
        independent = check_independent(gates, independent_record, job)
    check_geometry(gates, job, independent)
    if primary is not None and independent is not None:
        a, b = primary["newton"], independent["newton"]
        gates.add("X1_engine_newton_images_overlap", max(a[0], b[0]) <= min(a[1], b[1]), "PREDICATE")
    if states["ph"] == "not_run" and usable:
        gates.add("F0_phase_not_run", False, "NOT_RUN")
        phases = None
    else:
        phases = check_phase(gates, dirs["ph"], primary, usable, reference_model)
    failed = gates.failed()
    causes = [row for row in failed if row["kind"] in ("IMPLEMENTATION", "PREDICATE")]
    if not failed:
        verdict = "CERTIFIED"
    elif not causes:
        verdict = "NOT_RUN"
    elif all(row["kind"] == "IMPLEMENTATION" for row in causes):
        verdict = "NOT_CERTIFIED_IMPLEMENTATION"
    elif all(row["kind"] == "PREDICATE" for row in causes):
        verdict = "NOT_CERTIFIED_PREDICATE"
    else:
        verdict = "NOT_CERTIFIED_AMBIGUOUS"
    enclosure = {}
    if primary is not None:
        enclosure["A_newton_image_primary"] = [str(x) for x in primary["newton"]]
        enclosure["D_event_bracket_primary"] = [str(x) for x in primary["bracket"]]
    if independent is not None:
        enclosure["A_newton_image_independent"] = [str(x) for x in independent["newton"]]
        enclosure["k"] = [str(x) for x in independent["k"]]
        enclosure["T_b"] = [str(x) for x in independent["T_b"]]
        enclosure["q_prime_independent"] = [str(x) for x in independent["q_a"]]
        enclosure["D_event_bracket_independent"] = [str(x) for x in independent["bracket"]]
    if phases:
        enclosure["theta_b_over_pi"] = {name: [str(x) for x in value] for name, value in phases.items()}
        enclosure["theta_b_over_pi_hull"] = [str(min(v[0] for v in phases.values())),
                                             str(max(v[1] for v in phases.values()))]
    return {"subbox": tag, "param": job["param"], "interval": [job["lo"], job["hi"]],
            "A_box": [job["A_lo"], job["A_hi"]], "verdict": verdict, "job_states": states,
            "failed_gates": failed, "gate_count": len(gates.rows), "enclosures": enclosure,
            "phase_trace_summary": trace_summary(dirs["ph"])}


def seam_ok(left, right):
    """Same continuous root branch across the shared endpoint: overlapping
    A-boxes and the same strict sign of q' on both (independent exact bounds)."""
    a = (dyadic(left["A_box"][0]), dyadic(left["A_box"][1]))
    b = (dyadic(right["A_box"][0]), dyadic(right["A_box"][1]))
    overlap = max(a[0], b[0]) <= min(a[1], b[1])
    ql, qr = left["enclosures"].get("q_prime_independent"), right["enclosures"].get("q_prime_independent")
    if not (ql and qr):
        return False
    sign = lambda q: 1 if Q(q[0]) > 0 else (-1 if Q(q[1]) < 0 else 0)
    return overlap and sign(ql) != 0 and sign(ql) == sign(qr)


def family_mode(stage, refs, boxes_path, out_dir):
    boxes = load(boxes_path)
    frozen = load(os.path.join(stage, "FROZEN_SOURCES.json"))
    reference_model = load(os.path.join(refs, "central_bindings.json"))["model_exact"]
    report = {"families": {}}
    all_rows = []
    for family, spec in boxes["families"].items():
        rows = []
        for entry in spec["subboxes"]:
            job = {key: entry[key] for key in ("param", "lo", "hi", "A0", "A_lo", "A_hi")}
            rows.append(subbox(stage, job, family, entry["j"], frozen, reference_model))
        seams = [seam_ok(rows[i], rows[i + 1]) if rows[i]["verdict"] == rows[i + 1]["verdict"] == "CERTIFIED"
                 else None for i in range(len(rows) - 1)]
        anchor = spec["anchor_subbox"]
        run = []
        if rows[anchor]["verdict"] == "CERTIFIED":
            i = anchor
            while i - 1 >= 0 and rows[i - 1]["verdict"] == "CERTIFIED" and seams[i - 1]:
                i -= 1
            k = anchor
            while k + 1 < len(rows) and rows[k + 1]["verdict"] == "CERTIFIED" and seams[k]:
                k += 1
            run = [i, k]
        certified = [r["subbox"] for r in rows if r["verdict"] == "CERTIFIED"]
        if len(certified) == len(rows) and all(seams):
            classification = "FAMILY_CERTIFIED_FULL_SEGMENT"
        elif run:
            classification = "FAMILY_CERTIFIED_PARTIAL_SEGMENT"
        else:
            classification = "FAMILY_NOT_CERTIFIED_AT_ANCHOR_SUBBOX"
        segment = [rows[run[0]]["interval"][0], rows[run[1]]["interval"][1]] if run else None
        hulls = [r["enclosures"]["theta_b_over_pi_hull"] for r in rows[run[0]:run[1] + 1]] if run else []
        report["families"][family] = {
            "param": spec["param"], "frozen_segment": spec["segment"], "subboxes": len(rows),
            "certified_subboxes": len(certified), "anchor_subbox": rows[anchor]["subbox"],
            "certified_segment_containing_anchor": segment, "classification": classification,
            "certified_run_indices": run,
            "seams_failed_between_certified_neighbours": [i for i, s in enumerate(seams) if s is False],
            "verdict_counts": {v: sum(1 for r in rows if r["verdict"] == v) for v in sorted({r["verdict"] for r in rows})},
            "theta_b_over_pi_hull_over_certified_segment": None if not hulls else
            [str(min(Q(h[0]) for h in hulls)), str(max(Q(h[1]) for h in hulls))],
        }
        all_rows.extend(rows)
    with open(os.path.join(out_dir, "SUBBOX_VERDICTS.json"), "w") as handle:
        json.dump(all_rows, handle, indent=1, sort_keys=True)
    with open(os.path.join(out_dir, "FAMILY_VERDICT.json"), "w") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2, sort_keys=True))


def controls_mode(stage, refs, out_path):
    gates = Gates()
    jobs = os.path.join(stage, "jobs")
    ref_primary = load(os.path.join(refs, "primary_RESULT.json"))
    ref_independent = load(os.path.join(refs, "independent_RESULT.json"))
    ref_phase = load(os.path.join(refs, "phase_RESULT.json"))
    ref_binding = load(os.path.join(refs, "central_bindings.json"))
    for name, table in (("ctl_bgp", {k: BG_CODE[k] for k in ("validated_sensitivity_newton.py", "confirm_32768.py")}),
                        ("ctl_bgi", {k: BG_CODE[k] for k in ("independent_d1_replay.py", "independent_d1_replay_r1.py")}),
                        ("ctl_phase", PHASE_CODE)):
        gates.add(f"C0_{name}_code_byte_identical", all(code_hashes_ok(os.path.join(jobs, name), table).values()),
                  "IMPLEMENTATION")
    # C1a: archived primary rerun against the 18 October 2026 record.
    new = load(os.path.join(jobs, "ctl_bgp", "stdout.json"))
    if gates.add("C1a_primary_complete", new is not None and new.get("status") == "COMPLETE", "IMPLEMENTATION"):
        gates.add("C1a_primary_classification", new["classification"] == ref_primary["classification"]
                  == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS", "PREDICATE")
        old_rows = {(r["box_name"], r["steps"]): r for r in ref_primary["all_results"]}
        for row in new["all_results"]:
            old = old_rows.get((row["box_name"], row["steps"]))
            same = old is not None and inside_or_equal(pair(row["interval_newton_image"]["exact_bounds"]),
                                                       pair(old["interval_newton_image"]["exact_bounds"]))
            gates.add(f"C1a_{row['box_name']}_{row['steps']}_newton_image_equal_or_inside", same, "PREDICATE")
            gates.add(f"C1a_{row['box_name']}_{row['steps']}_event_bracket_equal",
                      old is not None and row["box_event"]["event_bracket"] == old["box_event"]["event_bracket"],
                      "PREDICATE")
    # C1b: archived independent R1 rerun.
    new = load(os.path.join(jobs, "ctl_bgi", "stdout.json"))
    if gates.add("C1b_independent_complete", new is not None and new.get("status") == "COMPLETE", "IMPLEMENTATION"):
        gates.add("C1b_independent_classification", new["classification"] == ref_independent["classification"]
                  == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS", "PREDICATE")
        old_levels = {lv["steps"]: lv for lv in ref_independent["levels"]}
        for level in new["levels"]:
            old = old_levels.get(level["steps"])
            same = old is not None and inside_or_equal(pair(level["interval_newton_image"]["exact_bounds"]),
                                                       pair(old["interval_newton_image"]["exact_bounds"]))
            gates.add(f"C1b_{level['steps']}_newton_image_equal_or_inside", same, "PREDICATE")
            gates.add(f"C1b_{level['steps']}_T_b_equal_or_inside", old is not None and inside_or_equal(
                pair(level["root_box"]["event_quantities"]["S"]["exact_bounds"]),
                pair(old["root_box"]["event_quantities"]["S"]["exact_bounds"])), "PREDICATE")
    # C1c: archived phase rerun.
    new = load(os.path.join(jobs, "ctl_phase", "test1_v3", "RESULT.json"))
    if gates.add("C1c_phase_complete", new is not None and new.get("status") == "COMPLETE_PENDING_INDEPENDENT_AUDIT",
                 "IMPLEMENTATION"):
        for name in ("primary", "independent"):
            bounds = pair(new["engines"][name]["phase_over_pi"]["bounds"])
            old = pair(ref_phase["engines"][name]["phase_over_pi"]["bounds"])
            gates.add(f"C1c_{name}_phase_equal_or_inside_archived", inside_or_equal(bounds, old), "PREDICATE")
            gates.add(f"C1c_{name}_phase_equal_or_inside_eq14", inside_or_equal(bounds, tuple(ARCHIVED_PHASE)),
                      "PREDICATE")
    # C2: family pipeline at the degenerate archived anchor box (box, centre,
    # step, precision, JSON embedding, binding generator; not consumption).
    narrow = {(r["box_name"], r["steps"]): r for r in ref_primary["all_results"]}[("narrow", 32768)]
    old_level = {lv["steps"]: lv for lv in ref_independent["levels"]}[8192]
    new = load(os.path.join(jobs, "c2_bgp", "stdout.json"))
    if gates.add("C2a_family_primary_present", new is not None and new["producer_result"].get("status") == "COMPLETE",
                 "IMPLEMENTATION"):
        row = new["producer_result"]["all_results"][0]
        for key in ("interval_newton_image", "box_event", "center_event", "strict_self_map",
                    "qualified_newton_inclusion"):
            gates.add(f"C2a_{key}_identical_to_archived_narrow", row[key] == narrow[key], "IMPLEMENTATION")
    new = load(os.path.join(jobs, "c2_bgi", "stdout.json"))
    if gates.add("C2b_family_independent_present", new is not None and new["engine_result"].get("status") == "COMPLETE",
                 "IMPLEMENTATION"):
        level = new["engine_result"]["levels"][0]
        for key in ("interval_newton_image", "strict_self_map", "root_replay_pass"):
            gates.add(f"C2b_{key}_identical_to_archived_8192", level[key] == old_level[key], "IMPLEMENTATION")
        gates.add("C2b_root_box_quantities_identical", level["root_box"]["event_quantities"]
                  == old_level["root_box"]["event_quantities"], "IMPLEMENTATION")
        gates.add("C2b_geometry_checks_identical", level["geometry"]["checks"] == old_level["geometry"]["checks"],
                  "IMPLEMENTATION")
    binding = load(os.path.join(jobs, "c2_phase", "inputs", "central_bindings.json"))
    if gates.add("C2c_binding_present", binding is not None, "IMPLEMENTATION"):
        gates.add("C2c_binding_A_equals_archived", pair(binding["config"]["A"]) == pair(ref_binding["config"]["A"]),
                  "IMPLEMENTATION")
        gates.add("C2c_binding_D_equals_archived", pair(binding["config"]["D"]) == pair(ref_binding["config"]["D"]),
                  "IMPLEMENTATION")
        gates.add("C2c_binding_model_equals_archived", binding["model_exact"] == ref_binding["model_exact"],
                  "IMPLEMENTATION")
    new = load(os.path.join(jobs, "c2_phase", "test1_v3", "RESULT.json"))
    if gates.add("C2c_phase_complete", new is not None and new.get("status") == "COMPLETE_PENDING_INDEPENDENT_AUDIT",
                 "IMPLEMENTATION"):
        for name in ("primary", "independent"):
            gates.add(f"C2c_{name}_phase_identical_to_archived", new["engines"][name]["phase_over_pi"]
                      == ref_phase["engines"][name]["phase_over_pi"], "IMPLEMENTATION")
    # C3: parameter-ball consumption at small non-degenerate balls around the anchor.
    old_centre = old_level["center"]["event_quantities"]
    for label, prefix, param in (("C3v", "c3v", "v1"), ("C3l", "c3l", "lambda_b")):
        for engine, calls_key, expected in (("bgp", "event_quantity_calls", 2 * 32768),
                                            ("bgi", "upper_quantity_calls", 2 * 8192)):
            record = load(os.path.join(jobs, f"{prefix}_{engine}", "stdout.json"))
            result = None if record is None else record.get("producer_result", record.get("engine_result"))
            if not gates.add(f"{label}_{engine}_complete", result is not None and result.get("status") == "COMPLETE",
                             "IMPLEMENTATION"):
                continue
            lo, hi = Q(record["job"]["lo"]), Q(record["job"]["hi"])
            plo, phi = pair(record["parameter_ball_exact_bounds"])
            gates.add(f"{label}_{engine}_nondegenerate_ball", plo <= lo < hi <= phi and record["job"]["param"] == param,
                      "IMPLEMENTATION")
            consumption_gates(gates, f"{label}_{engine}", record, record["job"], calls_key, expected)
            if engine == "bgp":
                row = result["all_results"][0]
                if param == "v1":
                    gates.add(f"{label}_primary_newton_image_strictly_contains_archived",
                              row["interval_newton_image"] is not None and strictly_contains(
                                  pair(row["interval_newton_image"]["exact_bounds"]),
                                  pair(narrow["interval_newton_image"]["exact_bounds"])), "IMPLEMENTATION")
                else:
                    gates.add(f"{label}_primary_box_bracket_strictly_contains_archived",
                              strictly_contains(pair(row["box_event"]["event_bracket"]), tuple(ARCHIVED_D)),
                              "IMPLEMENTATION")
            else:
                centre = result["levels"][0]["center"]["event_quantities"]
                key = "h" if param == "v1" else "G"
                new_width = Q(centre[key]["exact_bounds"][1]) - Q(centre[key]["exact_bounds"][0])
                old_width = Q(old_centre[key]["exact_bounds"][1]) - Q(old_centre[key]["exact_bounds"][0])
                gates.add(f"{label}_independent_centre_{key}_strictly_wider_than_archived", new_width > old_width,
                          "IMPLEMENTATION")
    failed = gates.failed()
    verdict = {"controls_pass": not failed, "gates": gates.rows, "failed": failed}
    with open(out_path, "w") as handle:
        json.dump(verdict, handle, indent=2, sort_keys=True)
    print(json.dumps({"controls_pass": not failed, "gate_count": len(gates.rows),
                      "failed": [row["gate"] for row in failed]}, indent=2))
    return 0 if not failed else 1


def main():
    mode = sys.argv[1]
    if mode == "controls":
        sys.exit(controls_mode(sys.argv[2], sys.argv[3], sys.argv[4]))
    family_mode(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


if __name__ == "__main__":
    main()
