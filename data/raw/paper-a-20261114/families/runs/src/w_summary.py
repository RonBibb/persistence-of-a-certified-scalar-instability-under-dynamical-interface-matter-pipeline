"""Reporting only: summarize family W from its checker outputs (decides nothing).

usage: w_summary.py W_PRODUCTION_DIR
"""
import json
import os
import sys
from fractions import Fraction as Q


def main():
    d = sys.argv[1]
    fam = json.load(open(os.path.join(d, "check_w", "FAMILY_VERDICT_W.json")))["families"]["W"]
    rows = json.load(open(os.path.join(d, "check_w", "SUBBOX_VERDICTS_W.json")))
    cert = [r for r in rows if r["verdict"] == "CERTIFIED"]
    out = {"classification": fam["classification"], "cells": fam["cells"], "certified_cells": fam["certified_cells"],
           "anchor_cell": fam["anchor_cell"], "anchor_cell_verdict": fam["anchor_cell_verdict"],
           "component_size": len(fam["component_containing_anchor"]),
           "branch_continuous_on_component": fam["branch_continuous_on_component"],
           "contacts_checked_inside_component": fam["contacts_checked_inside_component"],
           "untied_contacts_inside_component": fam["untied_contacts_inside_component"],
           "contacts_failed_between_certified_neighbours": fam["contacts_failed_between_certified_neighbours"],
           "not_certified_cells": fam["not_certified_cells"],
           "certified_cells_outside_component": fam["certified_cells_outside_component"],
           "verdict_counts": fam["verdict_counts"],
           "theta_hull_component_exact": fam["theta_b_over_pi_hull_over_component"]}
    if cert:
        out["theta_hull_all_certified_decimal"] = [float(min(Q(r["enclosures"]["theta_b_over_pi_hull"][0]) for r in cert)),
                                                    float(max(Q(r["enclosures"]["theta_b_over_pi_hull"][1]) for r in cert))]
        out["T_b_lower_min_decimal"] = float(min(Q(r["enclosures"]["T_b"][0]) for r in cert))
        out["k_lower_min_decimal"] = float(min(Q(r["enclosures"]["k"][0]) for r in cert))
        charts, lo, hi = set(), None, None
        for r in cert:
            for s in r["phase_trace_summary"].values():
                charts |= set(s["charts_on_cells_ge_1"])
                a, b = Q(s["arc_over_pi_hull_cells_ge_1"][0]), Q(s["arc_over_pi_hull_cells_ge_1"][1])
                lo = a if lo is None else min(lo, a)
                hi = b if hi is None else max(hi, b)
        out["charts_on_cells_ge_1"] = sorted(charts)
        out["arc_hull_cells_ge_1"] = [str(lo), str(hi), float(lo), float(hi)]
        out["failed_gate_kinds"] = sorted({(g["gate"], g["kind"]) for r in rows for g in r["failed_gates"]})
    print(json.dumps(out, indent=1, default=list))


if __name__ == "__main__":
    main()
