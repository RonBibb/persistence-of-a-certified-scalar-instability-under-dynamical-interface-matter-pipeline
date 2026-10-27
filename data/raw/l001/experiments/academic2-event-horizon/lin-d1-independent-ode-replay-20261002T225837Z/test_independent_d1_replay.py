#!/usr/bin/env python3
"""Fast non-scientific controls for the independent D1 replay source."""

from flint import arb, ctx

import independent_d1_replay as replay


def main() -> None:
    ctx.prec = replay.PRECISION_BITS
    controls = replay.algebra_controls()
    assert all(controls.values()), controls

    root_box = replay.ball(replay.ROOT_LO_Q, replay.ROOT_HI_Q)
    state = replay.launch(root_box)
    assert len(state) == 12
    assert len(replay.rhs(state)) == 12
    assert replay.contains_zero(replay.first_integral(state))
    assert replay.contains_zero(replay.lower_wall_identity(root_box))

    step = replay.S_END / 8192
    enclosure, iterations = replay.picard_box(state, step)
    assert 1 <= iterations <= replay.MAX_PICARD_ITERATIONS
    advanced = replay.advance(state, enclosure, step)
    assert len(advanced) == 12
    assert all(value.is_finite() for value in advanced)

    exponential = replay.Series([arb(0), arb(1), arb(0), arb(0), arb(0), arb(0)]).exp()
    assert exponential.coefficients[3].overlaps(arb(1) / 6)
    assert exponential.coefficients[4].overlaps(arb(1) / 24)
    print("PASS", controls, "picard_iterations", iterations)


if __name__ == "__main__":
    main()
