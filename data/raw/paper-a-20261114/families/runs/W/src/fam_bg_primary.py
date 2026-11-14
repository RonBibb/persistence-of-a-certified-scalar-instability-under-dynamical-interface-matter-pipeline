"""Family wrapper for the archived primary background producer.

The archived producer validated_sensitivity_newton.py is imported unchanged,
together with the archived confirm_32768.py settings (32768 cells, 768-bit
Arb, corrected dual-algebra controls).  One upper-wall parameter that the
bulk flow never reads (v1 or lambda_b) becomes an outward Arb ball over the
frozen sub-box; the shooting box and Newton centre become the frozen family
values.  Every other parameter keeps its archived exact value.

Consumption evidence: event_quantities, the producer's only reader of v1 and
lambda_b, is wrapped so that every call's exact radii of h and G are recorded.
A consumed v1 ball forces rad(h) >= 10 rad(v1) and a consumed lambda_b ball
forces rad(G) >= rad(lambda_b)/6 on every call, because h is affine in v1
with slope -gamma/2 and G is affine in lambda_b with slope -1/6 and Arb
radii only grow under these operations.  The producer's JSON is embedded
verbatim in the printed record.
"""
import contextlib
import io
import json

from flint import arb, ctx, fmpq

import confirm_32768  # noqa: F401  applies the archived step count, precision and controls
import validated_sensitivity_newton as producer

PARAMETERS = {"v1": ("V1", "V1_Q"), "lambda_b": ("LAMBDA_B", "LAMBDA_B_Q")}
CONSUMPTION = {"calls": 0, "min_radius_h": None, "min_radius_G": None}
_archived_event_quantities = producer.event_quantities


def recorded_event_quantities(z):
    quantities = _archived_event_quantities(z)
    CONSUMPTION["calls"] += 1
    for key, slot in (("h", "min_radius_h"), ("G", "min_radius_G")):
        radius = quantities[key].rad()
        if CONSUMPTION[slot] is None or radius < CONSUMPTION[slot]:
            CONSUMPTION[slot] = radius
    return quantities


def outward_ball(lo, hi):
    value = producer.ball(lo, hi)
    for candidate in (value, arb(value)):
        clo, chi = producer.bounds(candidate)
        if not (clo <= lo and hi <= chi):
            raise RuntimeError("PARAMETER_BALL_NOT_OUTWARD")
    return value


def exact(value):
    return None if value is None else str(producer.bounds(value)[0])


def main():
    with open("job.json") as handle:
        job = json.load(handle)
    if producer.STEP_COUNTS != (32768,) or producer.PRECISION_BITS != 768:
        raise RuntimeError("ARCHIVED_CONFIRMATION_SETTINGS_NOT_APPLIED")
    ctx.prec = producer.PRECISION_BITS
    outward_ball(fmpq(1, 3), fmpq(1, 2))
    name, name_q = PARAMETERS[job["param"]]
    lo, hi = fmpq(job["lo"]), fmpq(job["hi"])
    parameter = outward_ball(lo, hi)
    setattr(producer, name_q, parameter)
    setattr(producer, name, f"[{job['lo']}, {job['hi']}]")
    extra_bounds = []
    for extra_name, extra_lo, extra_hi in job.get("extra_params", []):
        if extra_name == job["param"] or extra_name not in PARAMETERS:
            raise RuntimeError("BAD_EXTRA_PARAMETER")
        extra_attr, extra_attr_q = PARAMETERS[extra_name]
        extra_ball = outward_ball(fmpq(extra_lo), fmpq(extra_hi))
        setattr(producer, extra_attr_q, extra_ball)
        setattr(producer, extra_attr, f"[{extra_lo}, {extra_hi}]")
        extra_bounds.append([extra_name] + [str(x) for x in producer.bounds(extra_ball)])
    producer.FULL_A_LO, producer.FULL_A_HI = job["A_lo"], job["A_hi"]
    producer.FULL_A_LO_Q = producer.dyadic(job["A_lo"])
    producer.FULL_A_HI_Q = producer.dyadic(job["A_hi"])
    producer.ROOT_CENTER = job["A0"]
    producer.ROOT_CENTER_Q = producer.dyadic(job["A0"])
    producer.ROOT_BOXES = {"family": (job["A_lo"], job["A_hi"])}
    producer.event_quantities = recorded_event_quantities
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        producer.main()
    result = json.loads(captured.getvalue())
    plo, phi = producer.bounds(parameter)
    record = {
        "schema": "family-background-primary-v3",
        "job": job,
        "parameter_ball_exact_bounds": [str(plo), str(phi)],
        "extra_parameter_balls_exact_bounds": extra_bounds,
        "box_exact_dyadic_bounds": [str(producer.FULL_A_LO_Q), str(producer.FULL_A_HI_Q)],
        "centre_exact_dyadic": str(producer.ROOT_CENTER_Q),
        "consumption": {"event_quantity_calls": CONSUMPTION["calls"],
                        "min_radius_h": exact(CONSUMPTION["min_radius_h"]),
                        "min_radius_G": exact(CONSUMPTION["min_radius_G"])},
        "producer_result": result,
    }
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
