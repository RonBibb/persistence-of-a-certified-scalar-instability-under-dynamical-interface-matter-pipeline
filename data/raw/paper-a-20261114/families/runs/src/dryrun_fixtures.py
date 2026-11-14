"""Pre-freeze dry-run fixtures (never part of production).

Builds, in a dry-run stage that already holds jobs_controls.json:
  T_00  the degenerate archived anchor (expected CERTIFIED);
  T_01  the degenerate anchor with an A-box shifted to exclude the archived
        root (expected NOT_CERTIFIED_PREDICATE, phase gates DEPENDENT);
  T_02  job directories marked as skipped at the launch cutoff (expected NOT_RUN);
  FX1   a phase-only feasibility fixture: the archived Newton image widened by
        1.5e-7 on each side and the archived wall interval widened by 1/100;
  FX2   a background feasibility fixture at the archived point with an A-box of
        half-width 3.9e-7 (the widest frozen design box).
FX1 and FX2 report only completion or abort and enclosure widths.

usage: dryrun_fixtures.py STAGE        (writes jobs_fixtures.json and BOXES_T.json)
       dryrun_fixtures.py report STAGE  (prints the FX implementation flags)
"""
import hashlib
import json
import os
import sys
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_jobs as bj  # noqa: E402

NARROW_IMAGE = (Q(456607025194779413, 4611686018427387904), Q(114151756532473697, 1152921504606846976))


def shifted_box():
    centre = float("0.09901086589880687") + 3e-9
    return {"A0": repr(centre), "A_lo": repr(centre - 1e-9), "A_hi": repr(centre + 1e-9)}


def wide_box():
    centre = float("0.09901086589880687")
    return {"A0": repr(centre), "A_lo": repr(centre - 3.9e-7), "A_hi": repr(centre + 3.9e-7)}


def build(stage):
    jobs = []
    anchor = dict(bj.ANCHOR_BOX, param="v1", lo=bj.ARCHIVED_V1, hi=bj.ARCHIVED_V1)
    jobs.append(bj.background_primary(stage, "bgp_T_00", anchor))
    jobs.append(bj.background_independent(stage, "bgi_T_00", anchor))
    jobs.append(bj.phase(stage, "ph_T_00", "bgp_T_00"))
    failing = dict(shifted_box(), param="v1", lo=bj.ARCHIVED_V1, hi=bj.ARCHIVED_V1)
    jobs.append(bj.background_primary(stage, "bgp_T_01", failing))
    jobs.append(bj.background_independent(stage, "bgi_T_01", failing))
    jobs.append(bj.phase(stage, "ph_T_01", "bgp_T_01"))
    skipped = dict(bj.ANCHOR_BOX, param="v1", lo=bj.ARCHIVED_V1, hi=bj.ARCHIVED_V1)
    for job in (bj.background_primary(stage, "bgp_T_02", skipped), bj.background_independent(stage, "bgi_T_02", skipped),
                bj.phase(stage, "ph_T_02", "bgp_T_02")):
        with open(os.path.join(job["dir"], "exec.json"), "w") as handle:
            json.dump({"job": job["name"], "status": "SKIPPED", "reason": "LAUNCH_CUTOFF_REACHED"}, handle)
    wide = dict(wide_box(), param="v1", lo=bj.ARCHIVED_V1, hi=bj.ARCHIVED_V1)
    jobs.append(bj.background_primary(stage, "fx2_bgp", wide))
    jobs.append(bj.background_independent(stage, "fx2_bgi", wide))
    fx1 = os.path.join(stage, "jobs", "fx1_phase")
    bj.make_dir(fx1)
    archived = os.path.join(stage, "archived_src", "phase")
    for rel in ("test1_phase_v3.py", "engine/primary_interval.py", "engine/independent_interval.py"):
        bj.copy(archived, rel, fx1, rel)
    bj.copy(os.path.join(stage, "src"), "boot.py", fx1)
    with open(os.path.join(archived, "inputs", "central_bindings.json")) as handle:
        binding = json.load(handle)
    pad = Q(3, 20000000)
    binding["config"]["A"] = [str(NARROW_IMAGE[0] - pad), str(NARROW_IMAGE[1] + pad)]
    binding["config"]["D"] = [str(Q(32727, 16384) - Q(1, 100)), str(Q(32729, 16384) + Q(1, 100))]
    os.makedirs(os.path.join(fx1, "inputs"))
    path = os.path.join(fx1, "inputs", "central_bindings.json")
    with open(path, "w") as handle:
        json.dump(binding, handle, indent=2, sort_keys=True)
    with open(os.path.join(archived, "SOURCE_BINDINGS.json")) as handle:
        sources = json.load(handle)
    with open(path, "rb") as handle:
        sources["inputs/central_bindings.json"]["sha256"] = hashlib.sha256(handle.read()).hexdigest()
    with open(os.path.join(fx1, "SOURCE_BINDINGS.json"), "w") as handle:
        json.dump(sources, handle, indent=2, sort_keys=True)
    jobs.append({"name": "fx1_phase", "dir": fx1, "entry": "test1_phase_v3.py", "deps": []})
    with open(os.path.join(stage, "jobs_fixtures.json"), "w") as handle:
        json.dump(jobs, handle, indent=2)
    boxes = {"families": {"T": {"param": "v1", "segment": [bj.ARCHIVED_V1, bj.ARCHIVED_V1], "anchor_subbox": 0,
                                "subboxes": [dict(anchor, j=0), dict(failing, j=1), dict(skipped, j=2)]}}}
    with open(os.path.join(stage, "BOXES_T.json"), "w") as handle:
        json.dump(boxes, handle, indent=1)


def width(bounds):
    return float(Q(bounds[1]) - Q(bounds[0]))


def report(stage):
    jobs = os.path.join(stage, "jobs")
    flags = {}
    result = json.load(open(os.path.join(jobs, "fx2_bgp", "stdout.json")))["producer_result"]
    row = result["all_results"][0] if result.get("all_results") else None
    flags["fx2_primary"] = {"status": result["status"], "error": result.get("error"),
                            "A_box_width": 7.8e-7,
                            "newton_image_width": None if not row or not row["interval_newton_image"] else row["interval_newton_image"]["width"],
                            "box_event_bracket_width": None if not row else width(row["box_event"]["event_bracket"]),
                            "hprime_bounds_width": None if not row else row["box_event"]["hprime_bounds"][1] - row["box_event"]["hprime_bounds"][0]}
    result = json.load(open(os.path.join(jobs, "fx2_bgi", "stdout.json")))["engine_result"]
    level = result["levels"][0] if result.get("levels") else None
    flags["fx2_independent"] = {"status": result["status"], "error": result.get("error"),
                                "newton_image_width": None if not level or not level["interval_newton_image"] else level["interval_newton_image"]["width"],
                                "T_b_enclosure_width": None if not level else level["root_box"]["event_quantities"]["S"]["width"],
                                "k_enclosure_width": None if not level else level["geometry"]["curvature"]["width"]}
    out = os.path.join(jobs, "fx1_phase", "test1_v3")
    failure = os.path.join(out, "FAILURE.json")
    if os.path.exists(failure):
        flags["fx1_phase"] = {"status": "ABORTED", "error": json.load(open(failure))["error"]}
    else:
        final = json.load(open(os.path.join(out, "RESULT.json")))
        flags["fx1_phase"] = {"status": final["status"], "engines": {
            name: {"phase_over_pi_width": width(engine["phase_over_pi"]["bounds"]), "event_pieces": len(engine["event"]),
                   "cells": engine["cells"]} for name, engine in final["engines"].items()}}
    print(json.dumps({"label": "FEASIBILITY_IMPLEMENTATION_FLAGS_ONLY", "flags": flags}, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "report":
        report(sys.argv[2])
    else:
        build(sys.argv[1])
