"""R1 entrypoint correcting only the Arb quotient-control predicate."""

from flint import arb

import validated_sensitivity_newton as producer


def corrected_dual_algebra_controls() -> dict[str, bool]:
    x = producer.TimeDual(arb(2), arb(3))
    y = producer.TimeDual(arb(5), arb(7))
    quotient = x / y
    return {
        "product_rule": (x * y).v == 10 and (x * y).d == 29,
        "quotient_value_contains_reference": quotient.v.contains(arb(2) / 5),
        "quotient_derivative_contains_reference": quotient.d.contains(arb(1) / 25),
        "square_rule": (x**2).v == 4 and (x**2).d == 12,
        "exp_rule_contains_reference": x.exp().d.contains(arb(3) * arb(2).exp()),
    }


producer.dual_algebra_controls = corrected_dual_algebra_controls


if __name__ == "__main__":
    producer.main()
