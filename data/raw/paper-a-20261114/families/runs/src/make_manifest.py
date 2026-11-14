"""Write OUTPUT_MANIFEST.json: full SHA-256 of every file this session produced.

Covers every file under the review folder except OUTPUT_MANIFEST.json and
CLOSEOUT.json (CLOSEOUT.json records this manifest's hash), the summary file,
and the VM-stage phase traces listed in runs/trace_hashes.json.  The draft
files and CURRENT_DRAFT.json are re-hashed to confirm they are unchanged.

usage: make_manifest.py REVIEW_DIR SUMMARY_PATH
"""
import hashlib
import json
import os
import subprocess
import sys

DRAFT = {
    "/Volumes/Research/papers/persistence-of-a-certified-scalar-instability-under-dynamical-interface-matter/CURRENT_DRAFT.json":
        "cc63f56cdf8b77b3d0ad0c76a6f1158d12c53e27cd94f4c7cfdfdabdffbb19f4",
    "/Volumes/Research/papers/persistence-of-a-certified-scalar-instability-under-dynamical-interface-matter/publication_updates/20261114_JMP_article_appendices_figures/manuscript/MAIN_ARTICLE.md":
        "1e5c1a989215be093bec4b78fb573405c4d6bf1cb21d9ccb67758a994076eb37",
    "/Volumes/Research/papers/persistence-of-a-certified-scalar-instability-under-dynamical-interface-matter/publication_updates/20261114_JMP_article_appendices_figures/manuscript/SUPPLEMENT.md":
        "b2f7280cc2e023a0698ff5997da13bb83a0937d57fc4c4dcac859914bde4b425",
}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    review, summary = sys.argv[1:3]
    files = []
    for root, dirs, names in os.walk(review):
        dirs.sort()
        for name in sorted(names):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, review)
            if rel in ("OUTPUT_MANIFEST.json", "CLOSEOUT.json") or name == ".DS_Store":
                continue
            files.append({"path": rel, "sha256": sha256(path), "bytes": os.path.getsize(path)})
    traces = {}
    for row in files:
        if os.path.basename(row["path"]) == "trace_hashes.json":
            with open(os.path.join(review, row["path"])) as handle:
                for key, value in json.load(handle).items():
                    traces[f"{os.path.dirname(row['path'])}::{key}"] = value
    record = {
        "schema": "output-manifest-v1",
        "written_utc": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip(),
        "review_folder": review,
        "review_folder_files": files,
        "summary_file": {"path": summary, "sha256": sha256(summary), "bytes": os.path.getsize(summary)}
        if os.path.exists(summary) else None,
        "vm_stage_phase_traces": traces,
        "draft_unchanged": {path: sha256(path) == expected for path, expected in DRAFT.items()},
    }
    with open(os.path.join(review, "OUTPUT_MANIFEST.json"), "w") as handle:
        json.dump(record, handle, indent=1, sort_keys=True)
    print(json.dumps({"files": len(files), "traces": len(traces), "draft_unchanged": record["draft_unchanged"]}, indent=1))


if __name__ == "__main__":
    main()
