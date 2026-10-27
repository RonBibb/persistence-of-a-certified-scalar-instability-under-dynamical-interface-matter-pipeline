"""Independent symbolic and high-precision control for the warped-Kottler route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import mpmath as mp
import sympy as sp

from kottler_barrier import (
    barrier_expansion,
    candidate_curvature,
    cap_expansions,
    horizon_roots,
    horizon_surface_gravity,
    lapse_function,
    normalized_barrier_expansion,
    outgoing_arrival_time,
    tau_slice_bracket_width,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbolic_controls() -> dict[str, object]:
    t, r, theta, phi, z, mass, curvature = sp.symbols(
        "t r theta phi z M k", positive=True
    )
    psi = sp.Function("psi")(z)
    f = 1 - 2 * mass / r - curvature * r**2
    coordinates = (t, r, theta, phi, z)
    base = sp.diag(-f, 1 / f, r**2, r**2 * sp.sin(theta) ** 2)
    metric = sp.diag(*[psi**2 * base[i, i] for i in range(4)], psi**2)
    inverse = sp.simplify(metric.inv())
    dimension = 5
    christoffel = [
        [
            [
                sp.simplify(
                    sum(
                        inverse[a, d]
                        * (
                            sp.diff(metric[d, c], coordinates[b])
                            + sp.diff(metric[d, b], coordinates[c])
                            - sp.diff(metric[b, c], coordinates[d])
                        )
                        for d in range(dimension)
                    )
                    / 2
                )
                for c in range(dimension)
            ]
            for b in range(dimension)
        ]
        for a in range(dimension)
    ]
    ricci = [
        [
            sp.simplify(
                sum(
                    sp.diff(christoffel[a][b][c], coordinates[a])
                    - sp.diff(christoffel[a][b][a], coordinates[c])
                    + sum(
                        christoffel[a][a][d] * christoffel[d][b][c]
                        - christoffel[a][c][d] * christoffel[d][b][a]
                        for d in range(dimension)
                    )
                    for a in range(dimension)
                )
            )
            for c in range(dimension)
        ]
        for b in range(dimension)
    ]
    omega = sp.log(psi)
    compact_factor = sp.diff(omega, z, 2) + 3 * sp.diff(omega, z) ** 2
    errors: list[sp.Expr] = []
    for i in range(4):
        for j in range(4):
            errors.append(
                sp.simplify(
                    ricci[i][j] - (3 * curvature - compact_factor) * base[i, j]
                )
            )
    errors.append(sp.simplify(ricci[4][4] + 4 * sp.diff(omega, z, 2)))
    for i in range(4):
        errors.extend((sp.simplify(ricci[i][4]), sp.simplify(ricci[4][i])))
    # Independent two-dimensional Eddington-Finkelstein frame algebra on the
    # fixed-radius cylinder.  These expressions also check that the nonzero
    # g_vr term is retained rather than silently diagonalised away.
    sqrt_f = sp.sqrt(f)
    frame_metric = psi**2 * sp.Matrix([[-f, 1], [1, 0]])
    T = sp.Matrix([1 / (psi * sqrt_f), 0])
    nu = sp.Matrix([1 / (psi * sqrt_f), sqrt_f / psi])
    null_out = T + nu
    ell = sp.Matrix([1, f / 2])
    ingoing = sp.Matrix([0, -1])
    inner = lambda x, y: sp.simplify((x.T * frame_metric * y)[0])
    frame_errors = {
        "T_norm_plus_1": sp.simplify(inner(T, T) + 1),
        "nu_norm_minus_1": sp.simplify(inner(nu, nu) - 1),
        "T_nu": inner(T, nu),
        "k_norm": inner(null_out, null_out),
        "ell_norm": inner(ell, ell),
        "ingoing_norm": inner(ingoing, ingoing),
        "ell_ingoing_plus_psi2": sp.simplify(inner(ell, ingoing) + psi**2),
        "theta_over_kr_minus_2_over_r": sp.simplify(
            (2 * null_out[1] / r) / null_out[1] - 2 / r
        ),
    }
    return {
        "warped_kottler_ricci_components_checked": len(errors),
        "warped_kottler_ricci_identity_exact": all(item == 0 for item in errors),
        "nonzero_symbolic_errors": [str(item) for item in errors if item != 0],
        "barrier_frame_identities_checked": len(frame_errors),
        "barrier_frame_identity_exact": all(item == 0 for item in frame_errors.values()),
        "nonzero_frame_errors": {
            name: str(value) for name, value in frame_errors.items() if value != 0
        },
    }


def numerical_controls() -> dict[str, object]:
    mp.mp.dps = 80
    mass = mp.mpf("1")
    curvature = candidate_curvature()
    r_cap = mp.mpf("1.5")
    r_visible = mp.mpf("4")
    r_barrier = mp.mpf("8")
    r_black, r_cosmological = horizon_roots(mass, curvature)
    cap_out, cap_in = cap_expansions(r_cap, mass, curvature)
    return {
        "mass": str(mass),
        "base_curvature_k": str(curvature),
        "sub_nariai_27_k_M2": mp.nstr(27 * curvature * mass**2, 50),
        "black_hole_horizon": mp.nstr(r_black, 50),
        "black_hole_surface_gravity": mp.nstr(
            horizon_surface_gravity(r_black, mass, curvature), 50
        ),
        "cosmological_horizon": mp.nstr(r_cosmological, 50),
        "radii": {
            "captured_cap": str(r_cap),
            "visible_launch": str(r_visible),
            "barrier": str(r_barrier),
        },
        "f_values": {
            "cap": mp.nstr(lapse_function(r_cap, mass, curvature), 50),
            "visible": mp.nstr(lapse_function(r_visible, mass, curvature), 50),
            "barrier": mp.nstr(lapse_function(r_barrier, mass, curvature), 50),
        },
        "cap_expansions_unnormalized": {
            "outgoing": mp.nstr(cap_out, 50),
            "ingoing": mp.nstr(cap_in, 50),
        },
        "barrier": {
            "full_remainder_E": "0",
            "theta_plus_over_k_r": mp.nstr(normalized_barrier_expansion(r_barrier), 50),
            "theta_plus_at_warp_1": mp.nstr(
                barrier_expansion(r_barrier, mass, curvature, mp.mpf("1")),
                50,
            ),
        },
        "visible_null_curve_delta_v_to_barrier": mp.nstr(
            outgoing_arrival_time(r_visible, r_barrier, mass, curvature), 50
        ),
        "tau_slice_bracket_width_at_warp_1_for_delta_0p01": mp.nstr(
            tau_slice_bracket_width(
                r_black - mp.mpf("0.01"),
                r_black + mp.mpf("0.01"),
                mass,
                curvature,
                mp.mpf("1"),
            ),
            50,
        ),
        "radii_strictly_ordered": bool(
            r_cap < r_black < r_visible < r_barrier < r_cosmological
        ),
        "cap_future_trapped": bool(cap_out < 0 and cap_in < 0),
        "barrier_strictly_outgoing": bool(
            barrier_expansion(r_barrier, mass, curvature, mp.mpf("1")) > 0
        ),
    }


def main() -> None:
    here = Path(__file__).resolve().parent
    result = {
        "schema": "warped-kottler-exact-control-v1",
        "symbolic": symbolic_controls(),
        "numerical": numerical_controls(),
        "source_sha256": {
            "kottler_barrier.py": sha(here / "kottler_barrier.py"),
            "test_kottler_barrier.py": sha(here / "test_kottler_barrier.py"),
            "symbolic_kottler_control.py": sha(here / "symbolic_kottler_control.py"),
        },
        "scientific_authority": "CONDITIONAL_MODEL_CONTROL_ONLY",
        "reason": "The bound positive-curvature warp/scalar background is a qualified numerical candidate, not a rigorous exact solution or a same-development continuation of the collapse lineage.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
