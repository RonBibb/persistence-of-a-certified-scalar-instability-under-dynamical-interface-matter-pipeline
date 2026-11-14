"""Assemble FAMILY_BOXES_W.json from the binary64 2-D design (design step only).

Box: v1 in [11/125, 1/10] x lambda_b in [-60529/10000, -60429/10000], cells of
1/1000 x 1/1000 (i = 0..11 along v1, k = 0..9 along lambda_b, j = 12k + i).
The design column v1 in [0.086, 0.088] (design indices 0 and 1) is dropped;
that is the only selection made from the exploration.  The radius rule is the
V/L rule with the 2-D spread and predicted Newton half-width.

usage: make_family_boxes_w.py OUT_JSON BOXES2D_0 BOXES2D_1 BOXES2D_2 BOXES2D_3
"""
import json
import sys
from fractions import Fraction as Q

V1 = "6520040733916207/72057594037927936"
LB = "-851862101055633/140737488355328"
V0 = Q(3602879701896397, 36028797018963968)


def main():
    rows = []
    for path in sys.argv[2:6]:
        with open(path) as handle:
            rows += json.load(handle)["rows"]
    cells = []
    anchor = None
    for row in rows:
        if "error" in row:
            raise RuntimeError("design cell without float root")
        if row["i"] < 2:
            continue
        i, k = row["i"] - 2, row["k"]
        va, vb = Q(row["v1"][0]), Q(row["v1"][1])
        la, lb = Q(row["lambda_b"][0]), Q(row["lambda_b"][1])
        if va != Q(11, 125) + i * Q(1, 1000) or vb != va + Q(1, 1000):
            raise RuntimeError("v1 tiling")
        if la != Q(-60529, 10000) + k * Q(1, 1000) or lb != la + Q(1, 1000):
            raise RuntimeError("lambda_b tiling")
        if not (float(row["A_lo"]) < float(row["A0"]) < float(row["A_hi"]) < float(V0)):
            raise RuntimeError("bad A box")
        if va <= Q(V1) <= vb and la <= Q(LB) <= lb:
            anchor = [i, k]
        cells.append({"j": 12 * k + i, "i": i, "k": k, "param": "v1", "lo": row["v1"][0], "hi": row["v1"][1],
                      "extra_params": [["lambda_b", row["lambda_b"][0], row["lambda_b"][1]]],
                      "A0": row["A0"], "A_lo": row["A_lo"], "A_hi": row["A_hi"]})
    cells.sort(key=lambda c: c["j"])
    if [c["j"] for c in cells] != list(range(120)) or anchor is None:
        raise RuntimeError("cells incomplete or anchor outside")
    boxes = {"schema": "family-boxes-w-v1",
             "label": "FROZEN DESIGN. Cells chosen from binary64 RK4 exploration; certification only by the interval producers.",
             "families": {"W": {"params": ["v1", "lambda_b"],
                                "box": {"v1": ["11/125", "1/10"], "lambda_b": ["-60529/10000", "-60429/10000"]},
                                "shape": [12, 10], "width": ["1/1000", "1/1000"], "anchor_value": {"v1": V1, "lambda_b": LB},
                                "anchor_cell": anchor, "subboxes": cells}}}
    with open(sys.argv[1], "w") as handle:
        json.dump(boxes, handle, indent=1, sort_keys=True)
    print(json.dumps({"cells": len(cells), "anchor_cell": anchor}))


if __name__ == "__main__":
    main()
