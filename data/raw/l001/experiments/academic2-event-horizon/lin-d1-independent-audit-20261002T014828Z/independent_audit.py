"""Independent symbolic formula and exact inclusion audit for D1 R1."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

import sympy as sp


def symbolic_checks() -> dict[str, bool]:
    A, H, phi, S, Z, k = sp.symbols("A H phi S Z k")
    pA, pH, pphi, pS, pZ, pk = sp.symbols("pA pH pphi pS pZ pk")
    m2, gamma, v0, v1, la, lb, a = sp.symbols("m2 gamma v0 v1 la lb a")
    y = sp.Matrix([A, H, phi, S, Z, k])
    p = sp.Matrix([pA, pH, pphi, pS, pZ, pk])
    F = sp.Matrix([
        H,
        -S**2 / 3 - k * sp.exp(-2 * A),
        S,
        m2 * phi - 4 * H * S,
        sp.exp(-A),
        0,
    ])
    declared_variation = sp.Matrix([
        pH,
        2 * k * sp.exp(-2 * A) * pA - 2 * S * pS / 3 - sp.exp(-2 * A) * pk,
        pS,
        m2 * pphi - 4 * (pH * S + H * pS),
        -sp.exp(-A) * pA,
        0,
    ])
    H0 = -(la + gamma * (a - v0) ** 2 / 2) / 6
    S0 = gamma * (a - v0) / 2
    k0 = H0**2 - 1 - S0**2 / 12 + m2 * a**2 / 12
    declared_initial = sp.Matrix([
        0,
        -gamma * (a - v0) / 6,
        1,
        gamma / 2,
        0,
        2 * H0 * (-gamma * (a - v0) / 6) - S0 * (gamma / 2) / 6 + m2 * a / 6,
    ])
    G = H - (lb + gamma * (phi - v1) ** 2 / 2) / 6
    h = S + gamma * (phi - v1) / 2
    Gs = sp.diff(G, A) * F[0] + sp.diff(G, H) * F[1] + sp.diff(G, phi) * F[2] + sp.diff(G, S) * F[3]
    Ga = sp.diff(G, A) * pA + sp.diff(G, H) * pH + sp.diff(G, phi) * pphi + sp.diff(G, S) * pS
    hs = sp.diff(h, A) * F[0] + sp.diff(h, H) * F[1] + sp.diff(h, phi) * F[2] + sp.diff(h, S) * F[3]
    ha = sp.diff(h, A) * pA + sp.diff(h, H) * pH + sp.diff(h, phi) * pphi + sp.diff(h, S) * pS
    declared_Gs = F[1] - gamma * (phi - v1) * S / 6
    declared_Ga = pH - gamma * (phi - v1) * pphi / 6
    declared_hs = F[3] + gamma * S / 2
    declared_ha = pS + gamma * pphi / 2
    return {
        "variational_rhs_exact": all(sp.simplify(x) == 0 for x in (F.jacobian(y) * p - declared_variation)),
        "initial_sensitivity_exact": all(sp.simplify(x) == 0 for x in (sp.Matrix([0, H0, a, S0, 0, k0]).diff(a) - declared_initial)),
        "G_s_formula_exact": sp.simplify(Gs - declared_Gs) == 0,
        "G_a_formula_exact": sp.simplify(Ga - declared_Ga) == 0,
        "h_s_formula_exact": sp.simplify(hs - declared_hs) == 0,
        "h_a_formula_exact": sp.simplify(ha - declared_ha) == 0,
        "implicit_total_derivative_exact": sp.simplify((ha + hs * (-Ga / Gs)) - (declared_ha + declared_hs * (-declared_Ga / declared_Gs))) == 0,
    }


def q(text: str) -> Fraction:
    return Fraction(text)


def inclusion_checks(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text())
    boxes = {name: tuple(map(q, pair)) for name, pair in data["boxes"].items()}
    center = q(data["center"])
    rows = []
    for item in data["images"]:
        lo, hi = boxes[item["box"]]
        nlo, nhi = map(q, item["bounds"])
        rows.append({
            "steps": item["steps"],
            "box": item["box"],
            "box_ordered": lo < center < hi,
            "image_ordered": nlo <= nhi,
            "strict_self_map": lo < nlo and nhi < hi,
            "exact_width": str(nhi - nlo),
        })
    lookup = {(row["steps"], row["box"]): tuple(map(q, item["bounds"])) for row, item in zip(rows, data["images"], strict=True)}
    nested = {
        "narrow_16384_inside_8192": lookup[(8192, "narrow")][0] < lookup[(16384, "narrow")][0] and lookup[(16384, "narrow")][1] < lookup[(8192, "narrow")][1],
        "wide_16384_inside_8192": lookup[(8192, "wide")][0] < lookup[(16384, "wide")][0] and lookup[(16384, "wide")][1] < lookup[(8192, "wide")][1],
    }
    return {
        "rows": rows,
        "strict_self_map_count": sum(row["strict_self_map"] for row in rows),
        "expected_single_miss_is_4096_narrow": [
            (row["steps"], row["box"]) for row in rows if not row["strict_self_map"]
        ] == [(4096, "narrow")],
        "finer_images_nested": nested,
    }


def main() -> None:
    root = Path(__file__).resolve().parent
    symbolic = symbolic_checks()
    inclusions = inclusion_checks(root / "INCLUSION_CERTIFICATES.json")
    passed = all(symbolic.values()) and inclusions["strict_self_map_count"] == 5 and inclusions["expected_single_miss_is_4096_narrow"] and all(inclusions["finer_images_nested"].values())
    print(json.dumps({
        "schema": "d1-independent-formula-inclusion-audit-v1",
        "status": "PASS" if passed else "FAIL",
        "symbolic": symbolic,
        "inclusions": inclusions,
        "scope": "Independent symbolic formula and exact rational certificate audit; not an independent ODE enclosure replay."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
