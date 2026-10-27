#!/usr/bin/env python3
"""Dependency-free exact checks for the formal static-reduction lemma.

The checker implements a small Laurent-polynomial algebra over ``Fraction``.
It deliberately uses no computer-algebra package, floating-point arithmetic,
source certificate, or numerical result.
"""

from fractions import Fraction


NAMES = ("H", "S", "phi", "m2", "k", "E", "psi", "psiz", "phiz", "tau", "tau_phi")
NVAR = len(NAMES)


class Poly:
    """Sparse Laurent polynomial with exact rational coefficients."""

    def __init__(self, terms=None):
        reduced = {}
        for powers, coefficient in (terms or {}).items():
            if len(powers) != NVAR:
                raise ValueError("wrong monomial dimension")
            value = Fraction(coefficient)
            if value:
                reduced[powers] = reduced.get(powers, Fraction(0)) + value
        self.terms = {powers: value for powers, value in reduced.items() if value}

    @classmethod
    def constant(cls, value):
        value = Fraction(value)
        if not value:
            return cls()
        return cls({(0,) * NVAR: value})

    @classmethod
    def variable(cls, index):
        powers = [0] * NVAR
        powers[index] = 1
        return cls({tuple(powers): Fraction(1)})

    @classmethod
    def monomial(cls, index, power):
        powers = [0] * NVAR
        powers[index] = power
        return cls({tuple(powers): Fraction(1)})

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Poly) else Poly.constant(value)

    def __add__(self, other):
        other = self.coerce(other)
        terms = dict(self.terms)
        for powers, value in other.terms.items():
            terms[powers] = terms.get(powers, Fraction(0)) + value
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly({powers: -value for powers, value in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        terms = {}
        for left_powers, left_value in self.terms.items():
            for right_powers, right_value in other.terms.items():
                powers = tuple(a + b for a, b in zip(left_powers, right_powers))
                terms[powers] = terms.get(powers, Fraction(0)) + left_value * right_value
        return Poly(terms)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        scalar = Fraction(scalar)
        if not scalar:
            raise ZeroDivisionError
        return Poly({powers: value / scalar for powers, value in self.terms.items()})

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("polynomial exponent must be a nonnegative integer")
        result = Poly.constant(1)
        factor = self
        while exponent:
            if exponent & 1:
                result = result * factor
            factor = factor * factor
            exponent //= 2
        return result

    def substitute(self, replacements):
        result = Poly.constant(0)
        variables = [Poly.variable(index) for index in range(NVAR)]
        for powers, coefficient in self.terms.items():
            term = Poly.constant(coefficient)
            for index, exponent in enumerate(powers):
                if exponent:
                    term *= replacements.get(index, variables[index]) ** exponent
            result += term
        return result

    def is_zero(self):
        return not self.terms

    def compact(self):
        return {str(powers): str(value) for powers, value in sorted(self.terms.items())}


def require_zero(name, expression):
    if not expression.is_zero():
        raise AssertionError(f"{name} failed: {expression.compact()}")
    print(f"{name}=PASS")


H, S, phi, m2, k, E, psi, psiz, phiz, tau, tau_phi = [
    Poly.variable(index) for index in range(NVAR)
]

# Proper-distance IVP and E=exp(-2A).
Hs = -(S**2) / 3 - k * E
Ss = m2 * phi - 4 * H * S
phis = S
Es = -2 * H * E

C = H**2 - 1 - S**2 / 12 + m2 * phi**2 / 12 - k * E
C_s = 2 * H * Hs - S * Ss / 6 + m2 * phi * phis / 6 - k * Es
require_zero("constraint_propagation", C_s)

# The ss and tangential Einstein residuals both reduce to 6*C after the IVP
# equation for H_s is used.  This checks all displayed coefficients and signs.
einstein_ss = 6 * H**2 - 6 * k * E - 6 - (S**2 - m2 * phi**2) / 2
require_zero("ss_einstein_reduction", einstein_ss - 6 * C)

einstein_tangent = 3 * Hs + 6 * H**2 - 3 * k * E - 6 + (S**2 + m2 * phi**2) / 2
require_zero("tangential_einstein_reduction", einstein_tangent - 6 * C)

# Coordinate conversion.  Laurent monomials allow the substitutions
# H=psi_z/psi^2, S=Phi_z/psi, E=psi^-2 to be made literally before
# multiplication by psi^4.
conformal_from_C = psi**4 * C.substitute(
    {
        0: psiz * Poly.monomial(6, -2),
        1: phiz * Poly.monomial(6, -1),
        5: Poly.monomial(6, -2),
    }
)
conformal_displayed = (
    psiz**2
    - psi**4
    - psi**2 * phiz**2 / 12
    + m2 * psi**4 * phi**2 / 12
    - k * psi**2
)
require_zero("conformal_first_integral", conformal_from_C - conformal_displayed)

# Wall identity.  Squaring makes the opposite lower/upper signs immaterial,
# while the half-Robin factor remains visible in the coefficient 1/48.
wall_constraint = H**2 - 1 - S**2 / 12 + m2 * phi**2 / 12
wall_from_junction = wall_constraint.substitute({0: tau / 6, 1: tau_phi / 2})
wall_displayed = tau**2 / 36 - 1 - tau_phi**2 / 48 + m2 * phi**2 / 12
require_zero("wall_identity", wall_from_junction - wall_displayed)

print("FORMAL_REDUCTION_IDENTITY_CHECK=PASS")
