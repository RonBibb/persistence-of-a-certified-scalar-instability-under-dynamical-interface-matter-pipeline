"""Copy per-job records from the VM stage into runs/ and hash the large traces.

Runs on linux.vm.  For every job directory it copies exec.json, stdout.json,
stderr.txt, source_sha256.txt, prepare.json, job.json and the phase inputs
and results (not the multi-megabyte traces) into REVIEW/runs/jobs/<name>/.
Every trace file gets its SHA-256 and byte count recorded in
trace_hashes.json.  Existing destination files are never overwritten.

usage: collect_outputs.py STAGE REVIEW_RUNS
"""
import hashlib
import json
import os
import shutil
import sys

SMALL = ["exec.json", "stdout.json", "stderr.txt", "source_sha256.txt", "prepare.json", "job.json",
         "inputs/central_bindings.json", "SOURCE_BINDINGS.json", "test1_v3/RESULT.json",
         "test1_v3/primary_result.json", "test1_v3/independent_result.json", "test1_v3/FAILURE.json",
         "test1_v3/progress.json"]
TRACES = ["test1_v3/primary_trace.json", "test1_v3/independent_trace.json"]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    stage, runs = sys.argv[1:3]
    jobs = os.path.join(stage, "jobs")
    traces = {}
    for name in sorted(os.listdir(jobs)):
        src = os.path.join(jobs, name)
        if os.path.islink(src):
            continue
        dest = os.path.join(runs, "jobs", name)
        for rel in SMALL:
            path = os.path.join(src, rel)
            if os.path.exists(path):
                target = os.path.join(dest, rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if os.path.exists(target):
                    raise RuntimeError(f"refusing to overwrite {target}")
                shutil.copyfile(path, target)
        for rel in TRACES:
            path = os.path.join(src, rel)
            if os.path.exists(path):
                traces[f"{name}/{rel}"] = {"sha256": sha256(path), "bytes": os.path.getsize(path),
                                           "vm_path": path}
    with open(os.path.join(runs, "trace_hashes.json"), "w") as handle:
        json.dump(traces, handle, indent=1, sort_keys=True)
    print(json.dumps({"jobs": len(os.listdir(jobs)), "traces": len(traces)}))


if __name__ == "__main__":
    main()
