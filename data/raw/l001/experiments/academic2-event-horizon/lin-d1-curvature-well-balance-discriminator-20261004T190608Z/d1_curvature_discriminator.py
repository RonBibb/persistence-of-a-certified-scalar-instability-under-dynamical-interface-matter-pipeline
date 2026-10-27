#!/usr/bin/env python3
"""Two-producer D1 curvature representation discriminator."""

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
from typing import Any

import numpy as np


A_GRIDS = ((65, 121), (97, 181), (129, 241))
B_NX = (257, 513, 1025, 1537, 2049)
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


def status(output: Path, phase: str, detail: str, started: str) -> None:
    atomic_json(output / "STATUS.json", {
        "schema": "lin-d1-curvature-discriminator-status-v1",
        "started_utc": started, "updated_utc": utc(), "phase": phase,
        "detail": detail, "pid": os.getpid(),
    })


def verify_bindings(root: Path, here: Path) -> list[dict[str, str]]:
    bindings = json.loads((here / "BINDINGS.json").read_text(encoding="utf-8"))
    verified = []
    for entry in bindings["parents"] + bindings["production_sources"]:
        path = root / entry["path"]
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise RuntimeError(f"binding changed: {entry['path']} {actual}")
        verified.append({"role": entry.get("role", "production_source"), "path": str(path), "sha256": actual})
    return verified


def observed_order(coarse: float, fine: float, coarse_n: int, fine_n: int) -> float | None:
    if coarse <= 0.0 or fine <= 0.0 or coarse == fine:
        return None
    return float(math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1)))


def maximum(value: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(value, dtype=float))))


def exact_geometry(fields: dict[str, Any], root_record: dict[str, Any]) -> dict[str, np.ndarray]:
    profile = fields["profile"]
    w = profile["w"][:, None]
    h = profile["H"][:, None]
    u = profile["U"][:, None]
    k = float(root_record["k"])
    hs = -u * u / 3.0 - k / (w * w)
    compact_contribution = -3.0 * (hs + h * h)
    brane_contribution = 2.0 * k / (w * w) - hs - 3.0 * h * h
    shape = fields["psi"].shape
    compact_contribution = np.broadcast_to(compact_contribution, shape)
    brane_contribution = np.broadcast_to(brane_contribution, shape)
    metric_zz = fields["q"][:, :, 6]
    metric_radial = fields["q"][:, :, 3] + fields["r"][None, :] ** 2 * fields["q"][:, :, 4]
    metric_transverse = fields["q"][:, :, 3]
    return {
        "compact_contribution": compact_contribution,
        "radial_contribution": brane_contribution,
        "transverse_contribution": brane_contribution,
        "ricci_zz": compact_contribution * metric_zz,
        "ricci_radial": brane_contribution * metric_radial,
        "ricci_transverse": brane_contribution * metric_transverse,
        "ricci_zr": np.zeros(shape),
        "scalar_curvature": compact_contribution + 3.0 * brane_contribution,
    }


def geometry_measurement(fields: dict[str, Any], root_record: dict[str, Any],
                         axisymmetric_diagonal_geometry, derivatives,
                         corrected: bool) -> tuple[dict[str, Any], np.ndarray, dict[str, np.ndarray]]:
    prod = axisymmetric_diagonal_geometry(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"], fields["c"], STENCIL,
    )
    exact = exact_geometry(fields, root_record)
    phi_derivatives = derivatives(fields["phi"], fields["x"], fields["r"], STENCIL)
    gradient = (
        phi_derivatives["z"] ** 2 / prod["metric_zz"]
        + phi_derivatives["r"] ** 2 / prod["metric_radial"]
    )
    if corrected:
        ricci = {
            "zz": prod["ricci_zz"] - prod["ricci_zz"] + exact["ricci_zz"],
            "radial": prod["ricci_radial"] - prod["ricci_radial"] + exact["ricci_radial"],
            "transverse": prod["ricci_transverse"] - prod["ricci_transverse"] + exact["ricci_transverse"],
            "zr": prod["ricci_zr"] - prod["ricci_zr"] + exact["ricci_zr"],
        }
        scalar = (
            ricci["zz"] / prod["metric_zz"]
            + ricci["radial"] / prod["metric_radial"]
            + 2.0 * ricci["transverse"] / prod["metric_transverse"]
        )
    else:
        ricci = {
            "zz": prod["ricci_zz"], "radial": prod["ricci_radial"],
            "transverse": prod["ricci_transverse"], "zr": prod["ricci_zr"],
        }
        scalar = prod["scalar_curvature"]
    hamiltonian = scalar + 12.0 - gradient - 0.41 * fields["phi"] ** 2
    component_errors = {
        "compact": maximum(ricci["zz"] / prod["metric_zz"] - exact["compact_contribution"]),
        "radial": maximum(ricci["radial"] / prod["metric_radial"] - exact["radial_contribution"]),
        "transverse_each": maximum(ricci["transverse"] / prod["metric_transverse"] - exact["transverse_contribution"]),
        "mixed": maximum(ricci["zr"]),
    }
    record = {
        "grid": [len(fields["x"]), len(fields["r"])],
        "hamiltonian_full": maximum(hamiltonian),
        "hamiltonian_interior": maximum(hamiltonian[3:-3, 3:-3]),
        "lower_wall_first_positive_radius": float(hamiltonian[0, 1]),
        "componentwise_ricci_errors": component_errors,
        "scalar_gradient_error": maximum(gradient - np.broadcast_to(fields["profile"]["U"][:, None] ** 2, gradient.shape)),
    }
    return record, hamiltonian, {**prod, "corrected_ricci": ricci, "exact": exact}


def corrected_adm_record(fields: dict[str, Any], root_record: dict[str, Any],
                         axisymmetric_diagonal_geometry, anisotropic_metric_acceleration,
                         anisotropic_scalar_acceleration) -> dict[str, Any]:
    zeros = np.zeros_like(fields["psi"])
    prod_geometry = axisymmetric_diagonal_geometry(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"], fields["c"], STENCIL,
    )
    exact = exact_geometry(fields, root_record)
    raw = anisotropic_metric_acceleration(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"], fields["c"],
        fields["phi"], zeros, zeros, 0.41, stencil_width=STENCIL, lapse=fields["alpha"],
    )
    scalar = anisotropic_scalar_acceleration(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"], fields["c"],
        fields["phi"], 0.41, lapse=fields["alpha"], stencil_width=STENCIL,
    )
    alpha2 = fields["alpha"] ** 2
    corrected = {
        "zz": raw["zz"] + 2.0 * alpha2 * (prod_geometry["ricci_zz"] - exact["ricci_zz"]),
        "radial": raw["radial"] + 2.0 * alpha2 * (prod_geometry["ricci_radial"] - exact["ricci_radial"]),
        "transverse": raw["transverse"] + 2.0 * alpha2 * (prod_geometry["ricci_transverse"] - exact["ricci_transverse"]),
        "zr": raw["zr"] + 2.0 * alpha2 * (prod_geometry["ricci_zr"] - exact["ricci_zr"]),
    }
    scales = {
        "zz": max(1.0, maximum(fields["q"][:, :, 6])),
        "radial": max(1.0, maximum(fields["q"][:, :, 3] + fields["r"][None, :] ** 2 * fields["q"][:, :, 4])),
        "transverse": max(1.0, maximum(fields["q"][:, :, 3])),
        "zr": 1.0, "phi": max(1.0, maximum(fields["phi"])),
    }
    by = {name: maximum(corrected[name]) / scales[name] for name in ("zz", "radial", "transverse", "zr")}
    by["phi"] = maximum(scalar) / scales["phi"]
    return {"by_component": by, "maximum_normalized": max(by.values())}


def perturbation_control(fields: dict[str, Any], root_record: dict[str, Any],
                         axisymmetric_diagonal_geometry) -> dict[str, Any]:
    x = fields["x"][:, None]
    r = fields["r"][None, :]
    shape = np.sin(math.pi * (x - 1.0) / (math.e - 1.0)) * np.exp(-(r / 6.0) ** 2)
    candidate_psi = fields["psi"] * (1.0 + 1e-6 * shape)
    background = axisymmetric_diagonal_geometry(
        fields["x"], fields["r"], fields["psi"], fields["a"], fields["b"], fields["c"], STENCIL,
    )
    candidate = axisymmetric_diagonal_geometry(
        fields["x"], fields["r"], candidate_psi, fields["a"], fields["b"], fields["c"], STENCIL,
    )
    exact = exact_geometry(fields, root_record)
    corrected_candidate = candidate["scalar_curvature"] - background["scalar_curvature"] + exact["scalar_curvature"]
    response = corrected_candidate - exact["scalar_curvature"]
    return {
        "amplitude": 1e-6,
        "maximum_absolute_response": maximum(response),
        "finite": bool(np.all(np.isfinite(response))),
        "nonzero": bool(maximum(response) > 1e-12),
    }


def arm_orders(levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for left, right in zip(levels[:-1], levels[1:]):
        records.append({
            "from_Nx": left["grid"][0], "to_Nx": right["grid"][0],
            "full_order": observed_order(left["hamiltonian_full"], right["hamiltonian_full"], left["grid"][0], right["grid"][0]),
            "interior_order": observed_order(left["hamiltonian_interior"], right["hamiltonian_interior"], left["grid"][0], right["grid"][0]),
        })
    return records


def complete_admission(label: str, fields_by_grid: list[dict[str, Any]], prior, root_record,
                       production: dict[str, Any], output: Path, started: str) -> dict[str, Any]:
    status(output, f"{label}_WALL_AXIS", "testing unchanged wall and axis rows", started)
    wall_axis = []
    for fields in fields_by_grid:
        wall = production["compact_wall_position_residuals"](
            fields["q"], fields["x"], fields["r"], prior.background_record(), STENCIL, 0,
        )
        axis = prior.axis_residual(fields, production["derivative_matrix"])
        wall_axis.append({"grid": [len(fields["x"]), len(fields["r"])], "wall": wall, "axis": axis})
    wall_values = [item["wall"]["maximum"] for item in wall_axis]
    axis_values = [item["axis"]["maximum"] for item in wall_axis]
    wall_gates = {
        "wall_candidate": wall_values[-1] <= GATES["wall"],
        "wall_any": max(wall_values) <= GATES["wall_any"],
        "wall_nonincreasing": len(wall_values) < 2 or wall_values[-1] <= wall_values[-2],
        "axis": max(axis_values) <= GATES["axis"],
    }
    record: dict[str, Any] = {"wall_axis": {"levels": wall_axis, "gates": wall_gates, "passed": all(wall_gates.values())}}
    if not all(wall_gates.values()):
        record.update({"passed": False, "first_failed_gate": next(k for k, v in wall_gates.items() if not v)})
        return record

    status(output, f"{label}_SOURCE", "testing unchanged source, gauge, moment, and outer rows", started)
    gauge_levels = []
    rhs_by_grid = {}
    for fields in fields_by_grid[-2:]:
        nx, nr = len(fields["x"]), len(fields["r"])
        source = production["StageRegularGaugeSource"](
            fields["source"], np.zeros_like(fields["source"]), fields["x"], fields["r"], STENCIL,
        )
        rhs = production["NativeRegularSO3RHS"](
            fields["x"], fields["r"], source, 0.41, prior.background_record(), np.zeros((2, nr)), STENCIL,
            live_normal_wall_gauge=False, live_outer_sommerfeld=True,
            boundary_closure_mode="legacy_wall_axis_outer",
        )
        rhs.set_outer_sommerfeld_reference(fields["q"], np.zeros_like(fields["q"]))
        rhs_by_grid[(nx, nr)] = (rhs, source)
        gauge = production["gauge_constraint_summary"](fields["q"], fields["v"], 0.0, rhs, gauge_source=source)
        outer_metric = production["outer_sommerfeld_position_residuals"](
            fields["q"], fields["v"], fields["q"], np.zeros_like(fields["q"]), 0.0, fields["r"], STENCIL,
        )
        _, outer_source = production["apply_outer_source_sommerfeld"](
            fields["source"], np.zeros_like(fields["source"]), fields["source"],
            np.zeros_like(fields["source"]), np.zeros_like(fields["source"]),
            fields["q"], 0.0, fields["r"], STENCIL,
        )
        radial_moment = maximum(production["derivatives"](
            fields["source"][:, :, 1], fields["x"], fields["r"], STENCIL,
        )["r"])
        speed = production["regular_so3_outward_radial_speed"](fields["q"], fields["r"])
        gauge_levels.append({
            "grid": [nx, nr], "gauge": gauge,
            "source_time": maximum(source.source_time_reduced),
            "source_mixed_time_space": max(maximum(source.source_time_z), maximum(source.source_time_r)),
            "radial_moment": radial_moment, "outer_metric": outer_metric,
            "outer_source": outer_source, "minimum_outward_speed": float(np.min(speed)),
        })
    abs_values = [item["gauge"]["maximum_absolute"] for item in gauge_levels]
    rel_values = [item["gauge"]["maximum_local_relative"] for item in gauge_levels]
    source_gates = {
        "gauge_absolute": abs_values[-1] <= GATES["gauge"],
        "gauge_relative": rel_values[-1] <= GATES["gauge"],
        "gauge_nonincreasing": len(abs_values) < 2 or (abs_values[-1] <= abs_values[-2] and rel_values[-1] <= rel_values[-2]),
        "source_trace": max(item["source_time"] for item in gauge_levels) <= GATES["source"],
        "source_mixed_trace": max(item["source_mixed_time_space"] for item in gauge_levels) <= GATES["source"],
        "radial_moment": max(item["radial_moment"] for item in gauge_levels) <= GATES["source"],
        "outer_metric": max(item["outer_metric"]["maximum_normalized"] for item in gauge_levels) <= GATES["outer"],
        "outer_source": max(item["outer_source"]["maximum_normalized"] for item in gauge_levels) <= GATES["outer"],
        "outgoing": min(item["minimum_outward_speed"] for item in gauge_levels) > 0.0,
    }
    record["source_outer"] = {"levels": gauge_levels, "gates": source_gates, "passed": all(source_gates.values())}
    if not all(source_gates.values()):
        record.update({"passed": False, "first_failed_gate": next(k for k, v in source_gates.items() if not v)})
        return record

    status(output, f"{label}_EQUILIBRIUM", "testing ADM then raw GH equilibrium", started)
    adm_levels = []
    for fields in fields_by_grid[-2:]:
        if label == "A":
            adm = corrected_adm_record(
                fields, root_record, production["axisymmetric_diagonal_geometry"],
                production["anisotropic_metric_acceleration"], production["anisotropic_scalar_acceleration"],
            )
        else:
            adm = prior.adm_acceleration_record(
                fields, production["anisotropic_metric_acceleration"], production["anisotropic_scalar_acceleration"],
            )
        adm_levels.append({"grid": [len(fields["x"]), len(fields["r"])], **adm})
    adm_gates = {
        "adm_acceleration": adm_levels[-1]["maximum_normalized"] <= GATES["adm_acceleration"],
        "adm_nonincreasing": len(adm_levels) < 2 or adm_levels[-1]["maximum_normalized"] <= adm_levels[-2]["maximum_normalized"],
    }
    record["adm_equilibrium"] = {"levels": adm_levels, "gates": adm_gates, "passed": all(adm_gates.values())}
    if not all(adm_gates.values()):
        record.update({"passed": False, "first_failed_gate": next(k for k, v in adm_gates.items() if not v)})
        return record

    gh_fields = fields_by_grid[0] if label == "A" else fields_by_grid[-1]
    key = (len(gh_fields["x"]), len(gh_fields["r"]))
    if key not in rhs_by_grid:
        source = production["StageRegularGaugeSource"](
            gh_fields["source"], np.zeros_like(gh_fields["source"]), gh_fields["x"], gh_fields["r"], STENCIL,
        )
        rhs = production["NativeRegularSO3RHS"](
            gh_fields["x"], gh_fields["r"], source, 0.41, prior.background_record(), np.zeros((2, key[1])), STENCIL,
            live_normal_wall_gauge=False, live_outer_sommerfeld=True,
            boundary_closure_mode="legacy_wall_axis_outer",
        )
        rhs.set_outer_sommerfeld_reference(gh_fields["q"], np.zeros_like(gh_fields["q"]))
    else:
        rhs, source = rhs_by_grid[key]
    acceleration, diagnostic = rhs.acceleration(0.0, gh_fields["q"], gh_fields["v"])
    gh = prior.gh_acceleration_record(acceleration, gh_fields["q"], diagnostic)
    gh_gate = bool(gh["finite"] and gh["maximum_normalized"] <= GATES["gh_acceleration"])
    record["raw_gh_equilibrium"] = {"grid": list(key), "record": gh, "passed": gh_gate}
    record["passed"] = gh_gate
    record["first_failed_gate"] = None if gh_gate else "raw_gh_acceleration"
    record["evolution_inputs"] = {
        "fields": fields_by_grid[-2:] if label == "B" else fields_by_grid[-2:],
        "rhs": rhs_by_grid,
    }
    return record


def run_evolution(label: str, fields_levels: list[dict[str, Any]], prior,
                  production: dict[str, Any], root_record: dict[str, Any],
                  output: Path, started: str) -> dict[str, Any]:
    levels = []
    all_pass = True
    for fields in fields_levels:
        nx, nr = len(fields["x"]), len(fields["r"])
        status(output, f"{label}_EVOLUTION", f"grid {nx}x{nr}", started)
        source = production["StageRegularGaugeSource"](
            fields["source"], np.zeros_like(fields["source"]), fields["x"], fields["r"], STENCIL,
        )
        rhs = production["NativeRegularSO3RHS"](
            fields["x"], fields["r"], source, 0.41, prior.background_record(), np.zeros((2, nr)), STENCIL,
            live_normal_wall_gauge=False, live_outer_sommerfeld=True,
            boundary_closure_mode="legacy_wall_axis_outer",
        )
        rhs.set_outer_sommerfeld_reference(fields["q"], np.zeros_like(fields["q"]))
        q0 = fields["q"].copy(); q = q0.copy(); v = np.zeros_like(q)
        initial_raw = prior.dynamic_hamiltonian(
            q, v, fields["x"], fields["r"], production["reduced_state_jets"],
            production["regular_so3_perturbation_jets"], production["metric_geometry_from_jets"],
        )
        records = []
        failed = None
        for step in range(1, 5):
            t0 = (step - 1) * 0.000125
            a1, d1 = rhs.acceleration(t0, q, v)
            qmid = q + 0.5 * 0.000125 * v
            vmid = v + 0.5 * 0.000125 * a1
            a2, d2 = rhs.acceleration(t0 + 0.5 * 0.000125, qmid, vmid)
            if not d1["finite"] or not d2["finite"]:
                failed = f"step_{step}_nonfinite"
                break
            q = q + 0.000125 * vmid
            v = v + 0.000125 * a2
            checkpoint = output / f"EVOLUTION_{label}_{nx}x{nr}_STEP_{step}.npz"
            temporary = checkpoint.with_suffix(".npz.tmp")
            with temporary.open("wb") as stream:
                np.savez_compressed(stream, q=q, v=v, step=np.asarray(step), dt=np.asarray(0.000125))
            os.replace(temporary, checkpoint)
            pos = prior.positivity({**fields, "q": q, "f": fields["f"]})
            wall = production["compact_wall_position_residuals"](
                q, fields["x"], fields["r"], prior.background_record(), STENCIL, 0,
            )
            gauge = production["gauge_constraint_summary"](q, v, step * 0.000125, rhs, gauge_source=source)
            change = max(
                maximum(q[:, :, field] - q0[:, :, field]) / max(1.0, maximum(q0[:, :, field]))
                for field in range(9)
            )
            records.append({"step": step, "positivity": pos, "wall": wall["maximum"], "gauge": gauge, "state_change": change})
            if not pos["passed"]:
                failed = f"step_{step}_signature"
                break
        if failed is None:
            final_raw = prior.dynamic_hamiltonian(
                q, v, fields["x"], fields["r"], production["reduced_state_jets"],
                production["regular_so3_perturbation_jets"], production["metric_geometry_from_jets"],
            )
            if label == "A":
                final_h = final_raw - initial_raw
                initial_h = np.zeros_like(initial_raw)
            else:
                final_h = final_raw
                initial_h = initial_raw
            gates = {
                "hamiltonian": maximum(final_h) <= max(4.0 * maximum(initial_h), 5e-6),
                "gauge": records[-1]["gauge"]["maximum_absolute"] <= 2e-4,
                "wall": records[-1]["wall"] <= 2e-5,
                "state_change": records[-1]["state_change"] <= 5e-6,
            }
            passed = all(gates.values())
        else:
            final_h = None; gates = {"stage_completion": False}; passed = False
        levels.append({
            "grid": [nx, nr], "records": records, "stage_failure": failed,
            "initial_hamiltonian": maximum(initial_raw),
            "final_hamiltonian": None if final_h is None else maximum(final_h),
            "gates": gates, "passed": passed,
        })
        all_pass &= passed
    return {"levels": levels, "passed": all_pass}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    started = utc(); clock = time.monotonic()
    result: dict[str, Any] = {
        "schema": "lin-d1-curvature-well-balance-discriminator-result-v1",
        "status": "RUNNING", "started_utc": started,
        "contract_sha256": sha256(here / "CONTRACT.md"),
        "bindings_sha256": sha256(here / "BINDINGS.json"),
        "gates": GATES, "classification": None,
        "claim_boundary": [
            "This is a discrete-representation discriminator for one certified D1 background.",
            "A continuum theorem, stability, P16 join, collapse, parent-child, or causal-horizon claim does not follow.",
        ],
    }
    try:
        status(output, "AUTHENTICATION", "checking frozen parents and production sources", started)
        result["bindings_verified"] = verify_bindings(root, here)
        prior_dir = root / "branches/02-event-horizon/lin-d1-cauchy-background-admission-20261004T172121Z"
        source_root = root / "branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src"
        sys.path.insert(0, str(prior_dir)); sys.path.insert(0, str(source_root))
        import d1_background_admission as prior
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
        evidence_x = np.linspace(1.0, math.e, 129)
        evidence_p = sample(evidence_x)
        analytic_h = -12.0 * (
            evidence_p["H"] ** 2 - 1.0 - evidence_p["U"] ** 2 / 12.0
            + 0.41 * evidence_p["phi"] ** 2 / 12.0
            - root_record["k"] * np.exp(-2.0 * evidence_p["A"])
        )
        result["independent_analytic_hamiltonian_maximum"] = maximum(analytic_h)
        result["representative_root"] = {
            "a": root_record["a"], "D": root_record["D"], "L": length,
            "k": root_record["k"], "upper_scalar_residual": root_record["upper_scalar_residual"],
            "upper_israel_residual": root_record["upper_israel_residual"],
        }

        status(output, "PRODUCER_A", "evaluating analytic D1 curvature well-balance", started)
        a_levels = []; a_fields = []
        for nx, nr in A_GRIDS:
            fields = prior.represented_fields(nx, nr, sample, root_record["k"], cscale)
            a_fields.append(fields)
            measurement, _h, _geometry = geometry_measurement(
                fields, root_record, axisymmetric_diagonal_geometry, _axisymmetric_derivatives, True,
            )
            a_levels.append(measurement)
            status(output, "PRODUCER_A", f"completed {nx}x{nr}", started)
        a_orders = arm_orders(a_levels)
        a_control = perturbation_control(a_fields[-1], root_record, axisymmetric_diagonal_geometry)
        a_hamiltonian_gates = {
            "full": a_levels[-1]["hamiltonian_full"] <= GATES["hamiltonian_full"],
            "interior": a_levels[-1]["hamiltonian_interior"] <= GATES["hamiltonian_interior"],
            "nonincreasing": bool(a_levels[-1]["hamiltonian_full"] <= a_levels[-2]["hamiltonian_full"] and a_levels[-1]["hamiltonian_interior"] <= a_levels[-2]["hamiltonian_interior"]),
            "perturbation_active": bool(a_control["finite"] and a_control["nonzero"]),
        }
        result["producer_A"] = {
            "levels": a_levels, "orders": a_orders,
            "perturbation_control": a_control,
            "hamiltonian_gates": a_hamiltonian_gates,
            "hamiltonian_passed": all(a_hamiltonian_gates.values()),
        }

        status(output, "PRODUCER_B", "evaluating unchanged high-Nx production ladder", started)
        b_levels = []
        for nx in B_NX:
            fields = prior.represented_fields(nx, B_NR, sample, root_record["k"], cscale)
            measurement, _h, _geometry = geometry_measurement(
                fields, root_record, axisymmetric_diagonal_geometry, _axisymmetric_derivatives, False,
            )
            b_levels.append(measurement)
            status(output, "PRODUCER_B", f"completed {nx}x{B_NR}", started)
        b_orders = arm_orders(b_levels)
        passing_indices = [
            index for index, item in enumerate(b_levels)
            if item["hamiltonian_full"] <= GATES["hamiltonian_full"]
            and item["hamiltonian_interior"] <= GATES["hamiltonian_interior"]
        ]
        consecutive_pass = len(passing_indices) >= 2 and passing_indices[-2:] == [len(b_levels)-2, len(b_levels)-1]
        last_orders = b_orders[-1]
        b_hamiltonian_gates = {
            "full": b_levels[-1]["hamiltonian_full"] <= GATES["hamiltonian_full"],
            "interior": b_levels[-1]["hamiltonian_interior"] <= GATES["hamiltonian_interior"],
            "monotone_full": all(right["hamiltonian_full"] < left["hamiltonian_full"] for left, right in zip(b_levels[:-1], b_levels[1:])),
            "monotone_interior": all(right["hamiltonian_interior"] < left["hamiltonian_interior"] for left, right in zip(b_levels[:-1], b_levels[1:])),
            "last_full_order": last_orders["full_order"] is not None and 2.0 <= last_orders["full_order"] <= 6.0,
            "last_interior_order": last_orders["interior_order"] is not None and 2.0 <= last_orders["interior_order"] <= 6.0,
            "two_consecutive_absolute_passes": consecutive_pass,
        }
        result["producer_B"] = {
            "levels": b_levels, "orders": b_orders,
            "passing_indices": passing_indices,
            "hamiltonian_gates": b_hamiltonian_gates,
            "hamiltonian_passed": all(b_hamiltonian_gates.values()),
        }

        admitted = []
        if result["producer_A"]["hamiltonian_passed"]:
            a_admission = complete_admission("A", a_fields, prior, root_record, production, output, started)
            result["producer_A"]["complete_admission"] = {
                key: value for key, value in a_admission.items() if key != "evolution_inputs"
            }
            if a_admission["passed"]:
                admitted.append(("A", a_fields[-2:]))
        if result["producer_B"]["hamiltonian_passed"]:
            b_fields = [
                prior.represented_fields(B_NX[-2], B_NR, sample, root_record["k"], cscale),
                prior.represented_fields(B_NX[-1], B_NR, sample, root_record["k"], cscale),
            ]
            b_admission = complete_admission("B", b_fields, prior, root_record, production, output, started)
            result["producer_B"]["complete_admission"] = {
                key: value for key, value in b_admission.items() if key != "evolution_inputs"
            }
            if b_admission["passed"]:
                admitted.append(("B", b_fields))

        if admitted:
            evolution_results = {}
            for label, fields_levels in admitted:
                evolution_results[label] = run_evolution(
                    label, fields_levels, prior, production, root_record, output, started,
                )
            result["short_evolution"] = evolution_results
            passing_evolution = [label for label, record in evolution_results.items() if record["passed"]]
            if "A" in passing_evolution:
                result["classification"] = "D1_CURVATURE_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS"
            elif "B" in passing_evolution:
                result["classification"] = "D1_DIRECT_REFINEMENT_ADMITS__SHORT_PRESERVATION_PASS"
            else:
                first = admitted[0][0]
                result["classification"] = f"D1_{'CURVATURE_REPRESENTATION' if first == 'A' else 'DIRECT_REFINEMENT'}_IDENTIFIED__FULL_ADMISSION_BLOCKED_SHORT_EVOLUTION"
        else:
            a_complete = result["producer_A"].get("complete_admission", {})
            b_complete = result["producer_B"].get("complete_admission", {})
            if result["producer_A"]["hamiltonian_passed"] and not a_complete.get("passed", False):
                result["classification"] = "D1_CURVATURE_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_" + str(a_complete.get("first_failed_gate", "UNKNOWN")).upper()
            elif result["producer_B"]["hamiltonian_passed"] and not b_complete.get("passed", False):
                result["classification"] = "D1_DIRECT_REFINEMENT_REACHES_HAMILTONIAN_GATE__FULL_ADMISSION_BLOCKED_" + str(b_complete.get("first_failed_gate", "UNKNOWN")).upper()
            else:
                result["classification"] = "NEITHER_D1_CURVATURE_PRODUCER_ADMITS"

        result["status"] = "COMPLETE"
        finest = a_fields[-1]
        np.savez_compressed(
            output / "EVIDENCE.npz", x=finest["x"], r=finest["r"],
            A=finest["profile"]["A"], H=finest["profile"]["H"],
            phi=finest["profile"]["phi"], U=finest["profile"]["U"],
            q=finest["q"], source=finest["source"],
            k=np.asarray(root_record["k"]), cscale=np.asarray(cscale),
            analytic_hamiltonian=analytic_h,
        )
    except Exception as error:
        result["status"] = "INCOMPLETE"
        result["classification"] = "D1_CURVATURE_DISCRIMINATOR_TECHNICAL_INCOMPLETE"
        result["error"] = repr(error)
    result["completed_utc"] = utc(); result["wall_seconds"] = time.monotonic() - clock
    atomic_json(output / "RESULT.json", result)
    terminal = {
        "schema": "lin-d1-curvature-discriminator-terminal-v1",
        "status": result["status"], "classification": result["classification"],
        "result_sha256": sha256(output / "RESULT.json"),
        "evidence_sha256": sha256(output / "EVIDENCE.npz") if (output / "EVIDENCE.npz").exists() else None,
        "completed_utc": result["completed_utc"],
    }
    atomic_json(output / "TERMINAL.json", terminal)
    status(output, "TERMINAL", str(result["classification"]), started)
    print(json.dumps({"status": result["status"], "classification": result["classification"], "wall_seconds": result["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
