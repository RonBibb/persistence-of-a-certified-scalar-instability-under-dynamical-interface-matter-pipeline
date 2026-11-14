"""Family wrapper for the archived independent background replay.

The archived engine independent_d1_replay.py is imported unchanged and run at
its R1 coarse level only (8192 cells, 768-bit Arb, fifth-order Taylor).  As in
the primary wrapper, v1 or lambda_b becomes an outward Arb ball over the
frozen sub-box and the root box and centre become the frozen family values;
the box is the same exact dyadic box the primary wrapper uses.

Consumption evidence: upper_quantities, the engine's only reader of v1 and
lambda_b, is wrapped so that every call's exact radii of h and G are
recorded (see fam_bg_primary.py for the bounds this must satisfy).  The
engine's JSON is embedded verbatim in the printed record.
"""
import contextlib
import io
import json

from flint import arb, ctx, fmpq

import independent_d1_replay as replay

PARAMETERS = {"v1": ("V1", "V1_Q"), "lambda_b": ("LAMBDA_B", "LAMBDA_B_Q")}
STEP_COUNTS = (8192,)
CONSUMPTION = {"calls": 0, "min_radius_h": None, "min_radius_G": None}
_archived_upper_quantities = replay.upper_quantities


def recorded_upper_quantities(state):
    quantities = _archived_upper_quantities(state)
    CONSUMPTION["calls"] += 1
    for key, slot in (("h", "min_radius_h"), ("G", "min_radius_G")):
        radius = quantities[key].rad()
        if CONSUMPTION[slot] is None or radius < CONSUMPTION[slot]:
            CONSUMPTION[slot] = radius
    return quantities


def outward_ball(lo, hi):
    value = replay.ball(lo, hi)
    for candidate in (value, arb(value)):
        clo, chi = replay.bounds(candidate)
        if not (clo <= lo and hi <= chi):
            raise RuntimeError("PARAMETER_BALL_NOT_OUTWARD")
    return value


def exact(value):
    return None if value is None else str(replay.bounds(value)[0])


def main():
    with open("job.json") as handle:
        job = json.load(handle)
    if replay.PRECISION_BITS != 768 or replay.TAYLOR_ORDER != 5:
        raise RuntimeError("ARCHIVED_ENGINE_SETTINGS_CHANGED")
    replay.STEP_COUNTS = STEP_COUNTS
    ctx.prec = replay.PRECISION_BITS
    outward_ball(fmpq(1, 3), fmpq(1, 2))
    name, name_q = PARAMETERS[job["param"]]
    lo, hi = fmpq(job["lo"]), fmpq(job["hi"])
    parameter = outward_ball(lo, hi)
    setattr(replay, name_q, parameter)
    setattr(replay, name, f"[{job['lo']}, {job['hi']}]")
    extra_bounds = []
    for extra_name, extra_lo, extra_hi in job.get("extra_params", []):
        if extra_name == job["param"] or extra_name not in PARAMETERS:
            raise RuntimeError("BAD_EXTRA_PARAMETER")
        extra_attr, extra_attr_q = PARAMETERS[extra_name]
        extra_ball = outward_ball(fmpq(extra_lo), fmpq(extra_hi))
        setattr(replay, extra_attr_q, extra_ball)
        setattr(replay, extra_attr, f"[{extra_lo}, {extra_hi}]")
        extra_bounds.append([extra_name] + [str(x) for x in replay.bounds(extra_ball)])
    replay.ROOT_CENTER, replay.ROOT_CENTER_Q = job["A0"], replay.dyadic(job["A0"])
    replay.ROOT_LO, replay.ROOT_LO_Q = job["A_lo"], replay.dyadic(job["A_lo"])
    replay.ROOT_HI, replay.ROOT_HI_Q = job["A_hi"], replay.dyadic(job["A_hi"])
    replay.upper_quantities = recorded_upper_quantities
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        replay.main()
    result = json.loads(captured.getvalue())
    plo, phi = replay.bounds(parameter)
    record = {
        "schema": "family-background-independent-v3",
        "job": job,
        "step_counts": list(STEP_COUNTS),
        "parameter_ball_exact_bounds": [str(plo), str(phi)],
        "extra_parameter_balls_exact_bounds": extra_bounds,
        "box_exact_dyadic_bounds": [str(replay.ROOT_LO_Q), str(replay.ROOT_HI_Q)],
        "centre_exact_dyadic": str(replay.ROOT_CENTER_Q),
        "consumption": {"upper_quantity_calls": CONSUMPTION["calls"],
                        "min_radius_h": exact(CONSUMPTION["min_radius_h"]),
                        "min_radius_G": exact(CONSUMPTION["min_radius_G"])},
        "engine_result": result,
    }
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
