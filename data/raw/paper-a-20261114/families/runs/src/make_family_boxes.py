"""Assemble FAMILY_BOXES.json from the float design tables (design step only).

usage: make_family_boxes.py BOXES_V_JSON BOXES_L_JSON OUT_JSON
"""
import json
import sys
from fractions import Fraction as Q

FIXED = {
    "m2": "7385903388887613/18014398509481984",
    "gamma": "20",
    "v0": "3602879701896397/36028797018963968",
    "v1": "6520040733916207/72057594037927936",
    "lambda_a": "6755388606266369/1125899906842624",
    "lambda_b": "-851862101055633/140737488355328",
}
SPEC = {
    "V": {"param": "v1", "segment": ["43/500", "3/20"], "width": "1/1000", "priority": 20},
    "L": {"param": "lambda_b", "segment": ["-60529/10000", "-60229/10000"], "width": "1/1000", "priority": 10},
}


def family(path, key):
    with open(path) as handle:
        table = json.load(handle)
    spec = dict(SPEC[key])
    anchor = Q(FIXED[spec["param"]])
    rows = []
    anchor_index = None
    for row in table["rows"]:
        if "error" in row:
            raise RuntimeError(f"design row without float root: {key} {row['j']}")
        lo, hi = Q(row["lo"]), Q(row["hi"])
        a_lo, a0, a_hi = float(row["A_lo"]), float(row["A0"]), float(row["A_hi"])
        if not (a_lo < a0 < a_hi < float(Q(FIXED["v0"]))):
            raise RuntimeError("bad A box")
        if lo <= anchor <= hi:
            anchor_index = row["j"]
        rows.append({"j": row["j"], "param": spec["param"], "lo": row["lo"], "hi": row["hi"],
                     "A0": row["A0"], "A_lo": row["A_lo"], "A_hi": row["A_hi"]})
    rows.sort(key=lambda r: r["j"])
    if [r["j"] for r in rows] != list(range(len(rows))):
        raise RuntimeError("sub-box indices not contiguous")
    for left, right in zip(rows, rows[1:]):
        if left["hi"] != right["lo"]:
            raise RuntimeError("sub-boxes do not tile the segment")
    if rows[0]["lo"] != spec["segment"][0] or rows[-1]["hi"] != spec["segment"][1]:
        raise RuntimeError("segment endpoints differ")
    if anchor_index is None:
        raise RuntimeError("anchor outside segment")
    spec.update(anchor_value=FIXED[spec["param"]], anchor_subbox=anchor_index, subboxes=rows)
    return spec


def main():
    boxes = {
        "schema": "family-boxes-v1",
        "label": "FROZEN DESIGN. Boxes were chosen from binary64 RK4 exploration; certification is only by the interval producers.",
        "fixed_parameters_exact": FIXED,
        "radius_rule": "r_j = 2.5*max(float root spread over the sub-box, predicted parametric-Newton half-width) + 5e-9; A-box [A0-r, A0+r] rounded outward to binary64",
        "families": {"V": family(sys.argv[1], "V"), "L": family(sys.argv[2], "L")},
    }
    with open(sys.argv[3], "w") as handle:
        json.dump(boxes, handle, indent=1, sort_keys=True)
    print(json.dumps({k: {"n": len(v["subboxes"]), "anchor_subbox": v["anchor_subbox"]} for k, v in boxes["families"].items()}))


if __name__ == "__main__":
    main()
