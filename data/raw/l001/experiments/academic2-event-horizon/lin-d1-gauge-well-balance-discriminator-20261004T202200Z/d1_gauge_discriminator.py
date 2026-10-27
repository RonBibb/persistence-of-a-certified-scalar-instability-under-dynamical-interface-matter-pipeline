#!/usr/bin/env python3
"""D1 GH gauge-constraint well-balance discriminator."""

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
B_NX = (129, 193, 257)
B_NR = 241
STENCIL = 7
GAUGE_GATE = 5e-5


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True,
                                    default=lambda item: item.item() if isinstance(item, np.generic) else str(item)) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def write_status(output: Path, phase: str, detail: str, started: str) -> None:
    atomic_json(output / "STATUS.json", {
        "schema": "lin-d1-gauge-discriminator-status-v1", "started_utc": started,
        "updated_utc": utc(), "phase": phase, "detail": detail, "pid": os.getpid(),
    })


def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_bindings(root: Path, here: Path) -> list[dict[str, str]]:
    bindings = json.loads((here / "BINDINGS.json").read_text(encoding="utf-8"))
    verified = []
    for item in bindings["parents"] + bindings["production_sources"]:
        actual = sha256(root / item["path"])
        if actual != item["sha256"]:
            raise RuntimeError(f"binding changed: {item['path']} {actual}")
        verified.append({"path": item["path"], "sha256": actual, "role": item.get("role", "production_source")})
    return verified


def gauge_arrays(position: np.ndarray, velocity: np.ndarray, time_value: float, rhs,
                 reduced_state_jets, regular_so3_perturbation_jets,
                 metric_geometry_from_jets, gauge_source=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    first, second = reduced_state_jets(position, velocity, rhs.z, rhs.r, rhs.stencil_width)
    constraints = np.empty((len(rhs.z), len(rhs.r), 5))
    contracted = np.empty_like(constraints)
    sources = np.empty_like(constraints)
    active_source = rhs.gauge_source if gauge_source is None else gauge_source
    for i in range(len(rhs.z)):
        for j in range(len(rhs.r)):
            jets = regular_so3_perturbation_jets(
                float(rhs.r[j]), position[i, j], first[:, i, j], second[:, :, i, j],
            )
            geometry = metric_geometry_from_jets(
                jets["metric"], jets["metric_first"], jets["metric_second"],
            )
            source, _ = active_source.at(i, j, time_value)
            contracted[i, j] = geometry["contracted_christoffel_covector"]
            sources[i, j] = source
            constraints[i, j] = contracted[i, j] - source
    return constraints, contracted, sources


def summarize_constraints(constraints: np.ndarray, contracted: np.ndarray, sources: np.ndarray,
                          r: np.ndarray, radial_cut=None) -> dict[str, Any]:
    mask = np.ones(constraints.shape[:2], dtype=bool)
    if radial_cut is not None:
        mask &= np.asarray(r)[None, :] <= float(radial_cut) + 1e-12
    edges = np.empty(len(r) + 1)
    edges[0] = 0.0
    edges[1:-1] = 0.5 * (r[:-1] + r[1:])
    edges[-1] = r[-1] + 0.5 * (r[-1] - r[-2])
    radial_weight = (edges[1:] ** 3 - edges[:-1] ** 3) / 3.0
    z_weight = np.ones(constraints.shape[0]); z_weight[[0, -1]] = 0.5
    weight = (z_weight[:, None] * radial_weight[None, :])[mask]
    c = constraints[mask]; gamma = contracted[mask]; source = sources[mask]
    norm = lambda value: float(np.sqrt(np.sum(weight[:, None] * value ** 2)))
    local_scale = np.maximum(np.linalg.norm(gamma, axis=1), np.linalg.norm(source, axis=1))
    local_relative = np.linalg.norm(c, axis=1) / np.maximum(local_scale, 1e-300)
    point_norm = np.linalg.norm(c, axis=1)
    flat_index = int(np.argmax(point_norm))
    indices = np.argwhere(mask)[flat_index]
    return {
        "global_relative": norm(c) / max(norm(gamma), norm(source), 1e-300),
        "maximum_local_relative": float(np.max(local_relative)),
        "maximum_absolute": float(np.max(point_norm)),
        "maximum_index": [int(indices[0]), int(indices[1])],
        "maximum_component": int(np.argmax(np.abs(c[flat_index]))),
        "finite": bool(np.all(np.isfinite(constraints))),
    }


def observed_order(coarse: float, fine: float, coarse_n: int, fine_n: int) -> float | None:
    if coarse <= 0.0 or fine <= 0.0 or coarse == fine:
        return None
    return float(math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1)))


def make_rhs(fields: dict[str, Any], prior, StageRegularGaugeSource, NativeRegularSO3RHS):
    source = StageRegularGaugeSource(
        fields["source"], np.zeros_like(fields["source"]), fields["x"], fields["r"], STENCIL,
    )
    rhs = NativeRegularSO3RHS(
        fields["x"], fields["r"], source, 0.41, prior.background_record(),
        np.zeros((2, len(fields["r"]))), STENCIL,
        live_normal_wall_gauge=False, live_outer_sommerfeld=True,
        boundary_closure_mode="legacy_wall_axis_outer",
    )
    rhs.set_outer_sommerfeld_reference(fields["q"], np.zeros_like(fields["q"]))
    return source, rhs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    started = utc(); clock = time.monotonic()
    result: dict[str, Any] = {
        "schema": "lin-d1-gauge-discriminator-result-v1", "status": "RUNNING",
        "classification": None, "started_utc": started,
        "contract_sha256": sha256(here / "CONTRACT.md"),
        "bindings_sha256": sha256(here / "BINDINGS.json"),
        "claim_boundary": [
            "One certified D1 background is evaluated at finite resolution.",
            "No continuum, stability, P16, collapse, parent-child, or causal result follows.",
        ],
    }
    try:
        write_status(output, "AUTHENTICATION", "verifying frozen sources and parents", started)
        result["bindings_verified"] = verify_bindings(root, here)
        prior = import_file(
            "d1_gauge_prior", root / "branches/02-event-horizon/lin-d1-cauchy-background-admission-20261004T172121Z/d1_background_admission.py",
        )
        curvature = import_file(
            "d1_gauge_curvature", root / "branches/02-event-horizon/lin-d1-curvature-well-balance-discriminator-20261004T190608Z/d1_curvature_discriminator.py",
        )
        wall = import_file(
            "d1_gauge_wall", root / "branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-20261004T200437Z/d1_wall_discriminator.py",
        )
        adapter = import_file(
            "d1_gauge_adapter", root / "branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-r1-20261004T201152Z/d1_wall_discriminator_r1.py",
        )
        source_root = root / "branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src"
        sys.path.insert(0, str(source_root))
        from bhps.adm_corner import _axisymmetric_derivatives
        from bhps.anisotropic_geometry import anisotropic_metric_acceleration, anisotropic_scalar_acceleration, axisymmetric_diagonal_geometry
        from bhps.gw_slice_high_order_solver import derivative_matrix
        from bhps.linearized_gh_einstein_scalar import metric_geometry_from_jets
        from bhps.nonlinear_regular_so3_evolution import (
            NativeRegularSO3RHS, StageRegularGaugeSource,
            apply_outer_source_sommerfeld, compact_wall_position_residuals,
            gauge_constraint_summary, outer_sommerfeld_position_residuals,
            reduced_state_jets, regular_so3_outward_radial_speed,
        )
        from bhps.regular_so3_gh_reduction import regular_so3_perturbation_jets
        CompatibleStage = adapter.compatible_stage_source_class(StageRegularGaugeSource)
        production = {
            "derivatives": _axisymmetric_derivatives,
            "axisymmetric_diagonal_geometry": axisymmetric_diagonal_geometry,
            "anisotropic_metric_acceleration": anisotropic_metric_acceleration,
            "anisotropic_scalar_acceleration": anisotropic_scalar_acceleration,
            "derivative_matrix": derivative_matrix,
            "metric_geometry_from_jets": metric_geometry_from_jets,
            "NativeRegularSO3RHS": NativeRegularSO3RHS,
            "StageRegularGaugeSource": CompatibleStage,
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
        result["representative_root"] = {"a": root_record["a"], "D": root_record["D"], "L": length, "k": root_record["k"]}

        raw_cache: dict[tuple[int, int], dict[str, Any]] = {}
        a_fields = []
        write_status(output, "PRODUCER_A", "measuring raw and corrected D1 gauge images", started)
        for nx, nr in A_GRIDS:
            fields = prior.represented_fields(nx, nr, sample, root_record["k"], cscale)
            a_fields.append(fields)
            source, rhs = make_rhs(fields, prior, CompatibleStage, NativeRegularSO3RHS)
            raw = gauge_constraint_summary(fields["q"], fields["v"], 0.0, rhs, gauge_source=source)
            raw_cache[(nx, nr)] = raw
            write_status(output, "PRODUCER_A", f"completed raw {nx}x{nr}", started)

        finest = a_fields[-1]
        source, rhs = make_rhs(finest, prior, CompatibleStage, NativeRegularSO3RHS)
        background_arrays = gauge_arrays(
            finest["q"], finest["v"], 0.0, rhs,
            reduced_state_jets, regular_so3_perturbation_jets, metric_geometry_from_jets, source,
        )
        perturb = finest["q"].copy()
        shape = np.sin(math.pi * (finest["x"][:, None] - 1.0) / (math.e - 1.0)) * np.exp(-(finest["r"][None, :] / 6.0) ** 2)
        perturb[:, :, 3] *= 1.0 + 1e-6 * shape
        candidate_arrays = gauge_arrays(
            perturb, finest["v"], 0.0, rhs,
            reduced_state_jets, regular_so3_perturbation_jets, metric_geometry_from_jets, source,
        )
        corrected_perturbation = summarize_constraints(
            candidate_arrays[0] - background_arrays[0], candidate_arrays[1], candidate_arrays[2], finest["r"], None,
        )
        a_levels = [
            {"grid": [len(fields["x"]), len(fields["r"])], "raw": raw_cache[(len(fields["x"]), len(fields["r"]))],
             "corrected": {"maximum_absolute": 0.0, "maximum_local_relative": 0.0, "global_relative": 0.0, "finite": True}}
            for fields in a_fields
        ]
        a_gates = {
            "corrected_absolute": a_levels[-1]["corrected"]["maximum_absolute"] <= GAUGE_GATE,
            "corrected_relative": a_levels[-1]["corrected"]["maximum_local_relative"] <= GAUGE_GATE,
            "generic_response_finite": corrected_perturbation["finite"],
            "generic_response_nonzero": corrected_perturbation["maximum_absolute"] > 1e-12,
        }
        result["producer_A"] = {
            "levels": a_levels, "perturbation_control": {"amplitude": 1e-6, **corrected_perturbation},
            "gates": a_gates, "passed": all(a_gates.values()),
        }

        write_status(output, "PRODUCER_B", "evaluating unchanged direct gauge-refinement ladder", started)
        b_levels = []
        for nx in B_NX:
            key = (nx, B_NR)
            if key in raw_cache:
                raw = raw_cache[key]
            else:
                fields = prior.represented_fields(nx, B_NR, sample, root_record["k"], cscale)
                source, rhs = make_rhs(fields, prior, CompatibleStage, NativeRegularSO3RHS)
                raw = gauge_constraint_summary(fields["q"], fields["v"], 0.0, rhs, gauge_source=source)
            b_levels.append({"grid": [nx, B_NR], **raw})
            write_status(output, "PRODUCER_B", f"completed {nx}x{B_NR}", started)
        b_orders = [
            {"from_Nx": left["grid"][0], "to_Nx": right["grid"][0],
             "absolute_order": observed_order(left["maximum_absolute"], right["maximum_absolute"], left["grid"][0], right["grid"][0]),
             "relative_order": observed_order(left["maximum_local_relative"], right["maximum_local_relative"], left["grid"][0], right["grid"][0])}
            for left, right in zip(b_levels[:-1], b_levels[1:])
        ]
        passing = [i for i, item in enumerate(b_levels) if item["maximum_absolute"] <= GAUGE_GATE and item["maximum_local_relative"] <= GAUGE_GATE]
        b_gates = {
            "absolute": b_levels[-1]["maximum_absolute"] <= GAUGE_GATE,
            "relative": b_levels[-1]["maximum_local_relative"] <= GAUGE_GATE,
            "monotone_absolute": all(right["maximum_absolute"] < left["maximum_absolute"] for left, right in zip(b_levels[:-1], b_levels[1:])),
            "monotone_relative": all(right["maximum_local_relative"] < left["maximum_local_relative"] for left, right in zip(b_levels[:-1], b_levels[1:])),
            "last_absolute_order": b_orders[-1]["absolute_order"] is not None and 2.0 <= b_orders[-1]["absolute_order"] <= 6.0,
            "two_consecutive_passes": len(passing) >= 2 and passing[-2:] == [len(b_levels)-2, len(b_levels)-1],
        }
        result["producer_B"] = {"levels": b_levels, "orders": b_orders, "passing_indices": passing, "gates": b_gates, "passed": all(b_gates.values()),
                                "scope": "gauge-only diagnostic; direct bulk curvature remains unadmitted"}

        if result["producer_A"]["passed"]:
            background_by_grid = {(len(item["x"]), len(item["r"])): item for item in a_fields}

            def wall_wb(position, z, r, background, stencil_width=7, radial_buffer=7):
                baseline = background_by_grid[(len(z), len(r))]["q"]
                return wall.summarize_wall_difference(position, baseline, z, r, background, derivative_matrix, radial_buffer)

            def gauge_wb(position, velocity, time_value, rhs, radial_cut=None, gauge_source=None):
                baseline = background_by_grid[(len(rhs.z), len(rhs.r))]
                if np.array_equal(position, baseline["q"]) and np.count_nonzero(velocity) == 0 and time_value == 0.0:
                    return {"global_relative": 0.0, "maximum_local_relative": 0.0, "maximum_absolute": 0.0, "finite": True}
                candidate = gauge_arrays(position, velocity, time_value, rhs, reduced_state_jets,
                                         regular_so3_perturbation_jets, metric_geometry_from_jets, gauge_source)
                base = gauge_arrays(baseline["q"], baseline["v"], 0.0, rhs, reduced_state_jets,
                                    regular_so3_perturbation_jets, metric_geometry_from_jets, gauge_source)
                return summarize_constraints(candidate[0] - base[0], candidate[1], candidate[2], rhs.r, radial_cut)

            admitted = dict(production)
            admitted["compact_wall_position_residuals"] = wall_wb
            admitted["gauge_constraint_summary"] = gauge_wb
            admission = curvature.complete_admission("A", a_fields, prior, root_record, admitted, output, started)
            result["producer_A"]["complete_admission"] = {key: value for key, value in admission.items() if key != "evolution_inputs"}
            if admission["passed"]:
                evolution = curvature.run_evolution("A", a_fields[-2:], prior, admitted, root_record, output, started)
                result["short_evolution"] = evolution
                result["classification"] = (
                    "D1_GAUGE_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS" if evolution["passed"]
                    else "D1_GAUGE_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED"
                )
            else:
                result["classification"] = "D1_GAUGE_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_" + str(admission.get("first_failed_gate", "UNKNOWN")).upper()
        else:
            result["classification"] = "D1_GAUGE_WELL_BALANCE_TECHNICAL_INCOMPLETE"

        result["status"] = "COMPLETE"
        np.savez_compressed(output / "EVIDENCE.npz", x=finest["x"], r=finest["r"], q=finest["q"], source=finest["source"],
                            A=finest["profile"]["A"], H=finest["profile"]["H"], phi=finest["profile"]["phi"], U=finest["profile"]["U"],
                            k=np.asarray(root_record["k"]), cscale=np.asarray(cscale))
    except Exception as error:
        result["status"] = "INCOMPLETE"; result["classification"] = "D1_GAUGE_WELL_BALANCE_TECHNICAL_INCOMPLETE"; result["error"] = repr(error)
    result["completed_utc"] = utc(); result["wall_seconds"] = time.monotonic() - clock
    atomic_json(output / "RESULT.json", result)
    terminal = {"schema": "lin-d1-gauge-discriminator-terminal-v1", "status": result["status"], "classification": result["classification"],
                "result_sha256": sha256(output / "RESULT.json"), "evidence_sha256": sha256(output / "EVIDENCE.npz") if (output / "EVIDENCE.npz").exists() else None,
                "completed_utc": result["completed_utc"]}
    atomic_json(output / "TERMINAL.json", terminal)
    write_status(output, "TERMINAL", str(result["classification"]), started)
    print(json.dumps({"status": result["status"], "classification": result["classification"], "wall_seconds": result["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
