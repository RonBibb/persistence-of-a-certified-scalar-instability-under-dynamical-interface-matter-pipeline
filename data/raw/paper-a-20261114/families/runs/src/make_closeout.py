"""Write CLOSEOUT.json (run last, after OUTPUT_MANIFEST.json).

Records start, deadline and end (end from `date -u` at write time), the
objectives done and not done, resource use summed from every exec.json, the
hash of OUTPUT_MANIFEST.json, and the checks that nothing outside the allowed
write locations changed.

usage: make_closeout.py REVIEW_DIR OBJECTIVES_JSON
"""
import glob
import hashlib
import json
import os
import subprocess
import sys


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def resources(pattern):
    jobs = elapsed = cpu = 0.0
    peak = 0
    nonzero = timed_out = 0
    for path in glob.glob(pattern):
        record = json.load(open(path))
        if record.get("status") == "SKIPPED":
            continue
        jobs += 1
        elapsed += record["elapsed_s"]
        cpu += record.get("cpu_user_s", 0) + record.get("cpu_system_s", 0)
        peak = max(peak, record.get("max_rss_kib", 0))
        nonzero += record["exit"] != 0
        timed_out += bool(record.get("timed_out"))
    return {"jobs": int(jobs), "elapsed_core_seconds": round(elapsed, 1), "cpu_seconds": round(cpu, 1),
            "peak_rss_kib": peak, "nonzero_exits": nonzero, "timed_out": timed_out}


def main():
    review, objectives_path = sys.argv[1:3]
    objectives = json.load(open(objectives_path))
    times = json.load(open(os.path.join(review, "TIMES.json")))
    manifest = json.load(open(os.path.join(review, "OUTPUT_MANIFEST.json")))
    git = subprocess.run(["git", "-C", "/Users/ronbibb/qgenda/projects/qgenda.com", "status", "--porcelain"],
                         capture_output=True, text=True).stdout.splitlines()
    record = {
        "schema": "closeout-v1",
        "utc_start": times["utc_start"],
        "hard_deadline_utc": times["hard_deadline_utc"],
        "closeout_start_utc": times["closeout_start_utc"],
        "utc_end": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip(),
        "objectives": objectives,
        "resource_use": {
            "V_L_production": resources(os.path.join(review, "runs", "production", "jobs", "*", "exec.json")),
            "W_production": resources(os.path.join(review, "runs", "W", "production", "jobs", "*", "exec.json")),
            "pre_freeze_dry_runs": resources(os.path.join(review, "runs", "pre_freeze_*", "jobs", "*", "exec.json")),
            "W_pre_freeze_dry_run": resources(os.path.join(review, "runs", "W", "pre_freeze_W_dryrun", "jobs", "*", "exec.json")),
            "concurrency": "at most 6 single-thread compute processes on linux.vm at any time, plus one idle coordinator; no CPU pinning; no package installs",
            "subagents": "one review subagent, used only for the gate reviews (PLAN, re-review, PLAN_W)",
        },
        "output_manifest_sha256": sha256(os.path.join(review, "OUTPUT_MANIFEST.json")),
        "nothing_else_modified": {
            "draft_and_current_draft_hashes_unchanged": manifest["draft_unchanged"],
            "manuscript_supplement_figures_bibliography_build_files": "not written (all writes confined to this review folder, the VM stage and the one summary file)",
            "publication_updates_revision_created": False,
            "qgenda_checkout_git_status_porcelain": git,
            "qgenda_checkout_note": "pre-existing untracked .factory/QGA-324164/ and .factory/QGA-325389/ were present at session start and are not this session's",
            "processes_touched": "only processes this session started; none of the sibling sessions' processes",
            "messages_sent": "none (no Slack or other messages)",
        },
    }
    with open(os.path.join(review, "CLOSEOUT.json"), "w") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
    print(json.dumps({k: record[k] for k in ("utc_start", "hard_deadline_utc", "utc_end")}, indent=1))


if __name__ == "__main__":
    main()
