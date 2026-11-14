"""Reporting only: assemble VERDICTS.json from the checker outputs (decides nothing).

usage: make_verdicts.py REVIEW_DIR
"""
import json
import os
import subprocess
import sys


def load(path):
    with open(path) as handle:
        return json.load(handle)


def compact(row):
    return {"subbox": row["subbox"], "verdict": row["verdict"], "param": row["param"], "interval": row["interval"],
            "extra_params": row.get("extra_params", []), "cell": row.get("cell"),
            "failed_gates": [[g["gate"], g["kind"], g.get("detail")] for g in row["failed_gates"]],
            "gate_count": row["gate_count"], "job_states": row["job_states"], "A_box": row["A_box"],
            "enclosures_exact": row["enclosures"], "phase_trace_summary": row["phase_trace_summary"]}


def main():
    review = sys.argv[1]
    prod = os.path.join(review, "runs", "production")
    wprod = os.path.join(review, "runs", "W", "production")
    out = {"schema": "verdicts-v1",
           "written_utc": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip(),
           "label": "Every verdict below was decided by the frozen exact-rational checkers; this file only collects them.",
           "controls": {"V_L": {"controls_pass": load(os.path.join(prod, "CONTROLS_VERDICT.json"))["controls_pass"],
                                "gate_count": len(load(os.path.join(prod, "CONTROLS_VERDICT.json"))["gates"])}},
           "families": dict(load(os.path.join(prod, "check", "FAMILY_VERDICT.json"))["families"]),
           "subboxes": [compact(r) for r in load(os.path.join(prod, "check", "SUBBOX_VERDICTS.json"))]}
    wcheck = os.path.join(wprod, "check_w", "FAMILY_VERDICT_W.json")
    if os.path.exists(wcheck):
        wcontrols = load(os.path.join(wprod, "CONTROLS_VERDICT_W.json"))
        out["controls"]["W"] = {"controls_pass": wcontrols["controls_pass"], "gate_count": len(wcontrols["gates"])}
        out["families"].update(load(wcheck)["families"])
        out["subboxes"] += [compact(r) for r in load(os.path.join(wprod, "check_w", "SUBBOX_VERDICTS_W.json"))]
    else:
        out["families"]["W"] = {"classification": "NOT_AVAILABLE"}
    with open(os.path.join(review, "VERDICTS.json"), "w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
    print(json.dumps({k: v.get("classification") for k, v in out["families"].items()}))


if __name__ == "__main__":
    main()
