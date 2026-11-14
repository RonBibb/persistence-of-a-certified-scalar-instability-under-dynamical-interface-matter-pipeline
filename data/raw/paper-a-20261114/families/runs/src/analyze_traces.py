"""Target C notes only (post-hoc reporting; decides no verdict).

Reads the saved whole-cell phase traces of every phase job.  Each trace row
holds an outward 2^-40 rounding of a certified whole-cell chart angle / pi,
so the hulls below are rigorous bounds on the lifted zero-mass phase along
the whole computed trajectory, for every launch in that job's A interval.

usage: analyze_traces.py STAGE OUT_JSON
"""
import json
import os
import sys
from fractions import Fraction as Q


def summarize(path):
    with open(path) as handle:
        trace = json.load(handle)
    kinds = {}
    after_first = None
    for row in trace:
        kinds[row["chart"]] = kinds.get(row["chart"], 0) + 1
        if row["cell"] >= 1:
            a, b = Q(row["arc_over_pi"][0]), Q(row["arc_over_pi"][1])
            after_first = (a, b) if after_first is None else (min(after_first[0], a), max(after_first[1], b))
    charts_after_first = sorted({row["chart"] for row in trace if row["cell"] >= 1})
    return {"cells": len(trace), "chart_counts": kinds, "charts_on_cells_ge_1": charts_after_first,
            "arc_over_pi_hull_cells_ge_1": [str(after_first[0]), str(after_first[1])],
            "arc_over_pi_hull_cells_ge_1_decimal_rounding": [float(after_first[0]), float(after_first[1])]}


def main():
    stage, out = sys.argv[1:3]
    rows = {}
    jobs = os.path.join(stage, "jobs")
    for name in sorted(os.listdir(jobs)):
        if not (name.startswith("ph_") or name in ("ctl_phase", "c2_phase")):
            continue
        entry = {}
        for engine in ("primary", "independent"):
            path = os.path.join(jobs, name, "test1_v3", f"{engine}_trace.json")
            if os.path.exists(path):
                entry[engine] = summarize(path)
        rows[name] = entry
    lows = [Q(e["arc_over_pi_hull_cells_ge_1"][0]) for r in rows.values() for e in r.values()]
    highs = [Q(e["arc_over_pi_hull_cells_ge_1"][1]) for r in rows.values() for e in r.values()]
    only_left = all(e["charts_on_cells_ge_1"] == ["left"] for r in rows.values() for e in r.values())
    report = {"label": "POST_HOC_TRACE_ANALYSIS_TARGET_C_NOTES",
              "jobs": rows,
              "all_cells_ge_1_use_only_the_L_negative_chart": only_left,
              "global_arc_over_pi_hull_cells_ge_1": None if not lows else [str(min(lows)), str(max(highs))]}
    with open(out, "w") as handle:
        json.dump(report, handle, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in report.items() if k != "jobs"}, indent=2))


if __name__ == "__main__":
    main()
