"""Reporting only: RESULTS.md tables from the checker's verdict files.

Decides nothing.  Exact enclosures are printed either verbatim (A Newton
images, D brackets, theta_b/pi hulls) or as outward rational roundings at
denominator 2^40 (k and T_b lower bounds: floor; these remain valid lower
bounds).  Decimal renderings are labelled as roundings.

usage: results_tables.py SUBBOX_VERDICTS_JSON FAMILY_LETTER [extra-column]
"""
import json
import math
import sys
from fractions import Fraction as Q

DEN = 2 ** 40


def floor40(text):
    value = Q(text)
    return Q(math.floor(value * DEN), DEN)


def main():
    rows = json.load(open(sys.argv[1]))
    fam = sys.argv[2]
    out = ["| Sub-box | Parameter interval (exact) | Verdict | A: primary Newton image (exact) | D: primary event bracket (exact) | k lower bound (floor at 2^-40) | T_b lower bound (floor at 2^-40) | θ_b(0)/π, hull of both engines (exact) | Failed gates |",
           "|---|---|---|---|---|---|---|---|---|"]
    for row in rows:
        if not row["subbox"].startswith(fam + "_"):
            continue
        enc = row["enclosures"]
        interval = f"v1 ∈ [{row['interval'][0]}, {row['interval'][1]}]" if row["param"] == "v1" else \
            f"λ_b ∈ [{row['interval'][0]}, {row['interval'][1]}]"
        for extra in row.get("extra_params", []):
            interval += f" × λ_b ∈ [{extra[1]}, {extra[2]}]"
        a = enc.get("A_newton_image_primary")
        d = enc.get("D_event_bracket_primary")
        k = enc.get("k")
        tb = enc.get("T_b")
        th = enc.get("theta_b_over_pi_hull")
        failed = ", ".join(f"{g['gate']} ({g['kind']})" for g in row["failed_gates"]) or "none"
        kq = floor40(k[0]) if k else None
        tq = floor40(tb[0]) if tb else None
        out.append(
            f"| {row['subbox']} | {interval} | {row['verdict']} | "
            f"{'—' if not a else '[' + a[0] + ', ' + a[1] + ']'} | "
            f"{'—' if not d else '[' + d[0] + ', ' + d[1] + ']'} | "
            f"{'—' if kq is None else f'{kq} (≈{float(kq):.6g})'} | "
            f"{'—' if tq is None else f'{tq} (≈{float(tq):.4g})'} | "
            f"{'—' if not th else '[' + th[0] + ', ' + th[1] + ']'} | {failed} |")
    print("\n".join(out))


if __name__ == "__main__":
    main()
