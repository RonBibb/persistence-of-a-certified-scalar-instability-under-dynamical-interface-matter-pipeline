"""Validated D1 event sensitivity and one-dimensional interval Newton.

The producer uses Arb outward ball arithmetic, a Picard enclosure on each
fixed proper-distance cell, and a second-order Taylor endpoint enclosure for
the 6-state proper-distance ODE plus its 6-component a-variational equation.
"""

from __future__ import annotations

import json
import platform
import sys
import time

from flint import arb, ctx, fmpq


M2 = "0.41"
GAMMA = "20.0"
V0 = "0.1"
V1 = "0.09048374180359596"
LAMBDA_A = "5.999990376773895"
LAMBDA_B = "-6.052844277744164"
FULL_A_LO = "0.09901076956670637"
FULL_A_HI = "0.09901087894170638"
ROOT_CENTER = "0.09901086589880687"
ROOT_BOXES = {
    "wide": ("0.09901086289880687", "0.09901086889880687"),
    "narrow": ("0.09901086489880687", "0.09901086689880687"),
}
STEP_COUNTS = (4096, 8192, 16384)
S_END = fmpq(2)
PRECISION_BITS = 512


def dyadic(text: str) -> fmpq:
    n, d = float(text).as_integer_ratio()
    return fmpq(n, d)


def ball(lo: fmpq, hi: fmpq) -> arb:
    if lo > hi:
        raise ValueError("empty interval")
    return arb((lo + hi) / 2, (hi - lo) / 2)


def bounds(x: arb) -> tuple[fmpq, fmpq]:
    return x.lower().fmpq(), x.upper().fmpq()


def hull(x: arb, y: arb) -> arb:
    xl, xh = bounds(x)
    yl, yh = bounds(y)
    return ball(min(xl, yl), max(xh, yh))


def union_all(values: list[arb]) -> arb:
    if not values:
        raise ValueError("empty union")
    out = values[0]
    for value in values[1:]:
        out = hull(out, value)
    return out


def inflate(x: arb) -> arb:
    lo, hi = bounds(x)
    pad = (hi - lo) / 10 + fmpq(1, 2**420)
    return ball(lo - pad, hi + pad)


def strictly_contains(outer: arb, inner: arb) -> bool:
    ol, oh = bounds(outer)
    il, ih = bounds(inner)
    return ol < il and ih < oh


def width(x: arb) -> float:
    lo, hi = bounds(x)
    return float(hi - lo)


def decimal_bounds(x: arb) -> list[float]:
    lo, hi = bounds(x)
    return [float(lo), float(hi)]


M2_Q = dyadic(M2)
GAMMA_Q = dyadic(GAMMA)
V0_Q = dyadic(V0)
V1_Q = dyadic(V1)
LAMBDA_A_Q = dyadic(LAMBDA_A)
LAMBDA_B_Q = dyadic(LAMBDA_B)
FULL_A_LO_Q = dyadic(FULL_A_LO)
FULL_A_HI_Q = dyadic(FULL_A_HI)
ROOT_CENTER_Q = dyadic(ROOT_CENTER)


class TimeDual:
    """Value plus directional derivative along the augmented ODE flow."""

    __slots__ = ("v", "d")

    def __init__(self, value: arb, derivative: arb):
        self.v = value
        self.d = derivative

    @staticmethod
    def coerce(value: object) -> "TimeDual":
        if isinstance(value, TimeDual):
            return value
        return TimeDual(arb(value), arb(0))

    def __add__(self, other: object) -> "TimeDual":
        other = self.coerce(other)
        return TimeDual(self.v + other.v, self.d + other.d)

    __radd__ = __add__

    def __neg__(self) -> "TimeDual":
        return TimeDual(-self.v, -self.d)

    def __sub__(self, other: object) -> "TimeDual":
        return self + (-self.coerce(other))

    def __rsub__(self, other: object) -> "TimeDual":
        return self.coerce(other) - self

    def __mul__(self, other: object) -> "TimeDual":
        other = self.coerce(other)
        return TimeDual(self.v * other.v, self.d * other.v + self.v * other.d)

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> "TimeDual":
        other = self.coerce(other)
        return TimeDual(self.v / other.v, (self.d * other.v - self.v * other.d) / other.v**2)

    def __rtruediv__(self, other: object) -> "TimeDual":
        return self.coerce(other) / self

    def __pow__(self, power: int) -> "TimeDual":
        if power != 2:
            raise ValueError("only square is needed")
        return self * self

    def exp(self) -> "TimeDual":
        ev = self.v.exp()
        return TimeDual(ev, ev * self.d)


def augmented_rhs(w: list[arb] | list[TimeDual]) -> list[arb] | list[TimeDual]:
    A, H, phi, S, _Z, curvature, pA, pH, pphi, pS, _pZ, pcurvature = w
    em2a = (-2 * A).exp()
    ema = (-A).exp()
    zero = A * 0
    return [
        H,
        -S**2 / 3 - curvature * em2a,
        S,
        phi * arb(M2_Q) - 4 * H * S,
        ema,
        zero,
        pH,
        2 * curvature * em2a * pA - 2 * S * pS / 3 - em2a * pcurvature,
        pS,
        pphi * arb(M2_Q) - 4 * (pH * S + H * pS),
        -ema * pA,
        zero,
    ]


def augmented_second_derivative(w: list[arb]) -> list[arb]:
    fw = augmented_rhs(w)
    dual_inputs = [TimeDual(value, derivative) for value, derivative in zip(w, fw, strict=True)]
    return [item.d for item in augmented_rhs(dual_inputs)]


def launch(a: arb) -> list[arb]:
    H = -(arb(LAMBDA_A_Q) + arb(GAMMA_Q) * (a - arb(V0_Q)) ** 2 / 2) / 6
    S = arb(GAMMA_Q) * (a - arb(V0_Q)) / 2
    curvature = H**2 - 1 - S**2 / 12 + arb(M2_Q) * a**2 / 12
    pA = arb(0)
    pH = -arb(GAMMA_Q) * (a - arb(V0_Q)) / 6
    pphi = arb(1)
    pS = arb(GAMMA_Q) / 2
    pZ = arb(0)
    pcurvature = 2 * H * pH - S * pS / 6 + arb(M2_Q) * a / 6
    return [arb(0), H, a, S, arb(0), curvature, pA, pH, pphi, pS, pZ, pcurvature]


def picard_box(w0: list[arb], h: fmpq) -> tuple[list[arb], int]:
    time_interval = ball(fmpq(0), h)
    f0 = augmented_rhs(w0)
    z = [inflate(hull(w, w + time_interval * f)) for w, f in zip(w0, f0, strict=True)]
    for iteration in range(1, 25):
        fz = augmented_rhs(z)
        candidate = [hull(w, w + time_interval * f) for w, f in zip(w0, fz, strict=True)]
        if all(strictly_contains(zo, ci) for zo, ci in zip(z, candidate, strict=True)):
            return z, iteration
        z = [inflate(hull(zo, ci)) for zo, ci in zip(z, candidate, strict=True)]
    raise RuntimeError("Picard enclosure did not self-contain in 24 iterations")


def advance(w0: list[arb], z: list[arb], h: fmpq) -> list[arb]:
    f0 = augmented_rhs(w0)
    f2 = augmented_second_derivative(z)
    return [w + arb(h) * f + arb(h * h / 2) * a2 for w, f, a2 in zip(w0, f0, f2, strict=True)]


def event_quantities(z: list[arb]) -> dict[str, arb]:
    A, H, phi, S, _Z, _k, _pA, pH, pphi, pS, _pZ, _pk = z
    fw = augmented_rhs(z)
    tau_b = arb(LAMBDA_B_Q) + arb(GAMMA_Q) * (phi - arb(V1_Q)) ** 2 / 2
    G = H - tau_b / 6
    Gs = fw[1] - arb(GAMMA_Q) * (phi - arb(V1_Q)) * S / 6
    Ga = pH - arb(GAMMA_Q) * (phi - arb(V1_Q)) * pphi / 6
    Dprime = -Ga / Gs
    h = S + arb(GAMMA_Q) * (phi - arb(V1_Q)) / 2
    ha = pS + arb(GAMMA_Q) * pphi / 2
    hs = fw[3] + arb(GAMMA_Q) * S / 2
    hprime = ha + hs * Dprime
    return {"G": G, "Gs": Gs, "Ga": Ga, "Dprime": Dprime, "h": h, "ha": ha, "hs": hs, "hprime": hprime}


def event_enclosure(a_lo: fmpq, a_hi: fmpq, steps: int) -> dict[str, object]:
    hstep = S_END / steps
    w = launch(ball(a_lo, a_hi))
    zero_cells: list[int] = []
    event_records: list[dict[str, arb]] = []
    max_picard = 0
    signs: list[str] = []
    for index in range(steps):
        z, iterations = picard_box(w, hstep)
        max_picard = max(max_picard, iterations)
        q = event_quantities(z)
        gl, gh = bounds(q["G"])
        if gl > 0:
            signs.append("positive")
        elif gh < 0:
            signs.append("negative")
        else:
            signs.append("zero-containing")
            zero_cells.append(index)
            event_records.append(q)
        w = advance(w, z, hstep)
    if not zero_cells:
        raise RuntimeError("no zero-containing event cell")
    contiguous = zero_cells == list(range(zero_cells[0], zero_cells[-1] + 1))
    positive_before = all(sign == "positive" for sign in signs[: zero_cells[0]])
    negative_after = all(sign == "negative" for sign in signs[zero_cells[-1] + 1 :])
    quantities = {key: union_all([record[key] for record in event_records]) for key in event_records[0]}
    gsl, gsh = bounds(quantities["Gs"])
    hpl, hph = bounds(quantities["hprime"])
    return {
        "event_cell_indices": [zero_cells[0], zero_cells[-1]],
        "event_bracket": [str(zero_cells[0] * hstep), str((zero_cells[-1] + 1) * hstep)],
        "event_bracket_decimal": [float(zero_cells[0] * hstep), float((zero_cells[-1] + 1) * hstep)],
        "event_bracket_width": float((zero_cells[-1] - zero_cells[0] + 1) * hstep),
        "zero_cells_contiguous": contiguous,
        "positive_before": positive_before,
        "negative_after": negative_after,
        "Gs_bounds": decimal_bounds(quantities["Gs"]),
        "Gs_strictly_negative": gsh < 0,
        "Ga_bounds": decimal_bounds(quantities["Ga"]),
        "Dprime_bounds": decimal_bounds(quantities["Dprime"]),
        "h_bounds": decimal_bounds(quantities["h"]),
        "ha_bounds": decimal_bounds(quantities["ha"]),
        "hs_bounds": decimal_bounds(quantities["hs"]),
        "hprime_bounds": decimal_bounds(quantities["hprime"]),
        "hprime_excludes_zero": hpl > 0 or hph < 0,
        "event_validated": contiguous and positive_before and negative_after and gsh < 0,
        "max_picard_iterations": max_picard,
        "_h_ball": quantities["h"],
        "_hprime_ball": quantities["hprime"],
    }


def public_record(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def interval_newton(box_name: str, box_pair: tuple[str, str], steps: int) -> dict[str, object]:
    lo, hi = (dyadic(box_pair[0]), dyadic(box_pair[1]))
    if not (FULL_A_LO_Q <= lo < ROOT_CENTER_Q < hi <= FULL_A_HI_Q):
        raise ValueError("root box not contained in full frozen bracket")
    box_record = event_enclosure(lo, hi, steps)
    point_record = event_enclosure(ROOT_CENTER_Q, ROOT_CENTER_Q, steps)
    derivative = box_record["_hprime_ball"]
    dl, dh = bounds(derivative)
    if dl <= 0 <= dh:
        newton = None
        self_map = False
    else:
        newton_ball = arb(ROOT_CENTER_Q) - point_record["_h_ball"] / derivative
        nl, nh = bounds(newton_ball)
        newton = {
            "exact_bounds": [str(nl), str(nh)],
            "decimal_bounds": [float(nl), float(nh)],
            "width": float(nh - nl),
        }
        self_map = lo < nl and nh < hi
    qualified = bool(
        self_map
        and box_record["event_validated"]
        and point_record["event_validated"]
        and box_record["hprime_excludes_zero"]
    )
    return {
        "box_name": box_name,
        "box_decimal_labels": list(box_pair),
        "box_exact_dyadic_bounds": [str(lo), str(hi)],
        "steps": steps,
        "box_event": public_record(box_record),
        "center_event": public_record(point_record),
        "interval_newton_image": newton,
        "strict_self_map": self_map,
        "qualified_newton_inclusion": qualified,
    }


def dual_algebra_controls() -> dict[str, bool]:
    x = TimeDual(arb(2), arb(3))
    y = TimeDual(arb(5), arb(7))
    return {
        "product_rule": (x * y).v == 10 and (x * y).d == 29,
        "quotient_rule": (x / y).v == arb(2) / 5 and (x / y).d == arb(1) / 25,
        "square_rule": (x**2).v == 4 and (x**2).d == 12,
        "exp_rule_contains_reference": x.exp().d.contains(arb(3) * arb(2).exp()),
    }


def main() -> None:
    ctx.prec = PRECISION_BITS
    started = time.monotonic()
    controls = dual_algebra_controls()
    results = []
    status = "COMPLETE"
    error = None
    try:
        if not all(controls.values()):
            raise RuntimeError("dual algebra control failed")
        for steps in STEP_COUNTS:
            for name, pair in ROOT_BOXES.items():
                results.append(interval_newton(name, pair, steps))
    except Exception as exc:
        status = "INCOMPLETE"
        error = repr(exc)
    all_self_map = bool(results) and len(results) == len(STEP_COUNTS) * len(ROOT_BOXES) and all(row["qualified_newton_inclusion"] for row in results)
    finest = [row for row in results if row["steps"] == max(STEP_COUNTS) and row["box_name"] == "narrow"]
    classification = (
        "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS"
        if status == "COMPLETE" and all_self_map
        else "VALIDATED_SENSITIVITY_NEWTON_NOT_ESTABLISHED"
        if status == "COMPLETE"
        else "VALIDATED_SENSITIVITY_NEWTON_INCOMPLETE"
    )
    result = {
        "schema": "d1-validated-sensitivity-newton-result-v1",
        "status": status,
        "classification": classification,
        "authority": "RIGOROUS_ONE_DIMENSIONAL_SHOOTING_ROOT_CONDITIONAL_ON_THE_DECLARED_ODE_AND_WALL_MAP",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": PRECISION_BITS,
            "wall_seconds": time.monotonic() - started,
        },
        "frozen_design": {
            "full_shooting_bracket": [FULL_A_LO, FULL_A_HI],
            "root_center": ROOT_CENTER,
            "root_boxes": ROOT_BOXES,
            "step_counts": list(STEP_COUNTS),
            "proper_distance_endpoint": 2,
        },
        "dual_algebra_controls": controls,
        "all_predeclared_newton_images_strict_self_maps": all_self_map,
        "finest_narrow_result": finest[0] if finest else None,
        "all_results": results,
        "error": error,
        "claim_boundary": [
            "This proves only a root of the reduced proper-distance shooting problem if the classification passes.",
            "An independent checker and derived-quantity enclosure remain separate before final D1 closure.",
            "No collapse-line matching, stability, event horizon, or D2 bridge follows."
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
