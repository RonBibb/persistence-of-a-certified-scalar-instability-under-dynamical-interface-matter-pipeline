"""Build the family W job directories and job lists in the W stage.

Reuses build_jobs.py (frozen for V and L) for the per-job directory layout.
Writes jobs_controls_w.json (C2w: both balls degenerate at the anchor;
C3w: v1 +- 2^-16 and lambda_b +- 2^-16 around the anchor) and jobs_family_w.json
(three jobs per frozen cell, ordered outward from the anchor cell).

usage: build_jobs_w.py STAGE_W BOXES_W_JSON
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_jobs as bj  # noqa: E402


def controls(stage):
    jobs = []
    degenerate = dict(bj.ANCHOR_BOX, param="v1", lo=bj.ARCHIVED_V1, hi=bj.ARCHIVED_V1,
                      extra_params=[["lambda_b", bj.ARCHIVED_LAMBDA_B, bj.ARCHIVED_LAMBDA_B]])
    jobs.append(dict(bj.background_primary(stage, "c2w_bgp", degenerate), priority=99))
    jobs.append(dict(bj.background_independent(stage, "c2w_bgi", degenerate), priority=99))
    jobs.append(dict(bj.phase(stage, "c2w_phase", "c2w_bgp"), priority=101))
    v1, lb = Fraction(bj.ARCHIVED_V1), Fraction(bj.ARCHIVED_LAMBDA_B)
    small = dict(bj.ANCHOR_BOX, param="v1", lo=str(v1 - Fraction(1, 2**16)), hi=str(v1 + Fraction(1, 2**16)),
                 extra_params=[["lambda_b", str(lb - Fraction(1, 2**16)), str(lb + Fraction(1, 2**16))]])
    jobs.append(dict(bj.background_primary(stage, "c3w_bgp", small), priority=98))
    jobs.append(dict(bj.background_independent(stage, "c3w_bgi", small), priority=98))
    return jobs


def family(stage, boxes):
    spec = boxes["families"]["W"]
    ai, ak = spec["anchor_cell"]
    jobs = []
    for entry in sorted(spec["subboxes"], key=lambda e: (abs(e["i"] - ai) + abs(e["k"] - ak), e["j"])):
        tag = f"W_{entry['j']:02d}"
        job = {key: entry[key] for key in ("param", "lo", "hi", "A0", "A_lo", "A_hi")}
        job["extra_params"] = entry["extra_params"]
        jobs.append(dict(bj.background_primary(stage, f"bgp_{tag}", job), priority=0))
        jobs.append(dict(bj.background_independent(stage, f"bgi_{tag}", job), priority=0))
        jobs.append(dict(bj.phase(stage, f"ph_{tag}", f"bgp_{tag}"), priority=1))
    return jobs


def main():
    stage, boxes_path = sys.argv[1], sys.argv[2]
    with open(boxes_path) as handle:
        boxes = json.load(handle)
    os.makedirs(os.path.join(stage, "jobs"), exist_ok=True)
    with open(os.path.join(stage, "jobs_controls_w.json"), "w") as handle:
        json.dump(controls(stage), handle, indent=2)
    if "--controls-only" not in sys.argv:
        with open(os.path.join(stage, "jobs_family_w.json"), "w") as handle:
            json.dump(family(stage, boxes), handle, indent=2)


if __name__ == "__main__":
    main()
