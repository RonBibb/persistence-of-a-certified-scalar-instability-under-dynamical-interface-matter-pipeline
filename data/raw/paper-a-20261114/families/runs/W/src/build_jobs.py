"""Build the job directories and job lists in the VM stage.

Archived sources are copied byte for byte from STAGE/archived_src; the family
wrappers and bootstrap come from STAGE/src.  Writes jobs_controls.json (the
archived chain C1, the degenerate-anchor family pipeline C2, and the small
non-degenerate consumption controls C3v and C3l) and jobs_family.json (three
jobs per frozen sub-box).  Phase jobs get their binding from the primary
record of the same sub-box through make_phase_binding.py.

usage: build_jobs.py STAGE BOXES_JSON [--dry-run-anchor-only]
"""
import json
import os
import shutil
import sys
from fractions import Fraction

ARCHIVED_V1 = "6520040733916207/72057594037927936"
ARCHIVED_LAMBDA_B = "-851862101055633/140737488355328"
ANCHOR_BOX = {"A0": "0.09901086589880687", "A_lo": "0.09901086489880687", "A_hi": "0.09901086689880687"}


def copy(src_root, rel, dest_dir, dest_rel=None):
    target = os.path.join(dest_dir, dest_rel or os.path.basename(rel))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(os.path.join(src_root, rel), target)


def make_dir(path):
    if os.path.exists(path):
        raise RuntimeError(f"JOB_DIR_EXISTS {path}")
    os.makedirs(path)


def background_primary(stage, name, job):
    d = os.path.join(stage, "jobs", name)
    make_dir(d)
    archived = os.path.join(stage, "archived_src")
    copy(archived, "background/primary/validated_sensitivity_newton.py", d)
    copy(archived, "background/primary/confirm_32768.py", d)
    copy(os.path.join(stage, "src"), "fam_bg_primary.py", d)
    copy(os.path.join(stage, "src"), "boot.py", d)
    with open(os.path.join(d, "job.json"), "w") as handle:
        json.dump(job, handle, indent=2, sort_keys=True)
    return {"name": name, "dir": d, "entry": "fam_bg_primary.py", "deps": []}


def background_independent(stage, name, job):
    d = os.path.join(stage, "jobs", name)
    make_dir(d)
    archived = os.path.join(stage, "archived_src")
    copy(archived, "background/independent/independent_d1_replay.py", d)
    copy(os.path.join(stage, "src"), "fam_bg_independent.py", d)
    copy(os.path.join(stage, "src"), "boot.py", d)
    with open(os.path.join(d, "job.json"), "w") as handle:
        json.dump(job, handle, indent=2, sort_keys=True)
    return {"name": name, "dir": d, "entry": "fam_bg_independent.py", "deps": []}


def phase(stage, name, primary_name):
    d = os.path.join(stage, "jobs", name)
    make_dir(d)
    archived = os.path.join(stage, "archived_src", "phase")
    copy(archived, "test1_phase_v3.py", d)
    copy(archived, "engine/primary_interval.py", d, "engine/primary_interval.py")
    copy(archived, "engine/independent_interval.py", d, "engine/independent_interval.py")
    copy(os.path.join(stage, "src"), "boot.py", d)
    primary_record = os.path.join(stage, "jobs", primary_name, "stdout.json")
    prepare = {"script": os.path.join(stage, "src", "make_phase_binding.py"),
               "args": [primary_record, os.path.join(archived, "inputs", "central_bindings.json"),
                        os.path.join(archived, "SOURCE_BINDINGS.json"), d]}
    return {"name": name, "dir": d, "entry": "test1_phase_v3.py", "deps": [primary_name], "prepare": prepare}


def controls(stage):
    jobs = []
    archived = os.path.join(stage, "archived_src")
    d = os.path.join(stage, "jobs", "ctl_bgp")
    make_dir(d)
    copy(archived, "background/primary/validated_sensitivity_newton.py", d)
    copy(archived, "background/primary/confirm_32768.py", d)
    copy(os.path.join(stage, "src"), "boot.py", d)
    jobs.append({"name": "ctl_bgp", "dir": d, "entry": "confirm_32768.py", "deps": [], "priority": 100})
    d = os.path.join(stage, "jobs", "ctl_bgi")
    make_dir(d)
    copy(archived, "background/independent/independent_d1_replay.py", d)
    copy(archived, "background/independent/independent_d1_replay_r1.py", d)
    copy(os.path.join(stage, "src"), "boot.py", d)
    jobs.append({"name": "ctl_bgi", "dir": d, "entry": "independent_d1_replay_r1.py", "deps": [], "priority": 100})
    d = os.path.join(stage, "jobs", "ctl_phase")
    make_dir(d)
    for rel in ("test1_phase_v3.py", "SOURCE_BINDINGS.json"):
        copy(os.path.join(archived, "phase"), rel, d)
    for rel in ("engine/primary_interval.py", "engine/independent_interval.py", "inputs/central_bindings.json"):
        copy(os.path.join(archived, "phase"), rel, d, rel)
    copy(os.path.join(stage, "src"), "boot.py", d)
    jobs.append({"name": "ctl_phase", "dir": d, "entry": "test1_phase_v3.py", "deps": [], "priority": 100})
    anchor = dict(ANCHOR_BOX, param="v1", lo=ARCHIVED_V1, hi=ARCHIVED_V1)
    jobs.append(dict(background_primary(stage, "c2_bgp", anchor), priority=99))
    jobs.append(dict(background_independent(stage, "c2_bgi", anchor), priority=99))
    jobs.append(dict(phase(stage, "c2_phase", "c2_bgp"), priority=101))
    v1, lb = Fraction(ARCHIVED_V1), Fraction(ARCHIVED_LAMBDA_B)
    small_v1 = dict(ANCHOR_BOX, param="v1", lo=str(v1 - Fraction(1, 2**30)), hi=str(v1 + Fraction(1, 2**30)))
    small_lb = dict(ANCHOR_BOX, param="lambda_b", lo=str(lb - Fraction(1, 2**16)), hi=str(lb + Fraction(1, 2**16)))
    for prefix, job in (("c3v", small_v1), ("c3l", small_lb)):
        jobs.append(dict(background_primary(stage, f"{prefix}_bgp", job), priority=98))
        jobs.append(dict(background_independent(stage, f"{prefix}_bgi", job), priority=98))
    return jobs


def family(stage, boxes):
    jobs = []
    for fam, spec in boxes["families"].items():
        base = spec["priority"]
        anchor = spec["anchor_subbox"]
        for entry in sorted(spec["subboxes"], key=lambda e: (abs(e["j"] - anchor), e["j"])):
            tag = f"{fam}_{entry['j']:02d}"
            job = {key: entry[key] for key in ("param", "lo", "hi", "A0", "A_lo", "A_hi")}
            jobs.append(dict(background_primary(stage, f"bgp_{tag}", job), priority=base))
            jobs.append(dict(background_independent(stage, f"bgi_{tag}", job), priority=base))
            jobs.append(dict(phase(stage, f"ph_{tag}", f"bgp_{tag}"), priority=base + 1))
    return jobs


def main():
    stage, boxes_path = sys.argv[1], sys.argv[2]
    with open(boxes_path) as handle:
        boxes = json.load(handle)
    os.makedirs(os.path.join(stage, "jobs"), exist_ok=True)
    with open(os.path.join(stage, "jobs_controls.json"), "w") as handle:
        json.dump(controls(stage), handle, indent=2)
    if "--dry-run-anchor-only" not in sys.argv:
        with open(os.path.join(stage, "jobs_family.json"), "w") as handle:
            json.dump(family(stage, boxes), handle, indent=2)


if __name__ == "__main__":
    main()
