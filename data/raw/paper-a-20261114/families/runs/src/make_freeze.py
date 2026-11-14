"""Write FREEZE.json, FROZEN_SOURCES.json and the stage manifest FROZEN_STAGE.sha256.

FROZEN_STAGE.sha256 lists, in `sha256sum -c` format and at their VM-stage
paths, every file the production run reads from the stage: src/*, the box
table, the archived sources and references, and FROZEN_SOURCES.json.
run_production.sh refuses to start unless the stage matches it.  The UTC
stamp comes from `date -u` at write time.

usage: make_freeze.py REVIEW_DIR
"""
import hashlib
import json
import os
import subprocess
import sys

FROZEN = ["boot.py", "fam_bg_primary.py", "fam_bg_independent.py", "make_phase_binding.py", "run_jobs.py",
          "build_jobs.py", "check_family.py", "run_production.sh", "make_family_boxes.py"]
ARCHIVED = {
    "archived_src/background/primary/validated_sensitivity_newton.py": "9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653",
    "archived_src/background/primary/confirm_32768.py": "98d17ad555c7012266debe9e406fab02eae6db6b57dbe41c53dc635c66e7fe09",
    "archived_src/background/independent/independent_d1_replay.py": "d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044",
    "archived_src/background/independent/independent_d1_replay_r1.py": "25e90b9b881787f8fd3d7f4e93bf2fb05ea64e2e30534f511c99b9911bdfe043",
    "archived_src/phase/test1_phase_v3.py": "9f2da0122d8f411365c8703f12d1342c8c70da83b79a1976dd80824c9864d816",
    "archived_src/phase/engine/primary_interval.py": "b4201caa2934905b0a2de198cd6eba2c2d08131a0d496d8da76ac3dc3c8c92d2",
    "archived_src/phase/engine/independent_interval.py": "260150e6371209bc3eac1834e7be2c97b4d7e582338cd567c82843a4f44efbeb",
    "archived_src/phase/inputs/central_bindings.json": "9d5267d65c8a2b07e0db0015e5e281c5e0316c20d4386eedf6e667e43ba5eeaf",
    "archived_src/phase/SOURCE_BINDINGS.json": "9ae6145544757d3b47883ef2008b29ac0d4489b48617807be1d6a88782f964a9",
    "archived_refs/primary_RESULT.json": "2fa1de3ee74107f4c55bcb96722d1846e814caf599fb1a97b8106e556224019d",
    "archived_refs/independent_RESULT.json": "23c7ffce194523313bd99037f3e046e560dc48648fc2e41fe9dcaf9a04a6c501",
    "archived_refs/phase_RESULT.json": "967806f7e33743f126d688e3a4df94d51ec149ae97715359a13ccebe21d8f1ba",
    "archived_refs/central_bindings.json": "9d5267d65c8a2b07e0db0015e5e281c5e0316c20d4386eedf6e667e43ba5eeaf",
}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    review = sys.argv[1]
    src = os.path.join(review, "runs", "src")
    frozen = {name: sha256(os.path.join(src, name)) for name in FROZEN}
    frozen_sources = {name: value for name, value in frozen.items() if name.endswith(".py")}
    sources_path = os.path.join(review, "runs", "FROZEN_SOURCES.json")
    with open(sources_path, "w") as handle:
        json.dump(frozen_sources, handle, indent=2, sort_keys=True)
    boxes = sha256(os.path.join(src, "FAMILY_BOXES.json"))
    stage_lines = [f"{value}  src/{name}" for name, value in sorted(frozen.items())]
    stage_lines.append(f"{boxes}  FAMILY_BOXES.json")
    stage_lines.append(f"{sha256(sources_path)}  FROZEN_SOURCES.json")
    stage_lines += [f"{value}  {path}" for path, value in sorted(ARCHIVED.items())]
    manifest_path = os.path.join(review, "runs", "FROZEN_STAGE.sha256")
    with open(manifest_path, "w") as handle:
        handle.write("\n".join(stage_lines) + "\n")
    record = {
        "schema": "freeze-v2",
        "frozen_utc": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip(),
        "plan": {"path": "PLAN.md", "sha256": sha256(os.path.join(review, "PLAN.md"))},
        "gate_review": {"path": "GATE_REVIEW.md", "sha256": sha256(os.path.join(review, "GATE_REVIEW.md"))},
        "frozen_sources": {f"runs/src/{name}": value for name, value in frozen.items()},
        "frozen_box_table": {"runs/src/FAMILY_BOXES.json": boxes},
        "frozen_sources_json": {"runs/FROZEN_SOURCES.json": sha256(sources_path)},
        "stage_manifest": {"runs/FROZEN_STAGE.sha256": sha256(manifest_path)},
        "archived_sources_and_references_in_vm_stage": ARCHIVED,
        "vm_stage": "/home/parallels/claude-second-bg-20261114T055250Z",
        "production_entry": "bash src/run_production.sh (detached, in the VM stage); it first runs sha256sum -c FROZEN_STAGE.sha256",
        "rule": "No radius, step, box width, segment, point or precision change after this record; failed inclusions are kept and reported; nothing is rescored.",
    }
    with open(os.path.join(review, "FREEZE.json"), "w") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
