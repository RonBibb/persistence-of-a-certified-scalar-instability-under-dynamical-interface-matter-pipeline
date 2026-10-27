"""Validated D2A cover at the source-bound original brane separation."""

from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path

from flint import arb, ctx, fmpq

import validated_flow_pilot as flow


D0 = flow.dyadic("0.9996389747145851")
THRESHOLD = fmpq(989750001, 10_000_000_000)  # exact 0.0989750001
A_MIN = fmpq(0)
A_MAX = flow.V0_Q
STEPS = 1024
TARGET_WIDTH = fmpq(1, 65536)
MAX_DEPTH = 24
PRECISION_BITS = 512


def no_turn_polynomial(a: arb) -> arb:
    tau = arb(flow.LAMBDA_A_Q) + arb(flow.GAMMA_Q) * (a - arb(flow.V0_Q)) ** 2 / 2
    return arb(flow.GAMMA_Q) * (arb(flow.V0_Q) - a) * tau - 3 * arb(flow.M2_Q) * arb(flow.V0_Q)


def integrate_box(lo: fmpq, hi: fmpq) -> dict[str, object]:
    hstep = D0 / STEPS
    y = flow.launch(flow.ball(lo, hi))
    phi_path_lo, phi_path_hi = flow.bounds(y[2])
    max_picard = 0
    for _ in range(STEPS):
        z, iterations = flow.picard_box(y, hstep)
        max_picard = max(max_picard, iterations)
        pl, ph = flow.bounds(z[2])
        phi_path_lo = min(phi_path_lo, pl)
        phi_path_hi = max(phi_path_hi, ph)
        f0 = flow.rhs(y)
        f2 = flow.second_derivative(z, flow.rhs(z))
        y = [v + arb(hstep) * f + arb(hstep * hstep / 2) * a2 for v, f, a2 in zip(y, f0, f2, strict=True)]
    G, scalar = flow.residuals(y)
    gl, gh = flow.bounds(G)
    sl, sh = flow.bounds(scalar)
    phil, phih = flow.bounds(y[2])
    return {
        "G_bounds": [float(gl), float(gh)],
        "scalar_residual_bounds": [float(sl), float(sh)],
        "phi_endpoint_bounds": [float(phil), float(phih)],
        "phi_path_bounds": [float(phi_path_lo), float(phi_path_hi)],
        "G_excludes_zero": gl > 0 or gh < 0,
        "path_scalar_admissible": phi_path_lo > 0 and phi_path_hi <= flow.V0_Q,
        "phi_endpoint_below_v1": phih < flow.V1_Q,
        "max_picard_iterations": max_picard,
    }


def classify_box(lo: fmpq, hi: fmpq, depth: int) -> tuple[str, dict[str, object] | None]:
    initial = flow.launch(flow.ball(lo, hi))
    kl, kh = flow.bounds(initial[5])
    if kh < 0:
        return "NEGATIVE_CURVATURE_EXCLUDED", None
    if hi - lo > TARGET_WIDTH:
        return "SPLIT", None
    record = integrate_box(lo, hi)
    if hi <= THRESHOLD:
        P = no_turn_polynomial(flow.ball(lo, hi))
        pl, _ph = flow.bounds(P)
        record["no_turn_polynomial_lower"] = float(pl)
        if record["path_scalar_admissible"] and record["phi_endpoint_below_v1"] and pl >= 0:
            return "NO_TURN_EXCLUDED", record
    elif lo >= THRESHOLD:
        if record["G_excludes_zero"]:
            return "UPPER_ISRAEL_EXCLUDED", record
    if depth >= MAX_DEPTH:
        return "UNRESOLVED", record
    return "SPLIT", record


def main() -> None:
    ctx.prec = PRECISION_BITS
    started = time.monotonic()
    stack = [(A_MIN, THRESHOLD, 0), (THRESHOLD, A_MAX, 0)]
    terminal = []
    unresolved = []
    integrated = 0
    while stack:
        lo, hi, depth = stack.pop()
        classification, record = classify_box(lo, hi, depth)
        if record is not None:
            integrated += 1
        if classification == "SPLIT":
            mid = (lo + hi) / 2
            stack.append((mid, hi, depth + 1))
            stack.append((lo, mid, depth + 1))
            continue
        row = {
            "a_bounds": [str(lo), str(hi)],
            "a_decimal_bounds": [float(lo), float(hi)],
            "depth": depth,
            "classification": classification,
            "record": record,
        }
        terminal.append(row)
        if classification == "UNRESOLVED":
            unresolved.append(row)
    counts = {name: sum(row["classification"] == name for row in terminal) for name in [
        "NEGATIVE_CURVATURE_EXCLUDED", "NO_TURN_EXCLUDED", "UPPER_ISRAEL_EXCLUDED", "UNRESOLVED"
    ]}
    passed = not unresolved and sum(counts.values()) == len(terminal)
    payload = {
        "schema": "d2a-validated-fixed-separation-cover-v1",
        "status": "COMPLETE" if passed else "INCOMPLETE",
        "classification": "FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE" if passed else "FIXED_SEPARATION_COVER_UNRESOLVED",
        "authority": "VALIDATED_COVER_OF_0_LE_A_LE_V0_FOR_THE_DECLARED_REDUCED_STATIC_IVP",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": PRECISION_BITS,
            "wall_seconds": time.monotonic() - started,
        },
        "frozen_design": {
            "D0_exact_dyadic": str(D0),
            "a_range": [str(A_MIN), str(A_MAX)],
            "no_turn_threshold_lower_exact": str(THRESHOLD),
            "steps": STEPS,
            "target_a_width": str(TARGET_WIDTH),
            "max_depth": MAX_DEPTH,
        },
        "terminal_box_count": len(terminal),
        "integrated_box_count_including_pre_split_attempts": integrated,
        "classification_counts": counts,
        "unresolved": unresolved,
        "terminal_boxes": terminal,
        "claim_boundary": [
            "The exclusion is for the declared reduced static IVP, positive curvature, and 0<=a<=v0.",
            "It does not exclude a dynamical radion bridge, altered wall/action parameters, or a branch outside the declared admissible launch range.",
            "It is not an event-horizon or collapse-development result."
        ],
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        output = Path(sys.argv[2])
        temporary = output.with_name(output.name + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        os.replace(temporary, output)
    elif len(sys.argv) == 1:
        print(rendered, end="")
    else:
        raise SystemExit("usage: d2a_validated_cover.py [--output PATH]")


if __name__ == "__main__":
    main()
