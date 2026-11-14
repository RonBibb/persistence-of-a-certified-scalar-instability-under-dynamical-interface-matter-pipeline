"""Exact-rational gates for family W (a 2-D box in v1 x lambda_b) and its controls.

Reuses check_family.py (frozen for V and L) unchanged and extends it:
  - consumption gates for every parameter ball (v1 and lambda_b together);
  - outwardness of the extra ball (P2x / I2x) and the independent engine's own
    centre-width evidence for both balls (R3, R3x);
  - a 2-D family verdict: the component is the set of certified cells joined
    to the anchor cell by passing edge seams; the one-branch claim is made only
    if every edge and every diagonal (corner) contact between component cells
    passes, otherwise the component cells are certified pointwise only;
  - W controls: the V/L production controls verdict (environment), C2w (both
    balls degenerate at the anchor, byte-identical to the archive) and C3w
    (both balls small and non-degenerate, consumption shown in both engines).

usage: check_family_w.py controls STAGE_W ARCHIVED_REFS VL_CONTROLS_VERDICT OUT_JSON
       check_family_w.py family   STAGE_W ARCHIVED_REFS BOXES_W_JSON OUT_DIR
"""
import json
import os
import sys
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_family as cf  # noqa: E402

GAMMA = Q(20)
ARCHIVED_D = (Q(32727, 16384), Q(32729, 16384))


def all_balls(record, job):
    plo, phi = cf.pair(record["parameter_ball_exact_bounds"])
    balls = [(job["param"], (phi - plo) / 2)]
    for name, lo, hi in record.get("extra_parameter_balls_exact_bounds", []):
        balls.append((name, (Q(hi) - Q(lo)) / 2))
    return balls


def consumption_gates_w(gates, label, record, job, calls_key, expected_calls):
    consumption = record.get("consumption") or {}
    gates.add(f"{label}_consumption_calls", consumption.get(calls_key) == expected_calls, "IMPLEMENTATION",
              consumption.get(calls_key))
    recorded = record.get("extra_parameter_balls_exact_bounds", [])
    expected = job.get("extra_params", [])
    gates.add(f"{label}x_extra_parameter_count", len(recorded) == len(expected), "IMPLEMENTATION")
    for name, lo, hi in expected:
        match = [row for row in recorded if row[0] == name]
        ok = len(match) == 1 and Q(match[0][1]) <= Q(lo) and Q(hi) <= Q(match[0][2])
        gates.add(f"{label}x_{name}_ball_outward", ok, "IMPLEMENTATION")
    for name, radius in all_balls(record, job):
        if name == "v1":
            observed = consumption.get("min_radius_h")
            ok = observed is not None and Q(observed) >= (GAMMA / 2) * radius * cf.SLACK
        else:
            observed = consumption.get("min_radius_G")
            ok = observed is not None and Q(observed) >= radius / 6 * cf.SLACK
        gates.add(f"{label}_{name}_ball_consumed_every_call", ok, "IMPLEMENTATION", observed)
    if "engine_result" in record and record["engine_result"].get("levels"):
        centre = record["engine_result"]["levels"][0]["center"]["event_quantities"]
        for name, radius in all_balls(record, job)[1:]:
            key, need = ("h", GAMMA * radius) if name == "v1" else ("G", radius / 3)
            width = Q(centre[key]["exact_bounds"][1]) - Q(centre[key]["exact_bounds"][0])
            gates.add(f"R3x_independent_centre_{key}_width_shows_{name}_ball", width >= need * cf.SLACK,
                      "IMPLEMENTATION")


cf.consumption_gates = consumption_gates_w


def job_of(entry):
    job = {key: entry[key] for key in ("param", "lo", "hi", "A0", "A_lo", "A_hi")}
    job["extra_params"] = entry["extra_params"]
    return job


def family_mode(stage, refs, boxes_path, out_dir):
    boxes = cf.load(boxes_path)
    frozen = cf.load(os.path.join(stage, "FROZEN_SOURCES.json"))
    reference_model = cf.load(os.path.join(refs, "central_bindings.json"))["model_exact"]
    spec = boxes["families"]["W"]
    ni, nk = spec["shape"]
    rows = {}
    for entry in spec["subboxes"]:
        row = cf.subbox(stage, job_of(entry), "W", entry["j"], frozen, reference_model)
        row["extra_params"] = entry["extra_params"]
        row["cell"] = [entry["i"], entry["k"]]
        rows[(entry["i"], entry["k"])] = row
    certified = {key for key, row in rows.items() if row["verdict"] == "CERTIFIED"}
    # Contacts: edge neighbours share an edge, diagonal neighbours share only a
    # corner point.  seam_ok is valid at every shared parameter point, so a
    # passing contact ties the two cells' roots on all of their common points.
    contacts = {}
    for (i, k) in rows:
        for (di, dk) in ((1, 0), (0, 1), (1, 1), (1, -1)):
            other = (i + di, k + dk)
            if other in rows:
                contacts[((i, k), other)] = (cf.seam_ok(rows[(i, k)], rows[other])
                                             if (i, k) in certified and other in certified else None)
    edges = {pair: ok for pair, ok in contacts.items()
             if abs(pair[0][0] - pair[1][0]) + abs(pair[0][1] - pair[1][1]) == 1}
    anchor = tuple(spec["anchor_cell"])
    component = set()
    if anchor in certified:
        stack = [anchor]
        component.add(anchor)
        while stack:
            cell = stack.pop()
            for (a, b), ok in edges.items():
                if ok and cell in (a, b):
                    nxt = b if cell == a else a
                    if nxt not in component:
                        component.add(nxt)
                        stack.append(nxt)
    internal = {pair: ok for pair, ok in contacts.items() if pair[0] in component and pair[1] in component}
    untied = [[rows[a]["subbox"], rows[b]["subbox"]] for (a, b), ok in internal.items() if not ok]
    if len(certified) == len(rows) and all(contacts.values()):
        classification = "FAMILY_CERTIFIED_FULL_BOX"
    elif component and not untied:
        classification = "FAMILY_CERTIFIED_CELL_COMPONENT"
    elif component:
        classification = "FAMILY_CERTIFIED_CELLS_POINTWISE_ONLY"
    else:
        classification = "FAMILY_NOT_CERTIFIED_AT_ANCHOR_CELL"
    hulls = [rows[c]["enclosures"]["theta_b_over_pi_hull"] for c in component]
    report = {"families": {"W": {
        "params": ["v1", "lambda_b"], "frozen_box": spec["box"], "shape": [ni, nk], "cells": len(rows),
        "certified_cells": len(certified), "anchor_cell": rows[anchor]["subbox"],
        "anchor_cell_verdict": rows[anchor]["verdict"], "classification": classification,
        "component_containing_anchor": sorted(rows[c]["subbox"] for c in component),
        "certified_cells_outside_component": sorted(rows[c]["subbox"] for c in certified - component),
        "not_certified_cells": sorted(row["subbox"] for key, row in rows.items() if key not in certified),
        "contacts_failed_between_certified_neighbours": [[rows[a]["subbox"], rows[b]["subbox"]]
                                                         for (a, b), ok in contacts.items() if ok is False],
        "untied_contacts_inside_component": untied,
        "branch_continuous_on_component": bool(component) and not untied,
        "contacts_checked_inside_component": len(internal),
        "verdict_counts": {v: sum(1 for r in rows.values() if r["verdict"] == v)
                           for v in sorted({r["verdict"] for r in rows.values()})},
        "theta_b_over_pi_hull_over_component": None if not hulls else
        [str(min(Q(h[0]) for h in hulls)), str(max(Q(h[1]) for h in hulls))],
    }}}
    with open(os.path.join(out_dir, "SUBBOX_VERDICTS_W.json"), "w") as handle:
        json.dump([rows[key] for key in sorted(rows, key=lambda c: (c[1], c[0]))], handle, indent=1, sort_keys=True)
    with open(os.path.join(out_dir, "FAMILY_VERDICT_W.json"), "w") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2, sort_keys=True))


def controls_mode(stage, refs, vl_verdict_path, out_path):
    gates = cf.Gates()
    jobs = os.path.join(stage, "jobs")
    vl = cf.load(vl_verdict_path)
    gates.add("CW0_vl_production_controls_passed", vl is not None and vl.get("controls_pass") is True,
              "IMPLEMENTATION")
    if vl is not None:
        c1 = [row for row in vl["gates"] if row["gate"].startswith(("C0_", "C1"))]
        gates.add("CW0_vl_c1_environment_gates_present_and_passed", bool(c1) and all(r["pass"] for r in c1),
                  "IMPLEMENTATION")
    ref_primary = cf.load(os.path.join(refs, "primary_RESULT.json"))
    ref_independent = cf.load(os.path.join(refs, "independent_RESULT.json"))
    ref_phase = cf.load(os.path.join(refs, "phase_RESULT.json"))
    ref_binding = cf.load(os.path.join(refs, "central_bindings.json"))
    narrow = {(r["box_name"], r["steps"]): r for r in ref_primary["all_results"]}[("narrow", 32768)]
    old_level = {lv["steps"]: lv for lv in ref_independent["levels"]}[8192]
    new = cf.load(os.path.join(jobs, "c2w_bgp", "stdout.json"))
    if gates.add("C2wa_primary_present", new is not None and new["producer_result"].get("status") == "COMPLETE",
                 "IMPLEMENTATION"):
        row = new["producer_result"]["all_results"][0]
        for key in ("interval_newton_image", "box_event", "center_event", "strict_self_map",
                    "qualified_newton_inclusion"):
            gates.add(f"C2wa_{key}_identical_to_archived_narrow", row[key] == narrow[key], "IMPLEMENTATION")
        gates.add("C2wa_two_balls_recorded", len(new.get("extra_parameter_balls_exact_bounds", [])) == 1,
                  "IMPLEMENTATION")
    new = cf.load(os.path.join(jobs, "c2w_bgi", "stdout.json"))
    if gates.add("C2wb_independent_present", new is not None and new["engine_result"].get("status") == "COMPLETE",
                 "IMPLEMENTATION"):
        level = new["engine_result"]["levels"][0]
        for key in ("interval_newton_image", "strict_self_map", "root_replay_pass"):
            gates.add(f"C2wb_{key}_identical_to_archived_8192", level[key] == old_level[key], "IMPLEMENTATION")
        gates.add("C2wb_root_box_quantities_identical",
                  level["root_box"]["event_quantities"] == old_level["root_box"]["event_quantities"], "IMPLEMENTATION")
        gates.add("C2wb_two_balls_recorded", len(new.get("extra_parameter_balls_exact_bounds", [])) == 1,
                  "IMPLEMENTATION")
    binding = cf.load(os.path.join(jobs, "c2w_phase", "inputs", "central_bindings.json"))
    if gates.add("C2wc_binding_present", binding is not None, "IMPLEMENTATION"):
        for key in ("A", "D"):
            gates.add(f"C2wc_binding_{key}_equals_archived",
                      cf.pair(binding["config"][key]) == cf.pair(ref_binding["config"][key]), "IMPLEMENTATION")
        gates.add("C2wc_binding_model_equals_archived", binding["model_exact"] == ref_binding["model_exact"],
                  "IMPLEMENTATION")
    new = cf.load(os.path.join(jobs, "c2w_phase", "test1_v3", "RESULT.json"))
    if gates.add("C2wc_phase_complete", new is not None and new.get("status") == "COMPLETE_PENDING_INDEPENDENT_AUDIT",
                 "IMPLEMENTATION"):
        for name in ("primary", "independent"):
            gates.add(f"C2wc_{name}_phase_identical_to_archived",
                      new["engines"][name]["phase_over_pi"] == ref_phase["engines"][name]["phase_over_pi"],
                      "IMPLEMENTATION")
    old_centre = old_level["center"]["event_quantities"]
    for engine, calls_key, expected in (("bgp", "event_quantity_calls", 2 * 32768),
                                        ("bgi", "upper_quantity_calls", 2 * 8192)):
        record = cf.load(os.path.join(jobs, f"c3w_{engine}", "stdout.json"))
        result = None if record is None else record.get("producer_result", record.get("engine_result"))
        if not gates.add(f"C3w_{engine}_complete", result is not None and result.get("status") == "COMPLETE",
                         "IMPLEMENTATION"):
            continue
        consumption_gates_w(gates, f"C3w_{engine}", record, record["job"], calls_key, expected)
        if engine == "bgp":
            row = result["all_results"][0]
            gates.add("C3w_primary_newton_image_strictly_contains_archived",
                      row["interval_newton_image"] is not None and cf.strictly_contains(
                          cf.pair(row["interval_newton_image"]["exact_bounds"]),
                          cf.pair(narrow["interval_newton_image"]["exact_bounds"])), "IMPLEMENTATION")
            gates.add("C3w_primary_box_bracket_strictly_contains_archived",
                      cf.strictly_contains(cf.pair(row["box_event"]["event_bracket"]), ARCHIVED_D), "IMPLEMENTATION")
        else:
            centre = result["levels"][0]["center"]["event_quantities"]
            for key in ("h", "G"):
                new_width = Q(centre[key]["exact_bounds"][1]) - Q(centre[key]["exact_bounds"][0])
                old_width = Q(old_centre[key]["exact_bounds"][1]) - Q(old_centre[key]["exact_bounds"][0])
                gates.add(f"C3w_independent_centre_{key}_strictly_wider_than_archived", new_width > old_width,
                          "IMPLEMENTATION")
    failed = gates.failed()
    with open(out_path, "w") as handle:
        json.dump({"controls_pass": not failed, "gates": gates.rows, "failed": failed}, handle, indent=2,
                  sort_keys=True)
    print(json.dumps({"controls_pass": not failed, "gate_count": len(gates.rows),
                      "failed": [row["gate"] for row in failed]}, indent=2))
    return 0 if not failed else 1


def main():
    if sys.argv[1] == "controls":
        sys.exit(controls_mode(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    family_mode(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


if __name__ == "__main__":
    main()
