#!/usr/bin/env python3
"""Close the D1 raw-GH gate and conditionally test bounded scalar response."""

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


STENCIL = 7
NR = 241
ANCHOR_NX = 257
NEW_NX = (385, 513)
RAW_GATE = 1e-4
PERTURB_GRID = (97, 181)
PERTURB_AMPLITUDE = 1e-6
PERTURB_SUPPORT_R = 4.0
PERTURB_STEPS = 8
DT = 0.000125
PERTURB_GATES = {
    "acceleration_minimum": 1e-12,
    "acceleration_maximum": 1e-2,
    "wall": 2e-5,
    "gauge_absolute": 2e-4,
    "hamiltonian_floor": 5e-6,
    "departure": 1e-4,
    "final_scalar_velocity_minimum": 1e-12,
}


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maximum(value: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(value, dtype=float))))


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            default=lambda item: item.item() if isinstance(item, np.generic) else str(item),
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def atomic_npz(path: Path, **arrays: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    os.replace(temporary, path)


def status(output: Path, phase: str, detail: str, started: str) -> None:
    atomic_json(
        output / "STATUS.json",
        {
            "schema": "lin-d1-raw-gh-dynamical-status-v1",
            "started_utc": started,
            "updated_utc": utc(),
            "phase": phase,
            "detail": detail,
            "pid": os.getpid(),
        },
    )


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_bindings(root: Path, here: Path) -> list[dict[str, str]]:
    bindings = json.loads((here / "BINDINGS.json").read_text(encoding="utf-8"))
    verified: list[dict[str, str]] = []
    for entry in bindings["parents"] + bindings["production_sources"]:
        path = root / entry["path"]
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise RuntimeError(f"binding changed: {entry['path']} {actual}")
        verified.append(
            {
                "role": entry.get("role", "production_source"),
                "path": entry["path"],
                "sha256": actual,
            }
        )
    return verified


def perturbation_shape(x: np.ndarray, r: np.ndarray) -> np.ndarray:
    compact = np.sin(math.pi * (x - 1.0) / (math.e - 1.0)) ** 4
    compact[0] = 0.0
    compact[-1] = 0.0
    scaled = r / PERTURB_SUPPORT_R
    radial = np.where(scaled < 1.0, (1.0 - scaled * scaled) ** 4, 0.0)
    return compact[:, None] * radial[None, :]


def normalized_departure(q: np.ndarray, v: np.ndarray, q_background: np.ndarray) -> float:
    values = []
    for field in range(q.shape[2]):
        scale = max(1.0, maximum(q_background[:, :, field]))
        values.append(maximum(q[:, :, field] - q_background[:, :, field]) / scale)
        values.append(maximum(v[:, :, field]) / scale)
    return max(values)


def raw_gate(levels: list[dict[str, Any]], order_function) -> tuple[dict[str, bool], list[dict[str, Any]], list[int]]:
    orders = []
    for left, right in zip(levels[:-1], levels[1:]):
        orders.append(
            {
                "from_Nx": left["grid"][0],
                "to_Nx": right["grid"][0],
                "order": order_function(
                    left["maximum_normalized"],
                    right["maximum_normalized"],
                    left["grid"][0],
                    right["grid"][0],
                ),
            }
        )
    passing = [
        index
        for index, level in enumerate(levels)
        if level["finite"] and level["maximum_normalized"] <= RAW_GATE
    ]
    gates = {
        "finite": all(level["finite"] for level in levels),
        "monotone": all(
            right["maximum_normalized"] < left["maximum_normalized"]
            for left, right in zip(levels[:-1], levels[1:])
        ),
        "last_order": orders[-1]["order"] is not None and 2.0 <= orders[-1]["order"] <= 6.0,
        "finest": levels[-1]["maximum_normalized"] <= RAW_GATE,
        "two_consecutive": len(passing) >= 2
        and passing[-2:] == [len(levels) - 2, len(levels) - 1],
    }
    return gates, orders, passing


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
    contract_hash = sha256(here / "CONTRACT.md")
    bindings_hash = sha256(here / "BINDINGS.json")
    source_hash = sha256(here / "d1_raw_gh_qualification.py")
    parent_result_path = root / "branches/02-event-horizon/lin-d1-gh-well-balance-discriminator-20261004T203750Z/output/RESULT.json"
    parent_result_hash = sha256(parent_result_path)
    result: dict[str, Any] = {
        "schema": "lin-d1-raw-gh-dynamical-qualification-result-v1",
        "status": "RUNNING",
        "classification": None,
        "started_utc": started,
        "contract_sha256": contract_hash,
        "bindings_sha256": bindings_hash,
        "source_sha256": source_hash,
        "parent_result_sha256": parent_result_hash,
        "claim_boundary": [
            "Raw-GH finite-resolution qualification and one bounded short scalar response only.",
            "No continuum stability, collapse, P16, horizon, or parent-child inference.",
        ],
    }

    try:
        status(output, "AUTHENTICATION", "verifying frozen parents and sources", started)
        result["bindings_verified"] = verify_bindings(root, here)

        d1_dir = root / "branches/02-event-horizon/lin-d1-cauchy-background-admission-20261004T172121Z"
        gh_dir = root / "branches/02-event-horizon/lin-d1-gh-well-balance-discriminator-20261004T203750Z"
        curvature_dir = root / "branches/02-event-horizon/lin-d1-curvature-well-balance-discriminator-20261004T190608Z"
        wall_dir = root / "branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-20261004T200437Z"
        adapter_dir = root / "branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-r1-20261004T201152Z"
        gauge_dir = root / "branches/02-event-horizon/lin-d1-gauge-well-balance-discriminator-20261004T202200Z"
        source_root = root / "branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src"

        prior = import_path("qual_prior", d1_dir / "d1_background_admission.py")
        gh = import_path("qual_gh", gh_dir / "d1_gh_discriminator.py")
        curvature = import_path("qual_curvature", curvature_dir / "d1_curvature_discriminator.py")
        wall = import_path("qual_wall", wall_dir / "d1_wall_discriminator.py")
        adapter = import_path("qual_adapter", adapter_dir / "d1_wall_discriminator_r1.py")
        gauge = import_path("qual_gauge", gauge_dir / "d1_gauge_discriminator.py")
        sys.path.insert(0, str(source_root))

        from bhps.gw_slice_high_order_solver import derivative_matrix
        from bhps.linearized_gh_einstein_scalar import metric_geometry_from_jets
        from bhps.nonlinear_regular_so3_evolution import (
            NativeRegularSO3RHS,
            StageRegularGaugeSource,
            reduced_state_jets,
        )
        from bhps.regular_so3_gh_reduction import regular_so3_perturbation_jets

        Stage = adapter.compatible_stage_source_class(StageRegularGaugeSource)
        representative = prior.solve_representative_root()
        sample, conformal_length, compact_scale = prior.make_profile(representative)
        result["representative_root"] = {
            "a": representative["a"],
            "D": representative["D"],
            "L": conformal_length,
            "k": representative["k"],
        }

        parent_result = json.loads(parent_result_path.read_text(encoding="utf-8"))
        parent_levels = parent_result["producer_B"]["levels"]
        parent_anchor = next(level for level in parent_levels if level["grid"] == [ANCHOR_NX, NR])

        computed_levels: dict[int, dict[str, Any]] = {}
        for nx in (ANCHOR_NX,) + NEW_NX:
            cache = output / f"RAW_GH_{nx}x{NR}.json"
            if cache.exists():
                payload = json.loads(cache.read_text(encoding="utf-8"))
                compatible = (
                    payload.get("contract_sha256") == contract_hash
                    and payload.get("bindings_sha256") == bindings_hash
                    and payload.get("source_sha256") == source_hash
                    and payload.get("parent_result_sha256") == parent_result_hash
                    and payload.get("grid") == [nx, NR]
                )
                if not compatible:
                    raise RuntimeError(f"incompatible raw-level checkpoint: {cache}")
                computed_levels[nx] = payload["record"]
                continue

            status(output, "RAW_GH", f"evaluating unchanged {nx}x{NR}", started)
            fields = prior.represented_fields(
                nx, NR, sample, representative["k"], compact_scale
            )
            _source, rhs = gh.make_rhs(fields, prior, Stage, NativeRegularSO3RHS)
            acceleration, diagnostic = rhs.acceleration(0.0, fields["q"], fields["v"])
            record = {
                "grid": [nx, NR],
                **prior.gh_acceleration_record(
                    acceleration, fields["q"], diagnostic
                ),
            }
            atomic_json(
                cache,
                {
                    "schema": "lin-d1-raw-gh-level-v1",
                    "grid": [nx, NR],
                    "contract_sha256": contract_hash,
                    "bindings_sha256": bindings_hash,
                    "source_sha256": source_hash,
                    "parent_result_sha256": parent_result_hash,
                    "record": record,
                },
            )
            computed_levels[nx] = record

        anchor_exact = computed_levels[ANCHOR_NX] == parent_anchor
        combined_levels = [
            level for level in parent_levels if level["grid"][0] < ANCHOR_NX
        ] + [computed_levels[ANCHOR_NX], computed_levels[385], computed_levels[513]]
        raw_gates, raw_orders, passing_indices = raw_gate(combined_levels, gh.order)
        raw_gates = {"anchor_exact": anchor_exact, **raw_gates}
        raw_passed = all(raw_gates.values())
        result["raw_gh_extension"] = {
            "levels": combined_levels,
            "orders": raw_orders,
            "passing_indices": passing_indices,
            "gates": raw_gates,
            "passed": raw_passed,
        }

        final_q = None
        final_v = None
        shape = None
        background = None
        if not raw_passed:
            result["classification"] = (
                "D1_RAW_GH_TWO_LEVEL_GATE_NOT_MET__PERTURBATION_NOT_RUN"
            )
            result["perturbation"] = {"status": "NOT_RUN_RAW_GATE_FAILED"}
        else:
            status(output, "PERTURBATION", "constructing physical scalar bump", started)
            nx, nr = PERTURB_GRID
            background = prior.represented_fields(
                nx, nr, sample, representative["k"], compact_scale
            )
            baseline = {(nx, nr): background}
            WellBalancedRHS = gh.wb_rhs_class(NativeRegularSO3RHS, baseline)
            source, rhs = gh.make_rhs(background, prior, Stage, WellBalancedRHS)
            shape = perturbation_shape(background["x"], background["r"])
            q_initial = background["q"].copy()
            q_initial[:, :, 7] += PERTURB_AMPLITUDE * shape
            v_initial = np.zeros_like(q_initial)
            initial_scalar_amplitude = maximum(q_initial[:, :, 7] - background["q"][:, :, 7])

            acceleration_initial, diagnostic_initial = rhs.acceleration(
                0.0, q_initial, v_initial
            )
            acceleration_record = prior.gh_acceleration_record(
                acceleration_initial, q_initial, diagnostic_initial
            )
            raw_h_background = prior.dynamic_hamiltonian(
                background["q"],
                background["v"],
                background["x"],
                background["r"],
                reduced_state_jets,
                regular_so3_perturbation_jets,
                metric_geometry_from_jets,
            )
            raw_h_initial = prior.dynamic_hamiltonian(
                q_initial,
                v_initial,
                background["x"],
                background["r"],
                reduced_state_jets,
                regular_so3_perturbation_jets,
                metric_geometry_from_jets,
            )
            initial_hamiltonian_change = maximum(raw_h_initial - raw_h_background)
            hamiltonian_limit = max(
                4.0 * initial_hamiltonian_change,
                PERTURB_GATES["hamiltonian_floor"],
            )

            def wall_record(q: np.ndarray) -> dict[str, Any]:
                return wall.summarize_wall_difference(
                    q,
                    background["q"],
                    background["x"],
                    background["r"],
                    prior.background_record(),
                    derivative_matrix,
                    0,
                )

            background_gauge = gauge.gauge_arrays(
                background["q"],
                background["v"],
                0.0,
                rhs,
                reduced_state_jets,
                regular_so3_perturbation_jets,
                metric_geometry_from_jets,
                source,
            )

            def gauge_record(q: np.ndarray, v: np.ndarray, t: float) -> dict[str, Any]:
                candidate = gauge.gauge_arrays(
                    q,
                    v,
                    t,
                    rhs,
                    reduced_state_jets,
                    regular_so3_perturbation_jets,
                    metric_geometry_from_jets,
                    source,
                )
                return gauge.summarize_constraints(
                    candidate[0] - background_gauge[0],
                    candidate[1],
                    candidate[2],
                    rhs.r,
                    None,
                )

            q = q_initial.copy()
            v = v_initial.copy()
            records: list[dict[str, Any]] = []
            resume_step = 0
            for step in range(1, PERTURB_STEPS + 1):
                checkpoint = output / f"PERTURB_STEP_{step}.npz"
                record_path = output / f"PERTURB_STEP_{step}.json"
                if not checkpoint.exists() or not record_path.exists():
                    break
                with np.load(checkpoint, allow_pickle=False) as saved:
                    compatible = (
                        int(saved["step"]) == step
                        and float(saved["dt"]) == DT
                        and str(saved["contract_sha256"]) == contract_hash
                        and str(saved["bindings_sha256"]) == bindings_hash
                        and str(saved["source_sha256"]) == source_hash
                        and str(saved["parent_result_sha256"]) == parent_result_hash
                    )
                    if not compatible:
                        raise RuntimeError(f"incompatible perturbation checkpoint {checkpoint}")
                    q = saved["q"].copy()
                    v = saved["v"].copy()
                records.append(json.loads(record_path.read_text(encoding="utf-8")))
                resume_step = step

            stage_failure = None
            for step in range(resume_step + 1, PERTURB_STEPS + 1):
                status(output, "PERTURBATION", f"step {step}/{PERTURB_STEPS}", started)
                t0 = (step - 1) * DT
                acceleration_1, diagnostic_1 = rhs.acceleration(t0, q, v)
                q_mid = q + 0.5 * DT * v
                v_mid = v + 0.5 * DT * acceleration_1
                acceleration_2, diagnostic_2 = rhs.acceleration(
                    t0 + 0.5 * DT, q_mid, v_mid
                )
                stage_finite = bool(
                    diagnostic_1["finite"]
                    and diagnostic_2["finite"]
                    and np.all(np.isfinite(q_mid))
                    and np.all(np.isfinite(v_mid))
                    and np.all(np.isfinite(acceleration_2))
                )
                if not stage_finite:
                    stage_failure = f"step_{step}_nonfinite"
                    break
                q = q + DT * v_mid
                v = v + DT * acceleration_2

                positivity = prior.positivity({**background, "q": q, "f": background["f"]})
                wall_value = wall_record(q)
                gauge_value = gauge_record(q, v, step * DT)
                raw_h = prior.dynamic_hamiltonian(
                    q,
                    v,
                    background["x"],
                    background["r"],
                    reduced_state_jets,
                    regular_so3_perturbation_jets,
                    metric_geometry_from_jets,
                )
                hamiltonian_change = maximum(raw_h - raw_h_background)
                departure = normalized_departure(q, v, background["q"])
                scalar_velocity = maximum(v[:, :, 7])
                scalar_change_from_initial = maximum(q[:, :, 7] - q_initial[:, :, 7])
                step_gates = {
                    "finite": bool(np.all(np.isfinite(q)) and np.all(np.isfinite(v))),
                    "positivity": bool(positivity["passed"]),
                    "wall": wall_value["maximum"] <= PERTURB_GATES["wall"],
                    "gauge": bool(
                        gauge_value["finite"]
                        and gauge_value["maximum_absolute"]
                        <= PERTURB_GATES["gauge_absolute"]
                    ),
                    "hamiltonian": hamiltonian_change <= hamiltonian_limit,
                    "departure": departure <= PERTURB_GATES["departure"],
                }
                step_record = {
                    "schema": "lin-d1-perturbation-step-v1",
                    "step": step,
                    "time": step * DT,
                    "hamiltonian_change": hamiltonian_change,
                    "hamiltonian_limit": hamiltonian_limit,
                    "wall": wall_value["maximum"],
                    "gauge": gauge_value,
                    "departure_from_equilibrium": departure,
                    "scalar_velocity": scalar_velocity,
                    "scalar_change_from_initial": scalar_change_from_initial,
                    "positivity": positivity,
                    "gates": step_gates,
                    "passed": all(step_gates.values()),
                }
                checkpoint = output / f"PERTURB_STEP_{step}.npz"
                atomic_npz(
                    checkpoint,
                    q=q,
                    v=v,
                    step=np.asarray(step),
                    dt=np.asarray(DT),
                    contract_sha256=np.asarray(contract_hash),
                    bindings_sha256=np.asarray(bindings_hash),
                    source_sha256=np.asarray(source_hash),
                    parent_result_sha256=np.asarray(parent_result_hash),
                )
                atomic_json(output / f"PERTURB_STEP_{step}.json", step_record)
                records.append(step_record)
                if not step_record["passed"]:
                    stage_failure = f"step_{step}_gate"
                    break

            final_q = q
            final_v = v
            response_gates = {
                "initial_amplitude": 0.5 * PERTURB_AMPLITUDE
                <= initial_scalar_amplitude
                <= PERTURB_AMPLITUDE,
                "initial_acceleration_finite": bool(acceleration_record["finite"]),
                "initial_acceleration_nonzero": acceleration_record["maximum_normalized"]
                > PERTURB_GATES["acceleration_minimum"],
                "initial_acceleration_bounded": acceleration_record["maximum_normalized"]
                <= PERTURB_GATES["acceleration_maximum"],
                "all_steps": stage_failure is None
                and len(records) == PERTURB_STEPS
                and all(record["passed"] for record in records),
                "dynamic_response_nonzero": len(records) == PERTURB_STEPS
                and records[-1]["scalar_velocity"]
                > PERTURB_GATES["final_scalar_velocity_minimum"],
            }
            perturbation_passed = all(response_gates.values())
            result["perturbation"] = {
                "status": "COMPLETE" if len(records) == PERTURB_STEPS else "STOPPED",
                "grid": list(PERTURB_GRID),
                "amplitude": PERTURB_AMPLITUDE,
                "support_radius": PERTURB_SUPPORT_R,
                "steps": PERTURB_STEPS,
                "dt": DT,
                "initial_scalar_amplitude": initial_scalar_amplitude,
                "initial_acceleration": acceleration_record,
                "initial_hamiltonian_change": initial_hamiltonian_change,
                "hamiltonian_limit": hamiltonian_limit,
                "records": records,
                "stage_failure": stage_failure,
                "gates": response_gates,
                "passed": perturbation_passed,
            }
            result["classification"] = (
                "D1_RAW_GH_TWO_LEVEL_GATE_PASS__BOUNDED_SHORT_SCALAR_RESPONSE"
                if perturbation_passed
                else "D1_RAW_GH_TWO_LEVEL_GATE_PASS__PERTURBED_RESPONSE_BLOCKED"
            )

        result["status"] = "COMPLETE"
        evidence: dict[str, Any] = {
            "raw_Nx": np.asarray([level["grid"][0] for level in combined_levels]),
            "raw_maximum": np.asarray(
                [level["maximum_normalized"] for level in combined_levels]
            ),
        }
        if background is not None and shape is not None:
            evidence.update(
                {
                    "x": background["x"],
                    "r": background["r"],
                    "shape": shape,
                    "q_background": background["q"],
                    "q_final": final_q,
                    "v_final": final_v,
                }
            )
        atomic_npz(output / "EVIDENCE.npz", **evidence)
    except Exception as error:
        result["status"] = "INCOMPLETE"
        result["classification"] = (
            "D1_RAW_GH_DYNAMICAL_QUALIFICATION_TECHNICAL_INCOMPLETE"
        )
        result["error"] = repr(error)

    result["completed_utc"] = utc()
    result["wall_seconds"] = time.monotonic() - clock
    atomic_json(output / "RESULT.json", result)
    terminal = {
        "schema": "lin-d1-raw-gh-dynamical-terminal-v1",
        "status": result["status"],
        "classification": result["classification"],
        "result_sha256": sha256(output / "RESULT.json"),
        "evidence_sha256": sha256(output / "EVIDENCE.npz")
        if (output / "EVIDENCE.npz").exists()
        else None,
        "completed_utc": result["completed_utc"],
    }
    atomic_json(output / "TERMINAL.json", terminal)
    status(output, "TERMINAL", str(result["classification"]), started)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": result["classification"],
                "wall_seconds": result["wall_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
