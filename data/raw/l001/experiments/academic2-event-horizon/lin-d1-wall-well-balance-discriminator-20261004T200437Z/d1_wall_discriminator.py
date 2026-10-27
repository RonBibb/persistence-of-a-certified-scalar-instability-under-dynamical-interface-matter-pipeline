#!/usr/bin/env python3
"""D1 compact-wall well-balance and direct-refinement discriminator."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np


A_GRIDS = ((65, 121), (97, 181), (129, 241))
B_NX = (129, 193, 257, 385, 513)
B_NR = 241
STENCIL = 7
GATES = {
    "hamiltonian_full": 2e-6,
    "hamiltonian_interior": 5e-7,
    "wall": 2e-6,
    "wall_any": 2e-5,
    "axis": 5e-12,
    "gauge": 5e-5,
    "source": 1e-12,
    "outer": 1e-12,
    "adm_acceleration": 5e-5,
    "gh_acceleration": 1e-4,
}


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True,
                   default=lambda item: item.item() if isinstance(item, np.generic) else str(item)) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_status(output: Path, phase: str, detail: str, started: str) -> None:
    atomic_json(output / "STATUS.json", {
        "schema": "lin-d1-wall-discriminator-status-v1",
        "started_utc": started,
        "updated_utc": utc(),
        "phase": phase,
        "detail": detail,
        "pid": os.getpid(),
    })


def verify_bindings(root: Path, here: Path) -> list[dict[str, str]]:
    bindings = json.loads((here / "BINDINGS.json").read_text(encoding="utf-8"))
    verified = []
    for item in bindings["parents"] + bindings["production_sources"]:
        actual = sha256(root / item["path"])
        if actual != item["sha256"]:
            raise RuntimeError(f"binding changed: {item['path']} {actual}")
        verified.append({"path": item["path"], "sha256": actual, "role": item.get("role", "production_source")})
    return verified


def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wall_coefficients(phi: np.ndarray, background: dict[str, float], upper: bool):
    gamma = float(background["wall_stiffness"])
    target = float(background["v1"] if upper else background["v0"])
    potential = 0.5 * gamma * (phi - target) ** 2
    if upper:
        beta = float(background["beta_b"]) - (potential - float(background["wall_potential_b"])) / 6.0
    else:
        beta = float(background["beta_a"]) + (potential - float(background["wall_potential_a"])) / 6.0
    return target, beta


def wall_row_fields(position: np.ndarray, z: np.ndarray, r: np.ndarray,
                    background: dict[str, float], derivative_matrix,
                    radial_buffer: int = 0) -> dict[str, Any]:
    q = np.asarray(position, dtype=float)
    z = np.asarray(z, dtype=float)
    r = np.asarray(r, dtype=float)
    dz = derivative_matrix(z, 1, STENCIL)
    if hasattr(dz, "toarray"):
        dz = dz.toarray()
    radius2 = r[None, :] ** 2
    fields = {
        "g00": q[:, :, 2],
        "perp": q[:, :, 3],
        "radial": q[:, :, 3] + radius2 * q[:, :, 4],
        "g0r": r[None, :] * q[:, :, 5],
    }
    retained = slice(None, -int(radial_buffer)) if radial_buffer else slice(None)
    walls = []
    for wall, index, upper, sign in (("lower", 0, False, -1.0), ("upper", -1, True, 1.0)):
        normal_scale = np.sqrt(q[index, :, 6])
        target, beta = wall_coefficients(q[index, :, 7], background, upper)
        rows = {}
        scales = {}
        for name, field in fields.items():
            derivative = (dz @ field)[index]
            robin = 2.0 * beta * normal_scale * field[index]
            rows[name] = derivative + robin
            scales[name] = np.maximum(1.0, np.abs(derivative) + np.abs(robin))
        gamma = float(background["wall_stiffness"])
        derivative = (dz @ q[:, :, 7])[index]
        robin = sign * 0.5 * gamma * (q[index, :, 7] - target) * normal_scale
        rows["phi"] = derivative + robin
        scales["phi"] = np.maximum(1.0, np.abs(derivative) + np.abs(robin))
        rows["chi"] = (dz @ q[:, :, 8])[index]
        scales["chi"] = np.ones_like(rows["chi"])
        rows["h_z0_dirichlet"] = q[index, :, 0]
        scales["h_z0_dirichlet"] = np.ones_like(rows["h_z0_dirichlet"])
        rows["h_zr_dirichlet"] = r * q[index, :, 1]
        scales["h_zr_dirichlet"] = np.ones_like(rows["h_zr_dirichlet"])
        walls.append({"wall": wall, "rows": rows, "scales": scales, "retained": retained})
    return {"walls": walls}


def summarize_wall_difference(candidate: np.ndarray, background_position: np.ndarray,
                              z: np.ndarray, r: np.ndarray, background: dict[str, float],
                              derivative_matrix, radial_buffer: int = 0) -> dict[str, Any]:
    candidate_rows = wall_row_fields(candidate, z, r, background, derivative_matrix, radial_buffer)
    baseline_rows = wall_row_fields(background_position, z, r, background, derivative_matrix, radial_buffer)
    records = []
    for candidate_wall, baseline_wall in zip(candidate_rows["walls"], baseline_rows["walls"]):
        retained = candidate_wall["retained"]
        rows = {}
        for name, value in candidate_wall["rows"].items():
            corrected = value - baseline_wall["rows"][name]
            scale = candidate_wall["scales"][name]
            rows[name] = float(np.max(np.abs(corrected[retained]) / scale[retained]))
        records.append({"wall": candidate_wall["wall"], "rows": rows, "maximum": max(rows.values())})
    return {"walls": records, "maximum": max(record["maximum"] for record in records)}


def wall_perturbation_control(fields: dict[str, Any], background: dict[str, float], derivative_matrix) -> dict[str, Any]:
    x = fields["x"][:, None]
    r = fields["r"][None, :]
    shape = np.sin(math.pi * (x - 1.0) / (math.e - 1.0)) * np.exp(-(r / 6.0) ** 2)
    candidate = fields["q"].copy()
    candidate[:, :, 3] *= 1.0 + 1e-6 * shape
    record = summarize_wall_difference(
        candidate, fields["q"], fields["x"], fields["r"], background, derivative_matrix, 0,
    )
    return {
        "amplitude": 1e-6,
        "maximum_absolute_normalized_response": record["maximum"],
        "finite": bool(np.isfinite(record["maximum"])),
        "nonzero": bool(record["maximum"] > 1e-12),
    }


def observed_order(coarse: float, fine: float, coarse_n: int, fine_n: int) -> float | None:
    if coarse <= 0.0 or fine <= 0.0 or coarse == fine:
        return None
    return float(math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1)))


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
    clock = time.monotonic()
    result: dict[str, Any] = {
        "schema": "lin-d1-wall-discriminator-result-v1",
        "status": "RUNNING",
        "classification": None,
        "started_utc": started,
        "contract_sha256": sha256(here / "CONTRACT.md"),
        "bindings_sha256": sha256(here / "BINDINGS.json"),
        "gates": GATES,
        "claim_boundary": [
            "One certified D1 background is tested at finite resolution.",
            "No continuum, stability, P16, collapse, parent-child, or causal-horizon inference follows.",
        ],
    }
    try:
        write_status(output, "AUTHENTICATION", "verifying frozen parent and operator bindings", started)
        result["bindings_verified"] = verify_bindings(root, here)
        prior_path = root / "branches/02-event-horizon/lin-d1-cauchy-background-admission-20261004T172121Z/d1_background_admission.py"
        curvature_path = root / "branches/02-event-horizon/lin-d1-curvature-well-balance-discriminator-20261004T190608Z/d1_curvature_discriminator.py"
        prior = import_file("d1_background_admission_wall_parent", prior_path)
        curvature = import_file("d1_curvature_discriminator_wall_parent", curvature_path)
        source_root = root / "branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src"
        sys.path.insert(0, str(source_root))
        from bhps.adm_corner import _axisymmetric_derivatives
        from bhps.anisotropic_geometry import (
            anisotropic_metric_acceleration, anisotropic_scalar_acceleration,
            axisymmetric_diagonal_geometry,
        )
        from bhps.gw_slice_high_order_solver import derivative_matrix
        from bhps.linearized_gh_einstein_scalar import metric_geometry_from_jets
        from bhps.nonlinear_regular_so3_evolution import (
            NativeRegularSO3RHS, StageRegularGaugeSource,
            apply_outer_source_sommerfeld, compact_wall_position_residuals,
            gauge_constraint_summary, outer_sommerfeld_position_residuals,
            reduced_state_jets, regular_so3_outward_radial_speed,
        )
        from bhps.regular_so3_gh_reduction import regular_so3_perturbation_jets

        production = {
            "derivatives": _axisymmetric_derivatives,
            "axisymmetric_diagonal_geometry": axisymmetric_diagonal_geometry,
            "anisotropic_metric_acceleration": anisotropic_metric_acceleration,
            "anisotropic_scalar_acceleration": anisotropic_scalar_acceleration,
            "derivative_matrix": derivative_matrix,
            "metric_geometry_from_jets": metric_geometry_from_jets,
            "NativeRegularSO3RHS": NativeRegularSO3RHS,
            "StageRegularGaugeSource": StageRegularGaugeSource,
            "apply_outer_source_sommerfeld": apply_outer_source_sommerfeld,
            "compact_wall_position_residuals": compact_wall_position_residuals,
            "gauge_constraint_summary": gauge_constraint_summary,
            "outer_sommerfeld_position_residuals": outer_sommerfeld_position_residuals,
            "reduced_state_jets": reduced_state_jets,
            "regular_so3_outward_radial_speed": regular_so3_outward_radial_speed,
            "regular_so3_perturbation_jets": regular_so3_perturbation_jets,
        }
        root_record = prior.solve_representative_root()
        sample, length, cscale = prior.make_profile(root_record)
        background_record = prior.background_record()
        result["representative_root"] = {
            "a": root_record["a"], "D": root_record["D"], "L": length,
            "k": root_record["k"],
            "maximum_terminal_wall_identity": max(
                abs(root_record["lower_scalar_residual"]), abs(root_record["lower_israel_residual"]),
                abs(root_record["upper_scalar_residual"]), abs(root_record["upper_israel_residual"]),
            ),
        }

        write_status(output, "PRODUCER_A", "evaluating D1 curvature and wall well-balances", started)
        a_fields = []
        a_levels = []
        for nx, nr in A_GRIDS:
            fields = prior.represented_fields(nx, nr, sample, root_record["k"], cscale)
            a_fields.append(fields)
            geometry, _hamiltonian, _ = curvature.geometry_measurement(
                fields, root_record, axisymmetric_diagonal_geometry, _axisymmetric_derivatives, True,
            )
            wall = summarize_wall_difference(
                fields["q"], fields["q"], fields["x"], fields["r"],
                background_record, derivative_matrix, 0,
            )
            a_levels.append({"grid": [nx, nr], "geometry": geometry, "wall": wall})
            write_status(output, "PRODUCER_A", f"completed {nx}x{nr}", started)
        perturbation = wall_perturbation_control(a_fields[-1], background_record, derivative_matrix)
        h_full = [item["geometry"]["hamiltonian_full"] for item in a_levels]
        h_interior = [item["geometry"]["hamiltonian_interior"] for item in a_levels]
        wall_values = [item["wall"]["maximum"] for item in a_levels]
        a_gates = {
            "hamiltonian_full": h_full[-1] <= GATES["hamiltonian_full"],
            "hamiltonian_interior": h_interior[-1] <= GATES["hamiltonian_interior"],
            "hamiltonian_nonincreasing": h_full[-1] <= h_full[-2] and h_interior[-1] <= h_interior[-2],
            "wall_candidate": wall_values[-1] <= GATES["wall"],
            "wall_any": max(wall_values) <= GATES["wall_any"],
            "wall_nonincreasing": wall_values[-1] <= wall_values[-2],
            "generic_response": bool(perturbation["finite"] and perturbation["nonzero"]),
        }
        result["producer_A"] = {
            "levels": a_levels,
            "perturbation_control": perturbation,
            "gates": a_gates,
            "passed": all(a_gates.values()),
        }

        write_status(output, "PRODUCER_B", "evaluating unchanged direct wall-refinement ladder", started)
        b_levels = []
        for nx in B_NX:
            fields = prior.represented_fields(nx, B_NR, sample, root_record["k"], cscale)
            wall = compact_wall_position_residuals(
                fields["q"], fields["x"], fields["r"], background_record, STENCIL, radial_buffer=0,
            )
            b_levels.append({"grid": [nx, B_NR], "wall": wall, "maximum": wall["maximum"]})
            write_status(output, "PRODUCER_B", f"completed {nx}x{B_NR}", started)
        b_orders = [
            {
                "from_Nx": left["grid"][0], "to_Nx": right["grid"][0],
                "order": observed_order(left["maximum"], right["maximum"], left["grid"][0], right["grid"][0]),
            }
            for left, right in zip(b_levels[:-1], b_levels[1:])
        ]
        b_passing = [index for index, item in enumerate(b_levels) if item["maximum"] <= GATES["wall"]]
        b_gates = {
            "candidate": b_levels[-1]["maximum"] <= GATES["wall"],
            "all_levels": max(item["maximum"] for item in b_levels) <= GATES["wall_any"],
            "monotone": all(right["maximum"] < left["maximum"] for left, right in zip(b_levels[:-1], b_levels[1:])),
            "last_order": b_orders[-1]["order"] is not None and 2.0 <= b_orders[-1]["order"] <= 6.0,
            "two_consecutive_candidate_passes": len(b_passing) >= 2 and b_passing[-2:] == [len(b_levels)-2, len(b_levels)-1],
        }
        result["producer_B"] = {
            "levels": b_levels, "orders": b_orders, "passing_indices": b_passing,
            "gates": b_gates, "passed": all(b_gates.values()),
            "scope": "wall-only diagnostic; preceding bulk direct-refinement failure remains controlling",
        }

        if result["producer_A"]["passed"]:
            background_by_grid = {(len(item["x"]), len(item["r"])): item["q"] for item in a_fields}

            def wall_wb(position, z, r, background, stencil_width=7, radial_buffer=7):
                key = (len(z), len(r))
                if key not in background_by_grid:
                    raise RuntimeError(f"no frozen D1 wall background for grid {key}")
                return summarize_wall_difference(
                    position, background_by_grid[key], z, r, background,
                    derivative_matrix, radial_buffer,
                )

            admitted_production = dict(production)
            admitted_production["compact_wall_position_residuals"] = wall_wb
            admission = curvature.complete_admission(
                "A", a_fields, prior, root_record, admitted_production, output, started,
            )
            result["producer_A"]["complete_admission"] = {
                key: value for key, value in admission.items() if key != "evolution_inputs"
            }
            if admission["passed"]:
                evolution = curvature.run_evolution(
                    "A", a_fields[-2:], prior, admitted_production, root_record, output, started,
                )
                result["short_evolution"] = evolution
                result["classification"] = (
                    "D1_WALL_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS"
                    if evolution["passed"] else
                    "D1_WALL_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED"
                )
            else:
                result["classification"] = (
                    "D1_WALL_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_"
                    + str(admission.get("first_failed_gate", "UNKNOWN")).upper()
                )
        else:
            result["classification"] = "D1_WALL_WELL_BALANCE_TECHNICAL_INCOMPLETE"

        result["status"] = "COMPLETE"
        finest = a_fields[-1]
        np.savez_compressed(
            output / "EVIDENCE.npz",
            x=finest["x"], r=finest["r"], q=finest["q"], source=finest["source"],
            A=finest["profile"]["A"], H=finest["profile"]["H"],
            phi=finest["profile"]["phi"], U=finest["profile"]["U"],
            k=np.asarray(root_record["k"]), cscale=np.asarray(cscale),
        )
    except Exception as error:
        result["status"] = "INCOMPLETE"
        result["classification"] = "D1_WALL_WELL_BALANCE_TECHNICAL_INCOMPLETE"
        result["error"] = repr(error)
    result["completed_utc"] = utc()
    result["wall_seconds"] = time.monotonic() - clock
    atomic_json(output / "RESULT.json", result)
    terminal = {
        "schema": "lin-d1-wall-discriminator-terminal-v1",
        "status": result["status"], "classification": result["classification"],
        "result_sha256": sha256(output / "RESULT.json"),
        "evidence_sha256": sha256(output / "EVIDENCE.npz") if (output / "EVIDENCE.npz").exists() else None,
        "completed_utc": result["completed_utc"],
    }
    atomic_json(output / "TERMINAL.json", terminal)
    write_status(output, "TERMINAL", str(result["classification"]), started)
    print(json.dumps({"status": result["status"], "classification": result["classification"], "wall_seconds": result["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
