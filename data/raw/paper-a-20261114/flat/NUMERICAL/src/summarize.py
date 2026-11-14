#!/usr/bin/env python3
"""Summarize flatcount v2 job JSONs against the frozen PLAN v2 gates and outcome classes.

Usage: python3 -I summarize.py OUT_JSON OUT_MD JOB_JSON [JOB_JSON ...]
All numbers are FLOAT EXPLORATORY.
"""
import json
import math
import sys
from fractions import Fraction as Fr

EXPECTED = {"F1": 1, "F1b": 1, "F3": 3, "F0": 0, "DS": 1}
D_LO = float(Fr(32727, 16384)) - 1e-4
D_HI = float(Fr(32729, 16384)) + 1e-4
TH_LO = float(Fr(577838035, 536870912)) - 1e-4
TH_HI = float(Fr(577858823, 536870912)) + 1e-4
IMPL = ("G3_pass", "G5_pass", "G6_pass", "G8_pass", "G9_pass", "G12_pass", "G13_pass", "G14_pass")


def case_summary(r):
    cid = r["case"]
    n = EXPECTED[cid]
    Nb = str(r["N_base"])
    N2 = str(2 * r["N_base"])
    blk = r["per_N"][Nb]
    bg = blk["background_gates"]
    rows = []
    impl_ok = bg["G1_pass"] and bg["G2_pass"]
    g4 = {(x["t_a"], x["t_b"]): x for x in r["G4"]}
    for rec in blk["records"]:
        key = (rec["t_a"], rec["t_b"])
        gates = {g: rec[g] for g in IMPL}
        gates["G4_pass"] = g4[key]["G4_pass"]
        gates["G7_pass"] = rec["G7_pass"]
        ok = all(gates.values())
        impl_ok = impl_ok and ok
        pred = {}
        if cid in ("F1", "F1b", "F3"):
            pred["P1"] = (rec["M1_count"] == rec["M2_count"] == rec["M1b_count"] == n)
            pred["P2"] = rec["char_mu0_physical"] < 0.0
            pred["P3"] = (0.0 < rec["theta_b_mu_min_mod_pi"] < math.pi / 2) and \
                (n < rec["theta_b_mu_top_over_pi"] < n + 0.5)
        if cid == "DS":
            b = rec["band"]
            pred["below_exactly_1"] = (rec["M1_count"] == rec["M2_count"] == rec["M1b_count"] == 1)
            pred["band_exactly_0"] = (b["M1_count"] == b["M1_count_nested"] == b["M1b_count"] == b["M2_count"] == 0)
            gates["band_G6"] = b["G6_band"]
            gates["band_G12"] = b["G12_threshold_signs"] and b["band_lo_gap_matches_pred"]
            ok = ok and gates["band_G6"] and gates["band_G12"]
            impl_ok = impl_ok and gates["band_G6"] and gates["band_G12"]
        rows.append({"t_a": rec["t_a"], "t_b": rec["t_b"], "M1": rec["M1_count"], "M1_nested": rec["M1_count_nested"],
                     "M1b": rec["M1b_count"], "M2": rec["M2_count"], "gates": gates, "all_gates": ok, "pred": pred,
                     "eigenvalues": rec["eigenvalues"], "theta_top_over_pi": rec["theta_b_mu_top_over_pi"],
                     "theta_pred_over_pi": rec["theta_pred_over_pi"], "near_threshold": rec["near_threshold_eigenvalue_flag"],
                     "G4_max_rel_ev_diff": g4[key]["max_rel_ev_diff"],
                     "constraint_rel_max": rec["constraint_rel_max"], "nu_h_mu_min": rec["nu_h_mu_min"],
                     "min_theta_increment": rec["min_theta_increment"], "mu_min": rec["mu_min"]})
    extra = {}
    if cid in ("F1", "F1b", "F3"):
        diag = sorted([x for x in rows if x["t_a"] == x["t_b"]], key=lambda x: -x["t_a"])
        p4 = None
        if diag and all(len(x["eigenvalues"]) == n for x in diag):
            p4 = True
            for j in range(n):
                seq = [x["eigenvalues"][j] for x in diag]
                for u, v in zip(seq, seq[1:]):
                    if v - u < -1e-6 * max(1.0, abs(u)):
                        p4 = False
                if not seq[-1] < 0.0:
                    p4 = False
        extra["P4"] = p4
        extra["P4_diagonal_eigenvalues"] = {str(x["t_a"]): x["eigenvalues"] for x in diag}
    if cid == "DS":
        meta = blk["meta"]
        th0 = [rec["band"]["theta_b_mu0_over_pi"] for rec in blk["records"] if (rec["t_a"], rec["t_b"]) == (1.0, 1.0)]
        extra["G10_D"] = D_LO <= meta["D"] <= D_HI
        extra["G10_theta"] = bool(th0) and TH_LO <= th0[0] <= TH_HI
        extra["theta_b_mu0_over_pi_t11"] = th0[0] if th0 else None
        extra["D_float"] = meta["D"]
        extra["k_float"] = meta["k"]
        extra["band_detail"] = [{"t_a": rec["t_a"], "t_b": rec["t_b"], **{kk: rec["band"][kk] for kk in
                                 ("M1_count", "M1_count_nested", "M1b_count", "M2_count", "theta_b_band_lo_over_pi",
                                  "theta_b_mu0_over_pi", "char_mu0", "roots")}} for rec in blk["records"]]
    if cid == "F0":
        recs = blk["records"]
        cnt = [(x["M1_count"], x["M2_count"], x["M1b_count"]) for x in recs]
        extra["P5_DD_exactly_0"] = cnt[0] == (0, 0, 0)
        extra["P5_softlower_dirichletupper_exactly_1"] = cnt[1] == (1, 1, 1)
        extra["P5_Bpositive_exactly_0"] = cnt[2] == (0, 0, 0)
        extra["G11"] = [x["G11_pass"] for x in blk["LS"]]
        extra["LS_detail"] = blk["LS"]
        extra["kappas_case3"] = blk["meta"].get("F0_case3_kappas")
    return {"case": cid, "N_base": r["N_base"], "N_second": int(N2), "background_gates": bg,
            "implementation_ok": impl_ok, "rows": rows, "extra": extra, "elapsed_s": r["elapsed_s"],
            "meta": blk["meta"], "lam_abs_min": blk["lam_abs_min"], "vartheta_D": blk["vartheta_D"]}


def classify(cs):
    def flat_ok(c):
        return c is not None and c["implementation_ok"] and all(
            x["pred"]["P1"] and x["pred"]["P2"] and x["pred"]["P3"] for x in c["rows"]) and c["extra"]["P4"] is True
    ds, f0 = cs.get("DS"), cs.get("F0")
    controls = (ds is not None and ds["implementation_ok"] and ds["extra"]["G10_D"] and ds["extra"]["G10_theta"]
                and all(x["pred"]["below_exactly_1"] and x["pred"]["band_exactly_0"] for x in ds["rows"])
                and f0 is not None and f0["implementation_ok"] and f0["extra"]["P5_DD_exactly_0"]
                and f0["extra"]["P5_softlower_dirichletupper_exactly_1"] and f0["extra"]["P5_Bpositive_exactly_0"]
                and all(f0["extra"]["G11"]))
    contradicted = False
    for cid in ("F1", "F1b", "F3"):
        c = cs.get(cid)
        if c and c["implementation_ok"]:
            for x in c["rows"]:
                if x["M1"] == x["M2"] == x["M1b"] != EXPECTED[cid]:
                    contradicted = True
    if contradicted:
        return "CONTRADICTED", controls
    if not controls:
        return "IMPLEMENTATION-FAIL", controls
    if all(flat_ok(cs.get(c)) for c in ("F1", "F1b", "F3")):
        return "SUPPORTED", controls
    if flat_ok(cs.get("F1")) and flat_ok(cs.get("F1b")):
        return "SUPPORTED-n=1-ONLY", controls
    return "AMBIGUOUS", controls


def main():
    out_json, out_md, paths = sys.argv[1], sys.argv[2], sys.argv[3:]
    cs = {}
    for p in paths:
        with open(p) as fh:
            r = json.load(fh)
        cs[r["case"]] = case_summary(r)
    outcome, controls = classify(cs)
    summary = {"label": "FLOAT EXPLORATORY", "outcome_class": outcome, "controls_pass": controls, "cases": cs}
    with open(out_json, "w") as fh:
        json.dump(summary, fh, indent=1)
    md = ["# Gate summary (float exploratory)", "", f"Outcome class: **{outcome}** (controls pass: {controls})", ""]
    for cid in ("DS", "F0", "F1", "F1b", "F3"):
        c = cs.get(cid)
        if not c:
            md.append(f"## {cid}: no result (INCOMPLETE)")
            continue
        bg = c["background_gates"]
        md.append(f"## {cid}: expected n = {EXPECTED[cid]}; N = {c['N_base']}/{c['N_second']}; "
                  f"implementation gates all pass: {c['implementation_ok']}")
        md.append("")
        md.append(f"Background: G1 {bg['G1_pass']} ({bg['G1_max_constraint']:.1e}), G2 {bg['G2_pass']}, "
                  f"n detected {bg['n_detected']}, T_a {bg['T_a']:.4g}, T_b {bg['T_b']:.4g}, T'_a {bg['Tp_a']:.4g}, "
                  f"T'_b {bg['Tp_b']:.4g}, s_sing {bg['s_sing']}, a in [{bg['a_min']:.3g}, {bg['a_max']:.3g}], "
                  f"μ_min {c['rows'][0]['mu_min']:.5g}")
        md.append("")
        md.append("| t_a | t_b | M1 | M1 nested | M1′ | M2 | all gates | predictions | eigenvalues μ (float) | θ_b(μ_top)/π | pred/π |")
        md.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for x in c["rows"]:
            ev = ", ".join(f"{v:.8g}" for v in x["eigenvalues"])
            pr = ", ".join(f"{k}:{'✓' if v else '✗'}" for k, v in x["pred"].items())
            md.append(f"| {x['t_a']:.4g} | {x['t_b']:.4g} | {x['M1']} | {x['M1_nested']} | {x['M1b']} | {x['M2']} | "
                      f"{x['all_gates']} | {pr} | {ev} | {x['theta_top_over_pi']:.6f} | {x['theta_pred_over_pi']:.6f} |")
        md.append("")
        failed = sorted({g for x in c["rows"] for g, v in x["gates"].items() if not v})
        md.append(f"Failed gates (any pair): {failed if failed else 'none'}")
        ex = {k: v for k, v in c["extra"].items() if k not in ("LS_detail", "band_detail", "P4_diagonal_eigenvalues")}
        md.append(f"Extra: `{json.dumps(ex)}`")
        md.append("")
    with open(out_md, "w") as fh:
        fh.write("\n".join(md) + "\n")
    print(outcome)


if __name__ == "__main__":
    main()
