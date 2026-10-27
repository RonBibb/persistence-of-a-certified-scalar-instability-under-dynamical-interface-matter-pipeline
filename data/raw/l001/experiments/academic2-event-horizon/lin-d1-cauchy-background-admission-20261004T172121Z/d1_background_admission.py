#!/usr/bin/env python3
"""Bounded D1-specific Cauchy-background admission and preservation test."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root_scalar


M2 = 0.41
GAMMA = 20.0
V0 = 0.1
V1 = 0.09048374180359596
LAMBDA_A = 5.999990376773895
LAMBDA_B = -6.052844277744164
ROOT_LO = 0.09901086489880687
ROOT_HI = 0.09901086689880687
R_MAX = 10.0
STENCIL = 7
ADMISSION_GRIDS = ((65, 121), (97, 181), (129, 241))
EVOLUTION_GRIDS = ((49, 91), (65, 121))
DT = 0.000125
STEPS = 4

GATES = {
    "terminal_wall": 2e-10,
    "first_integral": 5e-10,
    "hamiltonian_full_finest": 2e-6,
    "hamiltonian_interior_finest": 5e-7,
    "momentum": 1e-14,
    "wall_finest": 2e-6,
    "wall_any": 2e-5,
    "axis": 5e-12,
    "gauge": 5e-5,
    "source_trace": 1e-12,
    "source_moment": 1e-12,
    "outer": 1e-12,
    "adm_acceleration": 5e-5,
    "gh_acceleration": 1e-4,
    "evolution_hamiltonian_floor": 5e-6,
    "evolution_gauge_floor": 2e-4,
    "evolution_wall_floor": 2e-5,
    "evolution_state_change": 5e-6,
}


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def finite_max(value: np.ndarray) -> float:
    array = np.asarray(value, dtype=float)
    return float(np.max(np.abs(array))) if array.size else 0.0


def maximum_record(value: np.ndarray, x: np.ndarray, r: np.ndarray) -> dict[str, Any]:
    array = np.asarray(value, dtype=float)
    index = np.unravel_index(int(np.argmax(np.abs(array))), array.shape)
    return {
        "maximum_absolute": float(abs(array[index])),
        "x_index": int(index[0]),
        "r_index": int(index[1]),
        "x": float(x[index[0]]),
        "r": float(r[index[1]]),
        "signed_value": float(array[index]),
    }


def verify_bindings(root: Path, here: Path) -> list[dict[str, str]]:
    bindings = json.loads((here / "BINDINGS.json").read_text(encoding="utf-8"))
    verified: list[dict[str, str]] = []
    for entry in bindings["parents"] + bindings["production_sources"]:
        path = root / entry["path"]
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise RuntimeError(f"binding changed: {entry['path']} {actual}")
        verified.append({"path": str(path), "sha256": actual, "role": entry.get("role", "production_source")})
    return verified


def launch(a: float) -> tuple[np.ndarray, float]:
    h = -(LAMBDA_A + 0.5 * GAMMA * (a - V0) ** 2) / 6.0
    u = 0.5 * GAMMA * (a - V0)
    k = h * h - 1.0 - u * u / 12.0 + M2 * a * a / 12.0
    return np.asarray((0.0, h, a, u, 0.0), dtype=float), float(k)


def proper_rhs(_s: float, y: np.ndarray, k: float) -> np.ndarray:
    a, h, phi, u, _z = y
    return np.asarray((
        h,
        -u * u / 3.0 - k * math.exp(-2.0 * a),
        u,
        M2 * phi - 4.0 * h * u,
        math.exp(-a),
    ))


def upper_israel(_s: float, y: np.ndarray, _k: float) -> float:
    _a, h, phi, _u, _z = y
    tau = LAMBDA_B + 0.5 * GAMMA * (phi - V1) ** 2
    return float(h - tau / 6.0)


upper_israel.terminal = True
upper_israel.direction = -1


def integrate_to_upper(a: float) -> tuple[float, np.ndarray, float]:
    y0, k = launch(a)
    solution = solve_ivp(
        lambda s, y: proper_rhs(s, y, k),
        (0.0, 2.05), y0, method="DOP853", rtol=2e-13, atol=2e-15,
        max_step=1e-3, events=lambda s, y: upper_israel(s, y, k),
        dense_output=False,
    )
    if not solution.success or not solution.t_events or len(solution.t_events[0]) == 0:
        raise RuntimeError("D1 upper-Israel event was not reached")
    event_index = int(np.argmin(np.abs(solution.y_events[0][:, 1] - (
        LAMBDA_B + 0.5 * GAMMA * (solution.y_events[0][:, 2] - V1) ** 2
    ) / 6.0)))
    return float(solution.t_events[0][event_index]), np.asarray(solution.y_events[0][event_index]), k


def solve_representative_root() -> dict[str, Any]:
    def mismatch(a: float) -> float:
        _d, event, _k = integrate_to_upper(a)
        return float(event[3] + 0.5 * GAMMA * (event[2] - V1))

    left = mismatch(ROOT_LO)
    right = mismatch(ROOT_HI)
    if left == 0.0:
        root = ROOT_LO
    elif right == 0.0:
        root = ROOT_HI
    elif left * right >= 0.0:
        raise RuntimeError(f"certified launch box did not bracket the representative root: {left}, {right}")
    else:
        solved = root_scalar(
            mismatch, bracket=(ROOT_LO, ROOT_HI), method="brentq",
            xtol=5e-15, rtol=1e-14, maxiter=64,
        )
        if not solved.converged:
            raise RuntimeError("representative root solve did not converge")
        root = float(solved.root)
    distance, event, k = integrate_to_upper(root)
    tau = LAMBDA_B + 0.5 * GAMMA * (event[2] - V1) ** 2
    return {
        "a": root,
        "D": distance,
        "event": event,
        "k": k,
        "lower_scalar_residual": float(launch(root)[0][3] - 0.5 * GAMMA * (root - V0)),
        "lower_israel_residual": float(launch(root)[0][1] + (LAMBDA_A + 0.5 * GAMMA * (root - V0) ** 2) / 6.0),
        "upper_scalar_residual": float(event[3] + 0.5 * GAMMA * (event[2] - V1)),
        "upper_israel_residual": float(event[1] - tau / 6.0),
        "endpoint_mismatch_at_box": [left, right],
    }


def make_profile(root: dict[str, Any]):
    length = float(root["event"][4])
    cscale = length / (math.e - 1.0)
    y0, k = launch(float(root["a"]))
    conformal_initial = np.asarray((y0[0], y0[1], y0[2], y0[3], 0.0))

    def rhs_x(_x: float, y: np.ndarray) -> np.ndarray:
        a, h, phi, u, _s = y
        w = math.exp(a)
        factor = cscale * w
        return np.asarray((
            factor * h,
            factor * (-u * u / 3.0 - k * math.exp(-2.0 * a)),
            factor * u,
            factor * (M2 * phi - 4.0 * h * u),
            factor,
        ))

    solution = solve_ivp(
        rhs_x, (1.0, math.e), conformal_initial, method="DOP853",
        rtol=2e-13, atol=2e-15, max_step=(math.e - 1.0) / 4096.0,
        dense_output=True,
    )
    if not solution.success:
        raise RuntimeError("conformal-profile integration failed")

    def sample(x: np.ndarray) -> dict[str, np.ndarray]:
        values = np.asarray(solution.sol(np.asarray(x, dtype=float)))
        return {
            "A": values[0], "H": values[1], "phi": values[2],
            "U": values[3], "s": values[4],
            "w": np.exp(values[0]),
        }

    return sample, length, cscale


def background_record() -> dict[str, float]:
    return {
        "mass_squared": M2,
        "wall_stiffness": GAMMA,
        "v0": V0,
        "v1": V1,
        "wall_target_v0": V0,
        "wall_target_v1": V1,
        "beta_a": LAMBDA_A / 6.0,
        "beta_b": -LAMBDA_B / 6.0,
        "wall_potential_a": 0.0,
        "wall_potential_b": 0.0,
        "retuned_bare_tension_a": LAMBDA_A,
        "retuned_bare_tension_b": LAMBDA_B,
    }


def represented_fields(nx: int, nr: int, sample, k: float, cscale: float) -> dict[str, Any]:
    x = np.linspace(1.0, math.e, int(nx))
    r = np.linspace(0.0, R_MAX, int(nr))
    p = sample(x)
    w = p["w"][:, None]
    f = 1.0 - k * r[None, :] ** 2
    psi = np.broadcast_to(w, (nx, nr)).copy()
    anis_a = np.full((nx, nr), math.log(cscale))
    anis_b = np.broadcast_to(-0.5 * np.log(f), (nx, nr)).copy()
    anis_c = np.zeros((nx, nr))
    alpha = w * np.sqrt(f)
    phi = np.broadcast_to(p["phi"][:, None], (nx, nr)).copy()
    chi = np.zeros((nx, nr))
    q = np.zeros((nx, nr, 9))
    w2 = w * w
    q[:, :, 2] = -w2 * f
    q[:, :, 3] = w2
    q[:, :, 4] = w2 * k / f
    q[:, :, 6] = w2 * cscale * cscale
    q[:, :, 7] = phi
    source = np.zeros((nx, nr, 3))
    source[:, :, 1] = np.broadcast_to((-3.0 * cscale * p["w"] * p["H"])[:, None], (nx, nr))
    source[:, :, 2] = 4.0 * k / f
    return {
        "x": x, "r": r, "profile": p, "f": f, "psi": psi,
        "a": anis_a, "b": anis_b, "c": anis_c, "alpha": alpha,
        "phi": phi, "chi": chi, "q": q,
        "v": np.zeros_like(q), "source": source,
    }


def positivity(fields: dict[str, Any]) -> dict[str, Any]:
    q = fields["q"]
    r = fields["r"]
    radius2 = r[None, :] ** 2
    radial = q[:, :, 3] + radius2 * q[:, :, 4]
    determinant = q[:, :, 6] * radial - radius2 * q[:, :, 1] ** 2
    beta_z = (radial * q[:, :, 0] - radius2 * q[:, :, 1] * q[:, :, 5]) / determinant
    beta_r_coefficient = (-q[:, :, 1] * q[:, :, 0] + q[:, :, 6] * q[:, :, 5]) / determinant
    shift_norm = q[:, :, 0] * beta_z + radius2 * q[:, :, 5] * beta_r_coefficient
    lapse_squared = -q[:, :, 2] + shift_norm
    return {
        "minimum_f": float(np.min(fields["f"])),
        "minimum_lapse_squared": float(np.min(lapse_squared)),
        "minimum_compact_radial_determinant": float(np.min(determinant)),
        "minimum_transverse_metric": float(np.min(q[:, :, 3])),
        "passed": bool(
            np.all(np.isfinite(q)) and np.min(fields["f"]) > 0.0
            and np.min(lapse_squared) > 0.0 and np.min(determinant) > 0.0
            and np.min(q[:, :, 3]) > 0.0
        ),
    }


def axis_residual(fields: dict[str, Any], derivative_matrix) -> dict[str, Any]:
    q = fields["q"]
    source = fields["source"]
    r = fields["r"]
    dr = derivative_matrix(r, 1, STENCIL)
    if hasattr(dr, "toarray"):
        dr = dr.toarray()
    q_radial = np.einsum("jk,ikf->ijf", dr, q)
    h_radial = np.einsum("jk,ikf->ijf", dr, source)
    physical = max(
        finite_max(r[0] * q[:, 0, 1]),
        finite_max(r[0] * q[:, 0, 5]),
        finite_max(r[0] ** 2 * q[:, 0, 4]),
    )
    parity = max(finite_max(q_radial[:, 0]), finite_max(h_radial[:, 0]))
    return {
        "physical_tensor_axis_residual": physical,
        "reduced_even_parity_derivative_maximum": parity,
        "maximum": max(physical, parity),
    }


def adm_acceleration_record(fields: dict[str, Any], anisotropic_metric_acceleration,
                            anisotropic_scalar_acceleration) -> dict[str, Any]:
    zeros = np.zeros_like(fields["psi"])
    metric = anisotropic_metric_acceleration(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"],
        fields["c"], fields["phi"], zeros, zeros, M2,
        cosmological_constant=-6.0, kappa5_squared=1.0,
        stencil_width=STENCIL, lapse=fields["alpha"],
    )
    scalar = anisotropic_scalar_acceleration(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"],
        fields["c"], fields["phi"], M2, lapse=fields["alpha"],
        stencil_width=STENCIL,
    )
    scales = {
        "zz": max(1.0, finite_max(fields["q"][:, :, 6])),
        "radial": max(1.0, finite_max(fields["q"][:, :, 3] + fields["r"][None, :] ** 2 * fields["q"][:, :, 4])),
        "transverse": max(1.0, finite_max(fields["q"][:, :, 3])),
        "zr": 1.0,
        "phi": max(1.0, finite_max(fields["phi"])),
    }
    maxima = {name: finite_max(metric[name]) / scales[name] for name in ("zz", "radial", "transverse", "zr")}
    maxima["phi"] = finite_max(scalar) / scales["phi"]
    return {"by_component": maxima, "maximum_normalized": max(maxima.values())}


def gh_acceleration_record(acceleration: np.ndarray, q: np.ndarray, diagnostic: dict[str, Any]) -> dict[str, Any]:
    by_field = []
    for field in range(9):
        scale = max(1.0, finite_max(q[:, :, field]))
        by_field.append(finite_max(acceleration[:, :, field]) / scale)
    outer = diagnostic.get("outer_sommerfeld") or {}
    axis = diagnostic.get("axis_fit_preference_defect") or {}
    return {
        "maximum_normalized": max(by_field),
        "by_field": by_field,
        "finite": bool(diagnostic.get("finite") and np.all(np.isfinite(acceleration))),
        "wall_correction_count": len(diagnostic.get("wall_corrections") or []),
        "outer_sommerfeld": outer,
        "axis_fit_preference_defect": axis,
        "boundary_closure_mode": diagnostic.get("boundary_closure_mode"),
    }


def dynamic_hamiltonian(position: np.ndarray, velocity: np.ndarray, x: np.ndarray, r: np.ndarray,
                        reduced_state_jets, regular_so3_perturbation_jets,
                        metric_geometry_from_jets) -> np.ndarray:
    first, second = reduced_state_jets(position, velocity, x, r, STENCIL)
    out = np.empty((len(x), len(r)))
    for i in range(len(x)):
        for j in range(len(r)):
            jets = regular_so3_perturbation_jets(
                float(r[j]), position[i, j], first[:, i, j], second[:, :, i, j],
            )
            metric = jets["metric"]
            spatial = metric[1:, 1:]
            spatial_first = jets["metric_first"][1:, 1:, 1:]
            spatial_second = jets["metric_second"][1:, 1:, 1:, 1:]
            geometry = metric_geometry_from_jets(spatial, spatial_first, spatial_second)
            inverse = geometry["inverse_metric"]
            scalar_curvature = float(np.einsum("ij,ij", inverse, geometry["ricci"]))
            beta_covector = metric[0, 1:]
            beta = inverse @ beta_covector
            lapse_squared = -metric[0, 0] + float(beta_covector @ beta)
            if lapse_squared <= 0.0:
                out[i, j] = np.nan
                continue
            lapse = math.sqrt(lapse_squared)
            beta_first = jets["metric_first"][1:, 0, 1:]
            covariant_beta = beta_first - np.einsum(
                "kij,k->ij", geometry["connection"], beta_covector,
            )
            gamma_time = jets["metric_first"][0, 1:, 1:]
            extrinsic = -(gamma_time - covariant_beta - covariant_beta.T) / (2.0 * lapse)
            trace = float(np.einsum("ij,ij", inverse, extrinsic))
            squared = float(np.einsum("ik,jl,ij,kl", inverse, inverse, extrinsic, extrinsic))
            phi_spatial = jets["phi_first"][1:]
            chi_spatial = jets["chi_first"][1:]
            phi_pi = float((jets["phi_first"][0] - beta @ phi_spatial) / lapse)
            chi_pi = float((jets["chi_first"][0] - beta @ chi_spatial) / lapse)
            matter = (
                float(phi_spatial @ inverse @ phi_spatial) + phi_pi * phi_pi
                + M2 * float(jets["phi"]) ** 2
                + float(chi_spatial @ inverse @ chi_spatial) + chi_pi * chi_pi
            )
            out[i, j] = scalar_curvature + trace * trace - squared + 12.0 - matter
    return out


def write_status(output: Path, phase: str, detail: str, started: str) -> None:
    atomic_json(output / "STATUS.json", {
        "schema": "lin-d1-cauchy-background-admission-status-v1",
        "started_utc": started, "updated_utc": utc(), "phase": phase,
        "detail": detail, "pid": os.getpid(),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    started = utc()
    wall_start = time.monotonic()
    result: dict[str, Any] = {
        "schema": "lin-d1-cauchy-background-admission-result-v1",
        "started_utc": started,
        "status": "RUNNING",
        "classification": None,
        "contract_sha256": sha256(here / "CONTRACT.md"),
        "bindings_sha256": sha256(here / "BINDINGS.json"),
        "gates": GATES,
        "admission_grids": [list(item) for item in ADMISSION_GRIDS],
        "evolution_grids": [list(item) for item in EVOLUTION_GRIDS],
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
        "phases": {},
        "first_failed_gate": None,
        "claim_boundary": [
            "One representative member inside the certified D1 root box is tested; the parent interval theorem is not replaced.",
            "A pass is finite-resolution background admission and immediate preservation only, not stability.",
            "No perturbation, static continuation in D, parent-child, causal-horizon, or manuscript claim follows.",
        ],
    }

    try:
        write_status(output, "AUTHENTICATION", "verifying immutable parents and production operators", started)
        result["authority_bindings_verified"] = verify_bindings(root, here)
        source_root = root / "branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src"
        sys.path.insert(0, str(source_root))
        from bhps.adm_corner import _axisymmetric_derivatives
        from bhps.anisotropic_geometry import (
            anisotropic_hamiltonian_residual,
            anisotropic_metric_acceleration,
            anisotropic_scalar_acceleration,
        )
        from bhps.gw_slice_high_order_solver import derivative_matrix
        from bhps.linearized_gh_einstein_scalar import metric_geometry_from_jets
        from bhps.nonlinear_regular_so3_evolution import (
            NativeRegularSO3RHS,
            StageRegularGaugeSource,
            apply_outer_source_sommerfeld,
            compact_wall_position_residuals,
            gauge_constraint_summary,
            outer_sommerfeld_position_residuals,
            reduced_state_jets,
            regular_so3_outward_radial_speed,
        )
        from bhps.regular_so3_gh_reduction import regular_so3_perturbation_jets

        write_status(output, "PHASE_1", "solving the representative D1 root and frozen static-patch profile", started)
        root_record = solve_representative_root()
        sample, length, cscale = make_profile(root_record)
        x_evidence = np.linspace(1.0, math.e, ADMISSION_GRIDS[-1][0])
        p_evidence = sample(x_evidence)
        first_integral = (
            p_evidence["H"] ** 2 - 1.0 - p_evidence["U"] ** 2 / 12.0
            + M2 * p_evidence["phi"] ** 2 / 12.0
            - root_record["k"] * np.exp(-2.0 * p_evidence["A"])
        )
        endpoint_residual = max(
            abs(root_record["lower_scalar_residual"]),
            abs(root_record["lower_israel_residual"]),
            abs(root_record["upper_scalar_residual"]),
            abs(root_record["upper_israel_residual"]),
        )
        finest_fields = represented_fields(
            ADMISSION_GRIDS[-1][0], ADMISSION_GRIDS[-1][1], sample,
            root_record["k"], cscale,
        )
        positive = positivity(finest_fields)
        phase1_gates = {
            "root_inside_certified_box": bool(ROOT_LO <= root_record["a"] <= ROOT_HI),
            "terminal_wall_residual": bool(endpoint_residual < GATES["terminal_wall"]),
            "first_integral": bool(finite_max(first_integral) < GATES["first_integral"]),
            "finite_and_positive": bool(positive["passed"]),
        }
        result["representative_root"] = {
            **{key: value for key, value in root_record.items() if key != "event"},
            "event": root_record["event"].tolist(),
            "conformal_length": length,
            "coordinate_scale": cscale,
        }
        result["phases"]["1_authority_continuum_profile"] = {
            "gates": phase1_gates,
            "maximum_terminal_wall_residual": endpoint_residual,
            "maximum_first_integral_residual": finite_max(first_integral),
            "positivity": positive,
            "passed": all(phase1_gates.values()),
        }
        if not all(phase1_gates.values()):
            result["first_failed_gate"] = next(name for name, passed in phase1_gates.items() if not passed)
            raise StopIteration

        write_status(output, "PHASE_2", "evaluating full-slice Hamiltonian and momentum constraints", started)
        constraint_levels = []
        cached: dict[tuple[int, int], dict[str, Any]] = {}
        for nx, nr in ADMISSION_GRIDS:
            fields = represented_fields(nx, nr, sample, root_record["k"], cscale)
            cached[(nx, nr)] = fields
            zeros = np.zeros((nx, nr))
            hamiltonian = anisotropic_hamiltonian_residual(
                fields["x"], fields["r"], fields["psi"], fields["a"],
                fields["b"], fields["c"], fields["phi"], zeros, zeros, M2,
                cosmological_constant=-6.0, kappa5_squared=1.0,
                stencil_width=STENCIL,
            )
            interior = hamiltonian[3:-3, 3:-3]
            constraint_levels.append({
                "grid": [nx, nr],
                "hamiltonian_full": maximum_record(hamiltonian, fields["x"], fields["r"]),
                "hamiltonian_interior_maximum": finite_max(interior),
                "momentum_maximum": 0.0,
                "momentum_reason": "K_ij=Pi_Phi=Pi_chi=0 in the common represented state",
            })
        full_values = [item["hamiltonian_full"]["maximum_absolute"] for item in constraint_levels]
        interior_values = [item["hamiltonian_interior_maximum"] for item in constraint_levels]
        phase2_gates = {
            "full_hamiltonian_finest": full_values[-1] <= GATES["hamiltonian_full_finest"],
            "interior_hamiltonian_finest": interior_values[-1] <= GATES["hamiltonian_interior_finest"],
            "hamiltonian_nonincreasing_middle_to_fine": bool(full_values[-1] <= full_values[-2] and interior_values[-1] <= interior_values[-2]),
            "momentum": True,
        }
        result["phases"]["2_full_constraints"] = {
            "levels": constraint_levels, "gates": phase2_gates,
            "passed": all(phase2_gates.values()),
        }
        if not all(phase2_gates.values()):
            result["first_failed_gate"] = next(name for name, passed in phase2_gates.items() if not passed)
            raise StopIteration

        write_status(output, "PHASE_3", "evaluating both wall junctions and the regular axis", started)
        wall_axis_levels = []
        for nx, nr in ADMISSION_GRIDS:
            fields = cached[(nx, nr)]
            wall = compact_wall_position_residuals(
                fields["q"], fields["x"], fields["r"], background_record(),
                STENCIL, radial_buffer=0,
            )
            axis = axis_residual(fields, derivative_matrix)
            wall_axis_levels.append({
                "grid": [nx, nr], "wall": wall, "axis": axis,
            })
        wall_values = [item["wall"]["maximum"] for item in wall_axis_levels]
        axis_values = [item["axis"]["maximum"] for item in wall_axis_levels]
        phase3_gates = {
            "wall_any": max(wall_values) <= GATES["wall_any"],
            "wall_finest": wall_values[-1] <= GATES["wall_finest"],
            "wall_nonincreasing_middle_to_fine": wall_values[-1] <= wall_values[-2],
            "independent_continuum_wall": endpoint_residual < GATES["terminal_wall"],
            "axis": max(axis_values) <= GATES["axis"],
        }
        result["phases"]["3_walls_axis"] = {
            "levels": wall_axis_levels, "gates": phase3_gates,
            "passed": all(phase3_gates.values()),
        }
        if not all(phase3_gates.values()):
            result["first_failed_gate"] = next(name for name, passed in phase3_gates.items() if not passed)
            raise StopIteration

        write_status(output, "PHASE_4", "evaluating geometric GH source and outer-reference identities", started)
        gauge_levels = []
        rhs_cache: dict[tuple[int, int], Any] = {}
        source_cache: dict[tuple[int, int], Any] = {}
        for nx, nr in ADMISSION_GRIDS:
            fields = cached[(nx, nr)]
            source = StageRegularGaugeSource(
                fields["source"], np.zeros_like(fields["source"]),
                fields["x"], fields["r"], STENCIL,
            )
            rhs = NativeRegularSO3RHS(
                fields["x"], fields["r"], source, M2, background_record(),
                np.zeros((2, nr)), STENCIL,
                live_normal_wall_gauge=False, live_outer_sommerfeld=True,
                boundary_closure_mode="legacy_wall_axis_outer",
            )
            rhs.set_outer_sommerfeld_reference(fields["q"], np.zeros_like(fields["q"]))
            rhs_cache[(nx, nr)] = rhs
            source_cache[(nx, nr)] = source
            gauge = gauge_constraint_summary(
                fields["q"], fields["v"], 0.0, rhs,
                radial_cut=None, gauge_source=source,
            )
            outer_metric = outer_sommerfeld_position_residuals(
                fields["q"], fields["v"], fields["q"], np.zeros_like(fields["q"]),
                0.0, fields["r"], STENCIL,
            )
            _source_time, outer_source = apply_outer_source_sommerfeld(
                fields["source"], np.zeros_like(fields["source"]), fields["source"],
                np.zeros_like(fields["source"]), np.zeros_like(fields["source"]),
                fields["q"], 0.0, fields["r"], STENCIL,
            )
            radial_derivatives = _axisymmetric_derivatives(
                fields["source"][:, :, 1], fields["x"], fields["r"], STENCIL,
            )["r"]
            speed = regular_so3_outward_radial_speed(fields["q"], fields["r"])
            gauge_levels.append({
                "grid": [nx, nr], "gauge_constraint": gauge,
                "source_time_trace_maximum": finite_max(source.source_time_reduced),
                "mixed_time_space_trace_maximum": max(finite_max(source.source_time_z), finite_max(source.source_time_r)),
                "natural_radial_moment_maximum": finite_max(radial_derivatives),
                "outer_metric": outer_metric, "outer_source": outer_source,
                "minimum_outward_speed": float(np.min(speed)),
                "maximum_outward_speed": float(np.max(speed)),
            })
        gauge_abs = [item["gauge_constraint"]["maximum_absolute"] for item in gauge_levels]
        gauge_rel = [item["gauge_constraint"]["maximum_local_relative"] for item in gauge_levels]
        phase4_gates = {
            "gauge_absolute_finest": gauge_abs[-1] <= GATES["gauge"],
            "gauge_relative_finest": gauge_rel[-1] <= GATES["gauge"],
            "gauge_nonincreasing_middle_to_fine": bool(gauge_abs[-1] <= gauge_abs[-2] and gauge_rel[-1] <= gauge_rel[-2]),
            "source_time_trace": max(item["source_time_trace_maximum"] for item in gauge_levels) <= GATES["source_trace"],
            "mixed_source_trace": max(item["mixed_time_space_trace_maximum"] for item in gauge_levels) <= GATES["source_trace"],
            "natural_radial_moment": max(item["natural_radial_moment_maximum"] for item in gauge_levels) <= GATES["source_moment"],
            "outer_metric": max(item["outer_metric"]["maximum_normalized"] for item in gauge_levels) <= GATES["outer"],
            "outer_source": max(item["outer_source"]["maximum_normalized"] for item in gauge_levels) <= GATES["outer"],
            "outward_characteristic": min(item["minimum_outward_speed"] for item in gauge_levels) > 0.0,
        }
        result["phases"]["4_gauge_outer"] = {
            "levels": gauge_levels, "gates": phase4_gates,
            "passed": all(phase4_gates.values()),
        }
        if not all(phase4_gates.values()):
            result["first_failed_gate"] = next(name for name, passed in phase4_gates.items() if not passed)
            raise StopIteration

        write_status(output, "PHASE_5", "evaluating static ADM and full GH equilibrium compatibility", started)
        adm_levels = []
        for nx, nr in ADMISSION_GRIDS[1:]:
            fields = cached[(nx, nr)]
            adm_levels.append({
                "grid": [nx, nr],
                **adm_acceleration_record(fields, anisotropic_metric_acceleration, anisotropic_scalar_acceleration),
            })
        gh_fields = cached[(65, 121)]
        gh_acceleration, gh_diagnostic = rhs_cache[(65, 121)].acceleration(
            0.0, gh_fields["q"], gh_fields["v"],
        )
        gh_record = gh_acceleration_record(gh_acceleration, gh_fields["q"], gh_diagnostic)
        phase5_gates = {
            "adm_acceleration_finest": adm_levels[-1]["maximum_normalized"] <= GATES["adm_acceleration"],
            "adm_acceleration_nonincreasing": adm_levels[-1]["maximum_normalized"] <= adm_levels[-2]["maximum_normalized"],
            "gh_acceleration": gh_record["maximum_normalized"] <= GATES["gh_acceleration"],
            "gh_finite_boundary_closure": gh_record["finite"],
        }
        result["phases"]["5_equilibrium_compatibility"] = {
            "adm_levels": adm_levels, "gh_grid": [65, 121],
            "gh": gh_record, "gates": phase5_gates,
            "passed": all(phase5_gates.values()),
        }
        if not all(phase5_gates.values()):
            result["first_failed_gate"] = next(name for name, passed in phase5_gates.items() if not passed)
            raise StopIteration

        result["admission_passed"] = True
        write_status(output, "EVOLUTION", "running the conditionally authorized four-step unperturbed evolution", started)
        evolution_levels = []
        evolution_pass = True
        evolution_failure = None
        for nx, nr in EVOLUTION_GRIDS:
            fields = represented_fields(nx, nr, sample, root_record["k"], cscale)
            source = StageRegularGaugeSource(
                fields["source"], np.zeros_like(fields["source"]), fields["x"], fields["r"], STENCIL,
            )
            rhs = NativeRegularSO3RHS(
                fields["x"], fields["r"], source, M2, background_record(),
                np.zeros((2, nr)), STENCIL, live_normal_wall_gauge=False,
                live_outer_sommerfeld=True, boundary_closure_mode="legacy_wall_axis_outer",
            )
            rhs.set_outer_sommerfeld_reference(fields["q"], np.zeros_like(fields["q"]))
            q0 = fields["q"].copy()
            q = q0.copy()
            v = np.zeros_like(q)
            zero = np.zeros((nx, nr))
            initial_h = anisotropic_hamiltonian_residual(
                fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"],
                fields["c"], fields["phi"], zero, zero, M2, stencil_width=STENCIL,
            )
            initial_gauge = gauge_constraint_summary(q, v, 0.0, rhs, gauge_source=source)
            initial_wall = compact_wall_position_residuals(q, fields["x"], fields["r"], background_record(), STENCIL, 0)
            records = []
            stage_failure = None
            for step in range(1, STEPS + 1):
                t0 = (step - 1) * DT
                a1, d1 = rhs.acceleration(t0, q, v)
                if not d1["finite"]:
                    stage_failure = f"step_{step}_stage_1_nonfinite"
                    break
                qmid = q + 0.5 * DT * v
                vmid = v + 0.5 * DT * a1
                if not positivity({**fields, "q": qmid, "f": fields["f"]})["passed"]:
                    stage_failure = f"step_{step}_midpoint_signature"
                    break
                a2, d2 = rhs.acceleration(t0 + 0.5 * DT, qmid, vmid)
                if not d2["finite"]:
                    stage_failure = f"step_{step}_stage_2_nonfinite"
                    break
                q = q + DT * vmid
                v = v + DT * a2
                pos = positivity({**fields, "q": q, "f": fields["f"]})
                wall = compact_wall_position_residuals(q, fields["x"], fields["r"], background_record(), STENCIL, 0)
                gauge = gauge_constraint_summary(q, v, step * DT, rhs, gauge_source=source)
                change = max(
                    finite_max(q[:, :, field] - q0[:, :, field]) / max(1.0, finite_max(q0[:, :, field]))
                    for field in range(9)
                )
                record = {
                    "step": step, "time": step * DT, "positivity": pos,
                    "wall_maximum": wall["maximum"], "gauge_constraint": gauge,
                    "component_normalized_state_change": change,
                    "stage_1_acceleration": gh_acceleration_record(a1, q, d1),
                    "stage_2_acceleration": gh_acceleration_record(a2, qmid, d2),
                }
                records.append(record)
                if not pos["passed"]:
                    stage_failure = f"step_{step}_accepted_signature"
                    break
            if stage_failure is None:
                final_h = dynamic_hamiltonian(
                    q, v, fields["x"], fields["r"], reduced_state_jets,
                    regular_so3_perturbation_jets, metric_geometry_from_jets,
                )
                final_h_max = finite_max(final_h)
                final = records[-1]
                local_gates = {
                    "hamiltonian": final_h_max <= max(4.0 * finite_max(initial_h), GATES["evolution_hamiltonian_floor"]),
                    "gauge": final["gauge_constraint"]["maximum_absolute"] <= max(4.0 * initial_gauge["maximum_absolute"], GATES["evolution_gauge_floor"]),
                    "wall": final["wall_maximum"] <= max(4.0 * initial_wall["maximum"], GATES["evolution_wall_floor"]),
                    "state_change": final["component_normalized_state_change"] <= GATES["evolution_state_change"],
                    "finite_signature": all(item["positivity"]["passed"] for item in records),
                }
                passed = all(local_gates.values())
            else:
                final_h_max = None
                local_gates = {"stage_completion": False}
                passed = False
            evolution_levels.append({
                "grid": [nx, nr], "dt": DT, "steps": STEPS,
                "initial_hamiltonian_maximum": finite_max(initial_h),
                "initial_gauge": initial_gauge,
                "initial_wall_maximum": initial_wall["maximum"],
                "records": records,
                "final_dynamic_hamiltonian_maximum": final_h_max,
                "stage_failure": stage_failure,
                "gates": local_gates, "passed": passed,
            })
            if not passed and evolution_failure is None:
                evolution_failure = stage_failure or next(name for name, ok in local_gates.items() if not ok)
            evolution_pass &= passed
        result["phases"]["6_short_unperturbed_evolution"] = {
            "levels": evolution_levels,
            "passed": evolution_pass,
            "first_failure": evolution_failure,
        }
        if evolution_pass:
            result["classification"] = "D1_CAUCHY_BACKGROUND_ADMITTED__SHORT_UNPERTURBED_PRESERVATION_PASS"
        else:
            result["classification"] = "D1_CAUCHY_BACKGROUND_ADMITTED__SHORT_EVOLUTION_INCOMPATIBILITY"
            result["first_failed_gate"] = evolution_failure

    except StopIteration:
        result["admission_passed"] = False
        result["classification"] = "D1_CAUCHY_BACKGROUND_NOT_ADMITTED__" + str(result["first_failed_gate"]).upper()
    except Exception as error:
        result["status"] = "INCOMPLETE"
        result["classification"] = "D1_CAUCHY_BACKGROUND_TECHNICAL_INCOMPLETE"
        result["error"] = repr(error)
    finally:
        if "p_evidence" in locals():
            evidence: dict[str, Any] = {
                "x": x_evidence,
                "A": p_evidence["A"], "H": p_evidence["H"],
                "phi": p_evidence["phi"], "U": p_evidence["U"],
                "s": p_evidence["s"], "first_integral": first_integral,
                "root_a": np.asarray(root_record["a"]),
                "k": np.asarray(root_record["k"]),
                "D": np.asarray(root_record["D"]),
                "L": np.asarray(length), "cscale": np.asarray(cscale),
            }
            if "finest_fields" in locals():
                evidence.update({
                    "r": finest_fields["r"], "q": finest_fields["q"],
                    "source": finest_fields["source"], "f": finest_fields["f"],
                })
            np.savez_compressed(output / "EVIDENCE.npz", **evidence)
        if result["status"] == "RUNNING":
            result["status"] = "COMPLETE"
        result["completed_utc"] = utc()
        result["wall_seconds"] = time.monotonic() - wall_start
        atomic_json(output / "RESULT.json", result)
        atomic_json(output / "TERMINAL.json", {
            "schema": "lin-d1-cauchy-background-admission-terminal-v1",
            "status": result["status"],
            "classification": result["classification"],
            "first_failed_gate": result.get("first_failed_gate"),
            "result_sha256": sha256(output / "RESULT.json"),
            "evidence_sha256": sha256(output / "EVIDENCE.npz") if (output / "EVIDENCE.npz").exists() else None,
            "completed_utc": result["completed_utc"],
        })
        write_status(output, "TERMINAL", str(result["classification"]), started)
    print(json.dumps({
        "status": result["status"],
        "classification": result["classification"],
        "first_failed_gate": result.get("first_failed_gate"),
        "wall_seconds": result.get("wall_seconds"),
    }, indent=2))


if __name__ == "__main__":
    main()
