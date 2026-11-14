"""Reporting only: turn the checker's verdict files into tables for RESULTS.md.

Decides nothing; every verdict comes from check_family.py.  Exact rational
bounds are printed in full; decimal renderings are labelled as roundings.

usage: report_tables.py CHECK_DIR OUT_MD_FRAGMENT OUT_VERDICTS_JSON
"""
import json
import sys
from fractions import Fraction as Q


def dec(text, digits=10):
    return f"{float(Q(text)):.{digits}g}"


def main():
    check, out_md, out_json = sys.argv[1:4]
    with open(f"{check}/FAMILY_VERDICT.json") as handle:
        family = json.load(handle)
    with open(f"{check}/SUBBOX_VERDICTS.json") as handle:
        rows = json.load(handle)
    lines = []
    for fam in ("V", "L"):
        spec = family["families"][fam]
        lines.append(f"### Family {fam} ({spec['param']})\n")
        lines.append(f"- Classification: **{spec['classification']}**; certified {spec['certified_subboxes']} of "
                     f"{spec['subboxes']} sub-boxes; verdict counts {spec['verdict_counts']}.")
        lines.append(f"- Certified segment containing the anchor (exact): {spec['certified_segment_containing_anchor']}.")
        hull = spec["theta_b_over_pi_hull_over_certified_segment"]
        if hull:
            lines.append(f"- Hull of theta_b(0)/pi over that segment (exact): [{hull[0]}, {hull[1]}] "
                         f"(decimal rounding [{dec(hull[0])}, {dec(hull[1])}]).")
        lines.append("")
        lines.append("| Sub-box | Interval (exact) | Verdict | A Newton image, primary (decimal rounding) | "
                     "D bracket, primary (exact) | k lower (rounding) | T_b lower (rounding) | "
                     "theta_b/pi hull (exact) | Failed gates |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for row in rows:
            if not row["subbox"].startswith(fam + "_"):
                continue
            enc = row["enclosures"]
            a = enc.get("A_newton_image_primary")
            d = enc.get("D_event_bracket_primary")
            k = enc.get("k")
            tb = enc.get("T_b")
            th = enc.get("theta_b_over_pi_hull")
            failed = ", ".join(g["gate"] for g in row["failed_gates"]) or "none"
            lines.append(
                f"| {row['subbox']} | [{row['interval'][0]}, {row['interval'][1]}] | {row['verdict']} | "
                f"{'—' if not a else '[' + dec(a[0], 16) + ', ' + dec(a[1], 16) + ']'} | "
                f"{'—' if not d else '[' + d[0] + ', ' + d[1] + ']'} | "
                f"{'—' if not k else dec(k[0], 8)} | {'—' if not tb else dec(tb[0], 6)} | "
                f"{'—' if not th else '[' + th[0] + ', ' + th[1] + ']'} | {failed} |")
        lines.append("")
    with open(out_md, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    verdicts = {"families": family["families"],
                "subboxes": [{"subbox": r["subbox"], "param": r["param"], "interval": r["interval"],
                              "verdict": r["verdict"], "failed_gates": [g["gate"] for g in r["failed_gates"]],
                              "gate_count": r["gate_count"], "enclosures": r["enclosures"],
                              "phase_trace_summary": r["phase_trace_summary"]} for r in rows]}
    with open(out_json, "w") as handle:
        json.dump(verdicts, handle, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
