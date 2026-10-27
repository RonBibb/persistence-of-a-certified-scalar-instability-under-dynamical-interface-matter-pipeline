"""Pure logic and analytic helpers for the warped-Kottler barrier control.

This module does not load or qualify P407.  Its production-parameter case is a
conditional model control because the positive-curvature warp/scalar
background has numerical-candidate, not exact-existence, status.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import mpmath as mp


K_CANDIDATE_TEXT: Final[str] = "0.0003268413384542497"


def candidate_curvature() -> mp.mpf:
    """Construct the retained decimal at the caller's active precision."""

    return mp.mpf(K_CANDIDATE_TEXT)


def lapse_function(r: mp.mpf, mass: mp.mpf, curvature: mp.mpf) -> mp.mpf:
    """Kottler f=1-2M/r-k r^2 for Ric(gamma)=3k gamma."""

    return 1 - 2 * mass / r - curvature * r * r


def horizon_roots(mass: mp.mpf, curvature: mp.mpf) -> tuple[mp.mpf, mp.mpf]:
    """Return black-hole and cosmological roots in the sub-Nariai case."""

    if mass <= 0 or curvature <= 0 or 27 * curvature * mass * mass >= 1:
        raise ValueError("requires M>0, k>0 and 27 k M^2 < 1")
    roots = mp.polyroots([curvature, 0, -1, 2 * mass], maxsteps=1000)
    positive = sorted(
        mp.re(x) for x in roots if abs(mp.im(x)) < mp.mpf("1e-40") and mp.re(x) > 0
    )
    if len(positive) != 2:
        raise ArithmeticError("expected exactly two positive Kottler horizons")
    return positive[0], positive[1]


def barrier_remainder() -> mp.mpf:
    """Full E remainder for psi(z)^2(Kottler_4+dz^2) at fixed r.

    A=B=psi^2 have no r or time derivatives, U_0=V_0=0, and
    section normality gives k^z=0.  Thus every term in the previously derived
    production-variable expression vanishes, including the compact-tilt term.
    """

    return mp.mpf("0")


def normalized_barrier_expansion(radius: mp.mpf) -> mp.mpf:
    """theta_plus/k^r on a fixed-radius Kottler cylinder."""

    if radius <= 0:
        raise ValueError("radius must be positive")
    return 2 / radius + barrier_remainder()


def barrier_expansion(
    radius: mp.mpf, mass: mp.mpf, curvature: mp.mpf, warp: mp.mpf
) -> mp.mpf:
    """Expansion of k=T+nu on a timelike static-region cylinder."""

    f_value = lapse_function(radius, mass, curvature)
    if f_value <= 0 or warp <= 0:
        raise ValueError("barrier must lie in f>0 with positive warp")
    return 2 * mp.sqrt(f_value) / (warp * radius)


def cap_expansions(
    radius: mp.mpf, mass: mp.mpf, curvature: mp.mpf
) -> tuple[mp.mpf, mp.mpf]:
    """Unnormalised outgoing/ingoing expansions on a fixed-r cap.

    In ingoing Eddington-Finkelstein coordinates take
    l=d_v+(f/2)d_r and n=-d_r. Positive rescaling does not change signs.
    """

    if radius <= 0:
        raise ValueError("radius must be positive")
    return lapse_function(radius, mass, curvature) / radius, -2 / radius


def horizon_surface_gravity(
    horizon_radius: mp.mpf, mass: mp.mpf, curvature: mp.mpf
) -> mp.mpf:
    """One half of f' at a Kottler horizon."""

    return mass / horizon_radius**2 - curvature * horizon_radius


def outgoing_arrival_time(
    launch_radius: mp.mpf,
    target_radius: mp.mpf,
    mass: mp.mpf,
    curvature: mp.mpf,
) -> mp.mpf:
    """Advanced-time interval for the exact outgoing radial null curve."""

    if not 0 < launch_radius < target_radius:
        raise ValueError("require 0<launch_radius<target_radius")
    rb, rc = horizon_roots(mass, curvature)
    if not rb < launch_radius < target_radius < rc:
        raise ValueError("both radii must lie strictly in the static exterior")
    return mp.quad(
        lambda r: 2 / lapse_function(r, mass, curvature),
        [launch_radius, target_radius],
    )


def tau_slice_bracket_width(
    inner_radius: mp.mpf,
    outer_radius: mp.mpf,
    mass: mp.mpf,
    curvature: mp.mpf,
    warp_at_z: mp.mpf,
) -> mp.mpf:
    """Physical fixed-z radial arc length on tau=v-r=constant."""

    if not 0 < inner_radius < outer_radius or warp_at_z <= 0:
        raise ValueError("ordered positive radii and positive warp are required")
    return warp_at_z * mp.quad(
        lambda r: mp.sqrt(2 - lapse_function(r, mass, curvature)),
        [inner_radius, outer_radius],
    )


@dataclass(frozen=True)
class BracketAuthority:
    background_exact: bool
    same_development: bool
    einstein_base_replacement_exact: bool
    pure_potential_brane_data_preserved: bool
    ncc: bool
    closed_causal_future: bool
    cap_expansions_continuum_enclosed: bool
    barrier_all_future_positive: bool
    barrier_separates_cap_from_outer_end: bool
    exterior_causal_past_equality_proved: bool
    visible_continuum_curve_enclosed: bool
    connected_launch_curve: bool
    common_exterior_id: bool


def classify_authority(authority: BracketAuthority) -> str:
    """Fail-closed classification for one central end-relative bracket."""

    if not authority.background_exact:
        return "CONDITIONAL-MODEL-CONTROL-ONLY"
    capture = all(
        (
            authority.same_development,
            authority.einstein_base_replacement_exact,
            authority.pure_potential_brane_data_preserved,
            authority.ncc,
            authority.closed_causal_future,
            authority.cap_expansions_continuum_enclosed,
            authority.barrier_all_future_positive,
            authority.barrier_separates_cap_from_outer_end,
        )
    )
    if not capture:
        return "CAPTURE-AUTHORITY-INCOMPLETE"
    if not authority.exterior_causal_past_equality_proved:
        return "OUTER-END-TRANSFER-INCOMPLETE"
    if not authority.visible_continuum_curve_enclosed:
        return "VISIBLE-ENDPOINT-INCOMPLETE"
    if not (authority.connected_launch_curve and authority.common_exterior_id):
        return "CENTRAL-BRACKET-INCOMPLETE"
    return "ONE-CENTRAL-END-RELATIVE-BRACKET-QUALIFIED"
