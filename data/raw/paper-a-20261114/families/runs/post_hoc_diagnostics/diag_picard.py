"""POST-HOC DIAGNOSTIC ONLY (labelled; changes no verdict, rescoring nothing).

Re-runs the archived independent engine's centre flow for one failed V
sub-box exactly as fam_bg_independent.py configures it, and wraps picard_box
to report, at the failing cell, which state components fail strict inclusion
and whether any enclosure is non-finite.  The engine source is the frozen
byte-identical copy in the job directory.

usage (from a copy of the failed bgi job directory):
    python -I -B boot.py diag_picard.py
"""
import json

from flint import ctx, fmpq

import independent_d1_replay as replay

NAMES = ["A", "H", "phi", "S", "Z", "curvature", "A_a", "H_a", "phi_a", "S_a", "Z_a", "curvature_a"]
REPORT = {"cells_done": 0}
_archived_picard = replay.picard_box


def diagnosing_picard(state, step):
    try:
        box, iterations = _archived_picard(state, step)
        REPORT["cells_done"] += 1
        return box, iterations
    except RuntimeError:
        time_interval = replay.ball(fmpq(0), step)
        box = [replay.inflate(replay.hull(v, v + time_interval * d)) for v, d in zip(state, replay.rhs(state))]
        for _ in range(replay.MAX_PICARD_ITERATIONS):
            image = [replay.hull(v, v + time_interval * d) for v, d in zip(state, replay.rhs(box))]
            box = [replay.inflate(replay.hull(o, i)) for o, i in zip(box, image)]
        image = [replay.hull(v, v + time_interval * d) for v, d in zip(state, replay.rhs(box))]
        rows = []
        for name, value, outer, inner in zip(NAMES, state, box, image):
            rows.append({"component": name, "state_mid": str(value.mid()), "state_rad": str(value.rad()),
                         "state_finite": value.is_finite(), "box_finite": outer.is_finite(),
                         "image_finite": inner.is_finite(),
                         "strictly_inside": replay.strictly_contains(outer, inner) if outer.is_finite() and inner.is_finite() else False})
        REPORT["failing_cell"] = REPORT["cells_done"]
        REPORT["components"] = rows
        raise


def main():
    with open("job.json") as handle:
        job = json.load(handle)
    ctx.prec = replay.PRECISION_BITS
    lo, hi = fmpq(job["lo"]), fmpq(job["hi"])
    replay.V1_Q = replay.ball(lo, hi)
    centre = replay.dyadic(job["A0"])
    replay.picard_box = diagnosing_picard
    try:
        replay.run_event(centre, centre, 8192)
        REPORT["outcome"] = "COMPLETED_WITHOUT_FAILURE"
    except RuntimeError as exc:
        REPORT["outcome"] = repr(exc)
    print(json.dumps({"label": "POST_HOC_DIAGNOSTIC_NOT_A_VERDICT", "job": job, "report": REPORT}, indent=1))


if __name__ == "__main__":
    main()
