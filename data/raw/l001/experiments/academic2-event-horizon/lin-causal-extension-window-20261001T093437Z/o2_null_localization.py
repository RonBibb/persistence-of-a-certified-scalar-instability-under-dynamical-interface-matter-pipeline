#!/usr/bin/env python3
"""Stable-band multi-terminal backward-null localization pilot."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np


THREAD_VARIABLES = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
P407_ROOT = Path(
    "/home/parallels/research-runs/"
    "protocol407-r2-qualified-h-g10-eh-future-extension-2026-09-09"
)
P401_ROOT = Path(
    "/home/parallels/research-runs/"
    "protocol401-terminal-safe-extended-g10-mots-2026-09-08"
)
P408_SOURCE = Path(
    "/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/"
    "collapse-horizon-research/source-snapshot/free-boundary-mots-horizon-tube/"
    "protocol408-r2-p407-r2-multiterminal-eh-reconstruction-gate-2026-09-09"
)
NULL_CORE = Path(
    "/home/parallels/research-runs/"
    "protocol405-r3-terminal-packaging-and-projection-reduction-repair-2026-09-09/"
    "src/protocol399_null_core.py"
)
PRIMARY_TERMINALS = (1744, 1760, 1776, 1792)
PRIMARY_STEPS = tuple(range(512, 1537, 64))
TRACE_SPECS = (
    *(dict(tag=f"primary-T{terminal}", terminal=terminal, nodes=165, labels=257,
           formulation="coordinate", tolerance="base", role="primary")
      for terminal in PRIMARY_TERMINALS),
    dict(tag="strict-T1792", terminal=1792, nodes=165, labels=257,
         formulation="coordinate", tolerance="strict", role="control"),
    dict(tag="hamiltonian-T1792", terminal=1792, nodes=165, labels=257,
         formulation="hamiltonian", tolerance="base", role="control"),
    dict(tag="labels129-T1792", terminal=1792, nodes=165, labels=129,
         formulation="coordinate", tolerance="base", role="control"),
    dict(tag="surface157-T1792", terminal=1792, nodes=157, labels=257,
         formulation="coordinate", tolerance="base", role="control"),
    dict(tag="surface173-T1792", terminal=1792, nodes=173, labels=257,
         formulation="coordinate", tolerance="base", role="control"),
)


class PilotError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def native(value):
    if isinstance(value, dict):
        return {str(key): native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [native(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        raise PilotError("nonfinite JSON scalar")
    return value


def canonical(value: object) -> bytes:
    return (
        json.dumps(native(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(0o444)
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp-", suffix=".npz", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            np.savez(stream, **{key: np.ascontiguousarray(value) for key, value in arrays.items()})
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(0o444)
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_npz(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        arrays = {key: np.ascontiguousarray(archive[key]) for key in archive.files}
    if any(array.dtype.kind in "fc" and np.any(~np.isfinite(array)) for array in arrays.values()):
        raise PilotError(f"nonfinite array in {path}")
    return arrays


def verify_contract(path: Path) -> dict[str, object]:
    contract = json.loads(path.read_text())
    if contract.get("schema") != "stable-band-multiterminal-null-pilot-contract-v1":
        raise PilotError("contract schema differs")
    expected_specs = [dict(item) for item in TRACE_SPECS]
    if contract.get("trace_specs") != expected_specs:
        raise PilotError("trace inventory differs")
    root = path.resolve().parent
    for relative, expected in contract["local_files"].items():
        candidate = root / relative
        if not candidate.is_file() or sha256(candidate) != expected:
            raise PilotError(f"bound local file differs: {relative}")
    for raw, expected in contract["external_files"].items():
        candidate = Path(raw)
        if not candidate.is_file() or sha256(candidate) != expected:
            raise PilotError(f"bound external file differs: {raw}")
    return contract


def load_unit(path_json: Path, path_npz: Path, contract_sha: str, spec: dict[str, object]):
    if not path_json.exists() and not path_npz.exists():
        return None
    if not path_json.is_file() or not path_npz.is_file():
        raise PilotError(f"partial trace unit: {spec['tag']}")
    record = json.loads(path_json.read_text())
    arrays = load_npz(path_npz)
    if not (
        record.get("schema") == "stable-band-null-trace-unit-v1"
        and record.get("contract_sha256") == contract_sha
        and record.get("spec") == spec
        and record.get("archive_sha256") == sha256(path_npz)
    ):
        raise PilotError(f"trace checkpoint binding differs: {spec['tag']}")
    return record, arrays


def profile_for(interface: dict[str, np.ndarray], nodes: int, terminal: int) -> np.ndarray:
    terminals = np.asarray(interface["terminal_h_steps"], dtype=np.int64)
    indices = np.flatnonzero(terminals == int(terminal))
    if len(indices) != 1:
        raise PilotError("terminal is absent from O1 interface")
    profile = np.ascontiguousarray(interface[f"N{nodes}_profiles"][int(indices[0])])
    if profile.shape != (nodes,) or profile.dtype != np.float64 or np.any(~np.isfinite(profile)):
        raise PilotError("O1 profile semantics differ")
    return profile


def build_authenticated_spacetime(science):
    """Authenticate complete P407 evolution blocks without its failed terminal interface."""
    sys.path.insert(0, str(P407_ROOT))
    import mots_runner  # noqa: PLC0415
    import protocol407_schedule as p407_schedule  # noqa: PLC0415
    import runner as p407_runner  # noqa: PLC0415

    runtime = mots_runner.runtime_preflight()
    authority = p407_runner.authority_record()
    p407_runner.verify_external_records(authority)
    _, family_class, _ = mots_runner.load_science_modules(authority, P401_ROOT)
    initial = mots_runner.parent_state(authority)
    h_steps = [p407_schedule.START_H_STEP]
    q = [initial["q"]]
    v = [initial["v"]]
    evolution_receipts = []
    for block in range(1, p407_schedule.MAX_BLOCKS + 1):
        unit = p407_runner.validate_unit(p407_schedule.evolution_unit_id(block), authority)
        if unit is None:
            raise PilotError(f"authenticated P407 evolution block {block} is absent")
        evolution_receipts.append(unit["receipt_sha256"])
        local = unit["arrays"]
        for index, step in enumerate(np.asarray(local["knot_h_steps"], dtype=np.int64)):
            h_steps.append(int(step))
            q.append(np.ascontiguousarray(local["knot_q"][index]))
            v.append(np.ascontiguousarray(local["knot_v"][index]))
    h_steps = np.asarray(h_steps, dtype=np.int64)
    if (
        len(h_steps) != 81
        or h_steps[0] != p407_schedule.START_H_STEP
        or h_steps[-1] != p407_schedule.START_H_STEP + p407_schedule.MAX_EXTENSION_H_STEPS
        or np.any(np.diff(h_steps) != p407_schedule.KNOT_H_STEPS)
    ):
        raise PilotError("P407 evolution knot inventory differs")
    family, audit = mots_runner._family(family_class, h_steps, np.asarray(q), np.asarray(v))
    null_core = science._load_module("o2_bound_protocol399_null_core", NULL_CORE)
    if getattr(null_core, "PROJECTION_LOCATION_FRACTION_TOLERANCE", None) != 2.0e-10:
        raise PilotError("P405-R3 projection partition tolerance differs")
    spacetime = null_core.HermiteNullSpacetime(family)
    snapshot = {
        "authority_fingerprint": authority["fingerprint"],
        "evolution_receipt_sha256": evolution_receipts,
        "h_step_count": int(len(h_steps)),
        "first_h_step": int(h_steps[0]),
        "last_h_step": int(h_steps[-1]),
        "runtime": runtime,
    }
    return spacetime, null_core, audit, snapshot


def position_at(arrays: dict[str, np.ndarray], step: int) -> np.ndarray:
    indices = np.flatnonzero(np.asarray(arrays["steps"], dtype=np.int64) == int(step))
    if len(indices) != 1:
        raise PilotError(f"trace lacks step {step}")
    return arrays["positions"][int(indices[0])]


def compare_curves(science, null_core, spacetime, step: int, left: np.ndarray, right: np.ndarray):
    time_value = science.schedule.time_for_step(int(step))
    compared = null_core.compare_unparameterized_curves(spacetime, time_value, left, right)
    directions = (compared["left_to_right"], compared["right_to_left"])
    projection = min(float(item["projection_success_fraction"]) for item in directions)
    coverage = min(float(item["target_coverage_fraction"]) for item in directions)
    cell = min(
        science._native_cell(spacetime, time_value, left),
        science._native_cell(spacetime, time_value, right),
    )
    return {
        "step": int(step),
        "proper_hausdorff": float(compared["symmetric_proper_hausdorff"]),
        "native_cell": cell,
        "native_cell_fraction": float(compared["symmetric_proper_hausdorff"] / cell),
        "minimum_projection_success_fraction": projection,
        "minimum_target_coverage_fraction": coverage,
        "projection_and_coverage_pass": bool(projection >= 0.95 and coverage >= 0.95),
    }


def reduce_result(science, null_core, spacetime, units):
    primaries = {terminal: units[f"primary-T{terminal}"][1] for terminal in PRIMARY_TERMINALS}
    pairs = list(itertools.combinations(PRIMARY_TERMINALS, 2))
    pair_rows: dict[str, list[dict[str, object]]] = {}
    pair_tensor = np.empty((len(pairs), len(PRIMARY_STEPS)), dtype=float)
    projection_ok = True
    for pair_index, (left_terminal, right_terminal) in enumerate(pairs):
        rows = []
        for step_index, step in enumerate(PRIMARY_STEPS):
            row = compare_curves(
                science,
                null_core,
                spacetime,
                step,
                position_at(primaries[left_terminal], step),
                position_at(primaries[right_terminal], step),
            )
            rows.append(row)
            pair_tensor[pair_index, step_index] = row["native_cell_fraction"]
            projection_ok = projection_ok and row["projection_and_coverage_pass"]
        pair_rows[f"T{left_terminal}-T{right_terminal}"] = rows

    primary = units["primary-T1792"][1]
    controls = [item for item in TRACE_SPECS if item["role"] == "control"]
    control_rows = {}
    control_maxima = {}
    control_projection_ok = True
    for spec in controls:
        candidate = units[spec["tag"]][1]
        if not np.array_equal(primary["steps"], candidate["steps"]):
            raise PilotError(f"control step vector differs: {spec['tag']}")
        rows = []
        for index, step in enumerate(primary["steps"]):
            row = compare_curves(
                science,
                null_core,
                spacetime,
                int(step),
                primary["positions"][index],
                candidate["positions"][index],
            )
            rows.append(row)
            control_projection_ok = control_projection_ok and row["projection_and_coverage_pass"]
        control_rows[spec["tag"]] = rows
        control_maxima[spec["tag"]] = max(row["native_cell_fraction"] for row in rows)

    envelope = max(control_maxima.values())
    d_all = np.max(pair_tensor, axis=0)
    tail_indices = [
        index for index, pair in enumerate(pairs)
        if pair[0] != PRIMARY_TERMINALS[0]
    ]
    d_tail = np.max(pair_tensor[tail_indices], axis=0)
    budget = 0.05 / 3.0
    localized = np.asarray([
        bool(projection_ok and control_projection_ok and envelope <= budget and value + 2.0 * envelope <= 0.05)
        for value in d_all
    ], dtype=np.uint8)
    pass_count = int(np.sum(localized))
    traces_technical = bool(all(
        unit[0]["trace"]["all_checks_pass"] is True for unit in units.values()
    ))
    technically_complete = bool(traces_technical and projection_ok and control_projection_ok)
    if not technically_complete:
        classification = "TECHNICALLY-INCONCLUSIVE"
    elif pass_count >= 16:
        classification = "FINITE-ARCHIVE-TERMINAL-SHEET-LOCALIZATION-SUPPORTED"
    else:
        classification = "VALID-NO-EPOCH1-TERMINAL-LOCALIZATION-FUTURE-EXTENSION-REQUIRED"

    payload = {
        "schema": "stable-band-multiterminal-null-pilot-result-v1",
        "status": "COMPLETE",
        "classification": classification,
        "trace_technical_gates_pass": traces_technical,
        "all_curve_projections_and_coverage_pass": bool(projection_ok and control_projection_ok),
        "technically_complete": technically_complete,
        "control_maximum_native_cell_fraction": control_maxima,
        "numerical_envelope_native_cell_fraction": envelope,
        "numerical_budget_native_cell_fraction": budget,
        "localization_target_native_cell_fraction": 0.05,
        "pairwise_primary": pair_rows,
        "control_comparisons": control_rows,
        "common_steps": [
            {
                "step": int(step),
                "all_terminal_diameter_native_cell_fraction": float(d_all[index]),
                "tail_terminal_diameter_native_cell_fraction": float(d_tail[index]),
                "tail_tightening_fraction": float(d_tail[index] / d_all[index]) if d_all[index] > 0 else 0.0,
                "localized_after_allowance": bool(localized[index]),
            }
            for index, step in enumerate(PRIMARY_STEPS)
        ],
        "localized_step_count": pass_count,
        "required_localized_step_count": 16,
        "finite_archive_interpretation": (
            "A pass supports terminal-insensitivity of the constructed outgoing null sheets only on the "
            "finite P407 epoch-1 archive. A non-pass requires a longer future extension. Neither outcome "
            "defines future null infinity, escape/capture, or an event horizon."
        ),
        "conditional_on_inherited_spacetime": True,
        "boundary_acceleration_compatibility_resolved": False,
        "claim_firewall": {
            "event_horizon_claim_authorized": False,
            "future_null_infinity_claim_authorized": False,
            "causal_exterior_claim_authorized": False,
            "continuum_claim_authorized": False,
            "physical_wall_is_infinity": False,
        },
    }
    arrays = {
        "primary_steps": np.asarray(PRIMARY_STEPS, dtype=np.int64),
        "primary_terminal_pairs": np.asarray(pairs, dtype=np.int64),
        "pairwise_native_cell_fraction": pair_tensor,
        "all_terminal_diameter_native_cell_fraction": d_all,
        "tail_terminal_diameter_native_cell_fraction": d_tail,
        "localized_mask": localized,
        "numerical_envelope_native_cell_fraction": np.asarray(envelope),
    }
    return payload, arrays


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not sys.dont_write_bytecode:
        raise SystemExit("run with Python -B")
    if any(os.environ.get(name) != "1" for name in THREAD_VARIABLES):
        raise SystemExit("all numerical thread variables must equal 1")

    contract = verify_contract(args.contract)
    contract_sha = sha256(args.contract)
    output = args.output.resolve()
    units_root = output / "trace-units"
    output.mkdir(parents=True, exist_ok=True)
    units_root.mkdir(parents=True, exist_ok=True)
    if (output / "O2_RESULT.json").exists() or (output / "O2_RESULT.npz").exists():
        raise PilotError("refusing to overwrite terminal O2 result")

    sys.path.insert(0, str(P408_SOURCE))
    import science  # noqa: PLC0415

    spacetime, null_core, reproduction, p407_snapshot = build_authenticated_spacetime(science)
    if (
        reproduction["maximum_position_knot_defect"] > 2.0e-13
        or reproduction["maximum_velocity_knot_defect"] > 2.0e-13
    ):
        raise PilotError("Hermite knot reproduction failed")

    o1_archive = Path(contract["o1_interface_archive"])
    interface = load_npz(o1_archive)
    started = time.time()
    units = {}
    for spec in TRACE_SPECS:
        unit_json = units_root / f"{spec['tag']}.json"
        unit_npz = units_root / f"{spec['tag']}.npz"
        existing = load_unit(unit_json, unit_npz, contract_sha, spec)
        if existing is None:
            print(f"TRACE {spec['tag']} START", flush=True)
            trace_started = time.time()
            profile = profile_for(interface, int(spec["nodes"]), int(spec["terminal"]))
            result = science._integrate_sheet(
                null_core,
                spacetime,
                profile,
                int(spec["terminal"]),
                int(spec["labels"]),
                str(spec["formulation"]),
                str(spec["tolerance"]),
            )
            atomic_npz(unit_npz, result["arrays"])
            record = {
                "schema": "stable-band-null-trace-unit-v1",
                "contract_sha256": contract_sha,
                "spec": spec,
                "runtime_seconds": time.time() - trace_started,
                "trace": result["record"],
                "archive_sha256": sha256(unit_npz),
            }
            atomic_json(unit_json, record)
            arrays = result["arrays"]
            print(
                f"TRACE {spec['tag']} COMPLETE pass={record['trace']['all_checks_pass']} "
                f"seconds={record['runtime_seconds']:.1f}",
                flush=True,
            )
        else:
            record, arrays = existing
            print(f"TRACE {spec['tag']} REUSED", flush=True)
        units[spec["tag"]] = (record, arrays)

    result, result_arrays = reduce_result(science, null_core, spacetime, units)
    result["contract_sha256"] = contract_sha
    result["runtime_seconds"] = time.time() - started
    result["hermite_knot_reproduction"] = native(reproduction)
    result["p407_evolution_snapshot"] = p407_snapshot
    result["trace_units"] = {
        spec["tag"]: {
            "record_sha256": sha256(units_root / f"{spec['tag']}.json"),
            "archive_sha256": sha256(units_root / f"{spec['tag']}.npz"),
        }
        for spec in TRACE_SPECS
    }
    result_npz = output / "O2_RESULT.npz"
    result_json = output / "O2_RESULT.json"
    atomic_npz(result_npz, result_arrays)
    result["archive_sha256"] = sha256(result_npz)
    atomic_json(result_json, result)
    print(json.dumps({
        "classification": result["classification"],
        "localized_step_count": result["localized_step_count"],
        "numerical_envelope_native_cell_fraction": result["numerical_envelope_native_cell_fraction"],
        "runtime_seconds": result["runtime_seconds"],
        "result": str(result_json),
    }, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
