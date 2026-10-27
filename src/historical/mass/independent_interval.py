"""Independent validated central-mode flow in the physical proper coordinate.

The primary polynomial E-variable implementation is not imported. This engine
uses exp(-2W), a separately written coefficient recurrence, and outward Arb
Picard/Taylor enclosures. The proof method follows the inspected sealed D1
independent replay; no earlier numerical enclosure is substituted for a step.

State order: W, H, Phi, T, psi, f, g. The scalar T may cross zero.
This module performs no scientific run on import and writes no files.
"""

from fractions import Fraction

from flint import arb, fmpq


ORDER = 5
MAX_PICARD_ITERATIONS = 32


def exact_ball(value):
    if isinstance(value, arb):
        return value
    if isinstance(value, fmpq):
        return arb(value)
    if isinstance(value, float):
        raise TypeError("Pass exact rational model values, not binary64 decimals")
    q = Fraction(value)
    return arb(fmpq(q.numerator, q.denominator))


def bounds(value):
    return value.lower().fmpq(), value.upper().fmpq()


def interval(lo, hi):
    if lo > hi:
        raise ValueError("Reversed exact interval")
    return arb((lo + hi) / 2, (hi - lo) / 2)


def hull(left, right):
    ll, lh = bounds(left)
    rl, rh = bounds(right)
    return interval(min(ll, rl), max(lh, rh))


def enlarge(value):
    lo, hi = bounds(value)
    padding = (hi - lo) / 8 + fmpq(1, 2**640)
    return interval(lo - padding, hi + padding)


def strictly_inside(inner, outer):
    il, ih = bounds(inner)
    ol, oh = bounds(outer)
    return ol < il and ih < oh


def excludes_zero(value):
    lo, hi = bounds(value)
    return hi < 0 or lo > 0


def contains_rational(value, target):
    lo, hi = bounds(value)
    return lo <= target <= hi


def initial(A, mu, model):
    """Return a nonzero lower-wall/constraint profile and fixed parameters."""
    p = {name: exact_ball(value) for name, value in model.items()}
    a, p["mu"] = exact_ball(A), exact_ball(mu)
    displacement = a - p["v0"]
    H = -(p["lambda_a"] + p["gamma"] * displacement * displacement / 2) / 6
    T = p["gamma"] * displacement / 2
    p["k"] = H * H - 1 - T * T / 12 + p["m2"] * a * a / 12
    p["B0"] = p["gamma"] * T / 2 - (p["m2"] * a - 4 * H * T)
    if not excludes_zero(p["B0"]):
        raise RuntimeError("Independent lower normalization denominator contains zero")
    f = 3 * (p["mu"] + 4 * p["k"]) / p["B0"]
    g = p["gamma"] * f / 2 - 2 * T
    return [arb(0), H, a, T, arb(1), f, g], p


def rhs(state, p):
    W, H, phi, T, psi, f, g = state
    em2W = (-2 * W).exp()
    # Use products: the pinned Arb binding's generic power can return nan for
    # a tiny zero-straddling ball, whereas multiplication remains outward.
    return [H, -T * T / 3 - p["k"] * em2W, T,
            p["m2"] * phi - 4 * H * T,
            -2 * H * psi - T * f / 3,
            g,
            -4 * H * g + (p["m2"] - p["mu"] * em2W + 2 * T * T) * f
            + (12 * H * T - 4 * p["m2"] * phi) * psi]


def convolution(left, right, degree):
    total = arb(0)
    for j in range(degree + 1):
        total += left[j] * right[degree - j]
    return total


def triple_convolution(first, second, third, degree):
    total = arb(0)
    for j in range(degree + 1):
        for k in range(degree - j + 1):
            total += first[j] * second[k] * third[degree - j - k]
    return total


def exponential_coefficients(exponent, degree):
    output = [exponent[0].exp()]
    for n in range(1, degree + 1):
        total = arb(0)
        for j in range(1, n + 1):
            total += j * exponent[j] * output[n - j]
        output.append(total / n)
    return output


def taylor_coefficients(state, order, p):
    """Normalized derivatives from direct exponential/convolution recurrences."""
    if len(state) != 7:
        raise ValueError("Independent state must have seven entries")
    coefficients = [[value] for value in state]
    W, H, phi, T, psi, f, g = coefficients
    for n in range(order):
        em2W = exponential_coefficients([-2 * value for value in W], n)
        derivatives = [
            H[n],
            -convolution(T, T, n) / 3 - p["k"] * em2W[n],
            T[n],
            p["m2"] * phi[n] - 4 * convolution(H, T, n),
            -2 * convolution(H, psi, n) - convolution(T, f, n) / 3,
            g[n],
            -4 * convolution(H, g, n) + p["m2"] * f[n]
            - p["mu"] * convolution(em2W, f, n)
            + 2 * triple_convolution(T, T, f, n)
            + 12 * triple_convolution(H, T, psi, n)
            - 4 * p["m2"] * convolution(phi, psi, n),
        ]
        for row, derivative in zip(coefficients, derivatives):
            row.append(derivative / (n + 1))
    return coefficients


def picard_box(state, h, p):
    if h <= 0:
        raise ValueError("Validated step length must be positive")
    dt = interval(fmpq(0), h)
    box = [enlarge(hull(y, y + dt * v)) for y, v in zip(state, rhs(state, p))]
    for iteration in range(1, MAX_PICARD_ITERATIONS + 1):
        candidate = [hull(y, y + dt * v) for y, v in zip(state, rhs(box, p))]
        if all(strictly_inside(inner, outer) for inner, outer in zip(candidate, box)):
            return box, iteration
        box = [enlarge(hull(outer, inner)) for outer, inner in zip(box, candidate)]
    raise RuntimeError("Independent Picard box did not strictly contain its image")


def range_on_cell(cell, offset_lo, offset_hi):
    """Enclose all states at every time in a cell subinterval, not endpoints."""
    if not fmpq(0) <= offset_lo <= offset_hi <= cell["step"]:
        raise ValueError("Event evaluation interval is outside validated cell")
    offset = interval(offset_lo, offset_hi)
    output = []
    for point, remainder in zip(cell["point_coefficients"], cell["remainder_coefficient"]):
        value = remainder
        for coefficient in reversed(point):
            value = value * offset + coefficient
        output.append(value)
    return output


def step(state, h, p):
    """One Picard-validated step, with a fifth-derivative remainder enclosure."""
    box, iterations = picard_box(state, h, p)
    point = taylor_coefficients(state, ORDER - 1, p)
    remainder = [row[ORDER] for row in taylor_coefficients(box, ORDER, p)]
    cell = {"box": box, "point_coefficients": point,
            "remainder_coefficient": remainder, "step": h,
            "picard_iterations": iterations}
    return range_on_cell(cell, h, h), cell


def determinant(state, p):
    W, H, phi, T, psi, f, g = state
    return g + 2 * T * psi + p["gamma"] * f / 2


def constraint(state, p):
    W, H, phi, T, psi, f, g = state
    return (T * g - (p["m2"] * phi - 4 * H * T) * f
            + (2 * T * T - 3 * (p["mu"] + 4 * p["k"]) * (-2 * W).exp()) * psi)


def first_integral(state, p):
    W, H, phi, T, psi, f, g = state
    return H * H - 1 - T * T / 12 + p["m2"] * phi * phi / 12 - p["k"] * (-2 * W).exp()


def geometry(cell, p):
    W, H, phi, T, psi, f, g = cell["box"]
    return {"W": W, "psi": psi, "f": f, "warp_squared": (2 * W).exp(),
            "norm_density": 2 * (2 * W).exp() * (f * f + 6 * psi * psi),
            "displacement_density": -2 * psi,
            "constraint": constraint(cell["box"], p),
            "first_integral": first_integral(cell["box"], p)}


def algebra_controls():
    """Exact synthetic controls only; this is not the D1 physical background."""
    exponent = [arb(0), arb(1), arb(0), arb(0), arb(0), arb(0)]
    ec = exponential_coefficients(exponent, 5)
    factorial = 1
    exp_pass = True
    for degree, coefficient in enumerate(ec):
        if degree:
            factorial *= degree
        exp_pass &= contains_rational(coefficient, fmpq(1, factorial))
    p = {"m2": arb(fmpq(41, 100)), "mu": arb(0), "k": arb(0), "gamma": arb(20)}
    vacuum = [arb(0), arb(-1), arb(0), arb(0), arb(1), arb(0), arb(0)]
    coefficients = taylor_coefficients(vacuum, 5, p)
    psi_pass = True
    factorial = 1
    for degree, coefficient in enumerate(coefficients[4]):
        if degree:
            factorial *= degree
        psi_pass &= contains_rational(coefficient, fmpq(2**degree, factorial))
    return {"exp_series_through_order5": bool(exp_pass),
            "flat_vacuum_mode_coefficients": bool(psi_pass),
            "pass": bool(exp_pass and psi_pass)}


def symbolic_controls():
    """Exact identities supporting constraint preservation and lower launch."""
    import sympy as sp

    W, H, P, T, psi, f, g, k, mu, m2, gamma = sp.symbols("W H P T psi f g k mu m2 gamma")
    em2W = sp.exp(-2 * W)
    C = T * g - (m2 * P - 4 * H * T) * f + (2 * T**2 - 3 * (mu + 4 * k) * em2W) * psi
    flow = [H, -T**2 / 3 - k * em2W, T, m2 * P - 4 * H * T,
            -2 * H * psi - T * f / 3, g,
            -4 * H * g + (m2 - mu * em2W + 2 * T**2) * f + (12 * H * T - 4 * m2 * P) * psi]
    variables = [W, H, P, T, psi, f, g]
    propagation = sp.simplify(sum(sp.diff(C, q) * v for q, v in zip(variables, flow)) + 4 * H * C) == 0
    B0 = gamma * T / 2 - (m2 * P - 4 * H * T)
    f0 = 3 * (mu + 4 * k) / B0
    g0 = gamma * f0 / 2 - 2 * T
    launch_substitution = {W: 0, psi: 1, f: f0, g: g0}
    launch_constraint = sp.simplify(C.subs(launch_substitution, simultaneous=True)) == 0
    lower_robin = sp.simplify(g0 + 2 * T - gamma * f0 / 2) == 0
    return {"C_s_plus_4HC_identically_zero": bool(propagation),
            "C_at_launch_identically_zero": bool(launch_constraint),
            "lower_Robin_identically_zero": bool(lower_robin),
            "pass": bool(propagation and launch_constraint and lower_robin)}
