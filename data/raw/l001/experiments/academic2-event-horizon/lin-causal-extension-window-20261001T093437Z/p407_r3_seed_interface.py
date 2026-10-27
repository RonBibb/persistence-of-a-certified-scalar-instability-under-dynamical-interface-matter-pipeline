#!/usr/bin/env python3
"""Bound read-only replay producing a P407-R3 stable-band seed interface."""

from __future__ import annotations

import argparse
import hashlib
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
RESOLUTIONS = (157, 165, 173)
TERMINALS = (1744, 1760, 1776, 1792)
PARENT_SEEDS = {
    157: (161, 145),
    165: (161, 177),
    173: (177, 161),
}


class InterfaceError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_record(value: np.ndarray) -> dict[str, object]:
    value = np.ascontiguousarray(value)
    return {
        "shape": list(value.shape),
        "dtype": value.dtype.str,
        "byte_count": int(value.nbytes),
        "sha256": hashlib.sha256(value.tobytes(order="C")).hexdigest(),
    }


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
        raise InterfaceError("nonfinite JSON scalar")
    return value


def canonical(value) -> bytes:
    return (
        json.dumps(native(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: object, mode: int = 0o444) -> None:
    payload = canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(mode)
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_npz(path: Path, arrays: dict[str, np.ndarray], mode: int = 0o444) -> None:
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
        path.chmod(mode)
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_npz(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        arrays = {name: np.ascontiguousarray(archive[name]) for name in archive.files}
    if any(
        value.dtype.kind in "fc" and np.any(~np.isfinite(value))
        for value in arrays.values()
    ):
        raise InterfaceError(f"nonfinite checkpoint array: {path}")
    return arrays


def verify_contract(path: Path) -> dict[str, object]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema") != "p407-r3-stable-band-interface-contract-v1":
        raise InterfaceError("contract schema differs")
    if tuple(contract["resolutions"]) != RESOLUTIONS:
        raise InterfaceError("resolution set differs")
    if tuple(contract["terminals"]) != TERMINALS:
        raise InterfaceError("terminal schedule differs")
    root = path.resolve().parent
    for relative, expected in contract["local_files"].items():
        candidate = root / relative
        if not candidate.is_file() or sha256(candidate) != expected:
            raise InterfaceError(f"bound local file differs: {relative}")
    for raw_path, expected in contract["external_files"].items():
        candidate = Path(raw_path)
        if not candidate.is_file() or sha256(candidate) != expected:
            raise InterfaceError(f"bound external file differs: {raw_path}")
    return contract


def solve_summary(record: dict[str, object]) -> dict[str, object]:
    return {
        "all_checks_pass": bool(record["all_checks_pass"]),
        "failed_checks": sorted(
            name for name, passed in record["checks"].items() if not passed
        ),
        "distinct_seed_profile_distance": float(record["distinct_seed_profile_distance"]),
        "predictor_correction_maximum": float(record["predictor_correction_maximum"]),
        "adjacent_profile_change_maximum": float(record["adjacent_profile_change_maximum"]),
        "predictor_residual_maximum": float(
            record["predictor_seed_solve"]["residual_maximum"]
        ),
        "previous_residual_maximum": float(
            record["previous_profile_seed_solve"]["residual_maximum"]
        ),
        "both_repeats_bitwise_exact": bool(
            record["predictor_seed_solve"]["repeat_bitwise_exact"]
            and record["previous_profile_seed_solve"]["repeat_bitwise_exact"]
        ),
    }


def certificate_summary(record: dict[str, object]) -> dict[str, object]:
    primary = record["stability"]["sweeps"]["4e-04"]
    tangent = record["tangents"]["left"]
    return {
        "all_checks_pass": bool(record["all_checks_pass"]),
        "failed_checks": sorted(
            name for name, passed in record["checks"].items() if not passed
        ),
        "dense_theta_plus_maximum": float(record["dense"]["theta_plus_maximum"]),
        "dense_theta_minus_maximum": float(record["dense"]["theta_minus_maximum"]),
        "area": float(record["area"]["finest_area"]),
        "principal_eigenvalue_real": float(primary["principal_eigenvalue_real"]),
        "A_minimum": float(tangent["A_minimum"]),
        "B_minimum": float(tangent["B_minimum"]),
        "X2_minimum": float(tangent["X2_minimum"]),
    }


def validate_existing_unit(
    nodes: int,
    unit_json: Path,
    unit_npz: Path,
    contract_sha256: str,
    expected_hashes: dict[str, str],
) -> tuple[dict[str, object], dict[str, np.ndarray]] | None:
    if not unit_json.exists() and not unit_npz.exists():
        return None
    if not unit_json.is_file() or not unit_npz.is_file():
        raise InterfaceError(f"partial checkpoint for N={nodes}")
    record = json.loads(unit_json.read_text(encoding="utf-8"))
    arrays = load_npz(unit_npz)
    if not (
        record.get("schema") == "p407-r3-resolution-unit-v1"
        and record.get("nodes") == nodes
        and record.get("contract_sha256") == contract_sha256
        and record.get("archive_sha256") == sha256(unit_npz)
        and record.get("all_checks_pass") is True
    ):
        raise InterfaceError(f"checkpoint binding differs for N={nodes}")
    for terminal in TERMINALS:
        key = f"profile_T{terminal}"
        if key not in arrays or array_record(arrays[key])["sha256"] != expected_hashes[str(terminal)]:
            raise InterfaceError(f"checkpoint terminal profile differs: N={nodes}, T={terminal}")
    return record, arrays


def compute_resolution(
    nodes: int,
    authority,
    runner,
    mots_runner,
    schedule,
    modules,
    expected_hashes: dict[str, str],
) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    mots_core, family_class, problem_class = modules
    parent_profiles = {
        source_nodes: mots_runner.parent_profile(authority, source_nodes)
        for source_nodes in (145, 161, 177)
    }
    block1_family, _ = mots_runner._block_family(authority, 1, family_class)
    problem = problem_class(block1_family, nodes=nodes)
    start_parameter = block1_family.parameter_at_time(
        float(schedule.h_step_time(schedule.START_H_STEP))
    )
    primary_parent, alternate_parent = PARENT_SEEDS[nodes]
    primary_seed = mots_core.chebyshev_values(parent_profiles[primary_parent], problem.x)
    alternate_seed = mots_core.chebyshev_values(parent_profiles[alternate_parent], problem.x)
    previous, anchor_solve, _ = mots_core.solve_tracked_leaf(
        problem, start_parameter, primary_seed, alternate_seed
    )
    anchor_dense, _ = mots_core.certify_dense_spine_root(
        problem, previous, start_parameter, anchor_solve
    )
    if not anchor_solve["all_checks_pass"] or not anchor_dense["all_checks_pass"]:
        raise InterfaceError(f"N={nodes} parent anchor failed")

    before = None
    before_parameter = None
    previous_parameter = start_parameter
    knot_summaries = []
    terminal_records: dict[str, object] = {}
    output_arrays: dict[str, np.ndarray] = {}

    for block in range(1, schedule.MAX_BLOCKS + 1):
        family, reproduction = mots_runner._block_family(
            authority, block, family_class
        )
        if (
            reproduction["maximum_position_knot_defect"] > 2e-13
            or reproduction["maximum_velocity_knot_defect"] > 2e-13
        ):
            raise InterfaceError(f"N={nodes} block {block} knot reproduction failed")
        problem = problem_class(family, nodes=nodes)
        evolution = runner.validate_unit(schedule.evolution_unit_id(block), authority)
        if evolution is None:
            raise InterfaceError(f"missing authenticated evolution block {block}")
        for knot_index, h_step in enumerate(schedule.block_knot_h_steps(block)):
            parameter = family.parameter_at_time(float(schedule.h_step_time(h_step)))
            predictor = (
                previous.copy()
                if before is None
                else mots_core.secant_predictor(
                    before,
                    previous,
                    before_parameter,
                    previous_parameter,
                    parameter,
                )
            )
            profile, solve_record, _ = mots_core.solve_tracked_leaf(
                problem, parameter, predictor, previous
            )
            dense_record, _ = mots_core.certify_dense_spine_root(
                problem, profile, parameter, solve_record
            )
            passed = bool(
                solve_record["all_checks_pass"] and dense_record["all_checks_pass"]
            )
            knot_summaries.append({
                "block": block,
                "h_step": int(h_step),
                "profile": array_record(profile),
                "solve": solve_summary(solve_record),
                "dense_theta_plus_maximum": float(
                    dense_record["dense"]["theta_plus_maximum"]
                ),
                "all_checks_pass": passed,
            })
            if not passed:
                raise InterfaceError(f"N={nodes} lineage failed at H-step {h_step}")

            if h_step in TERMINALS:
                state = {
                    "q": evolution["arrays"]["knot_q"][knot_index],
                    "v": evolution["arrays"]["knot_v"][knot_index],
                }
                certificate, certificate_arrays = mots_core.certify_leaf(
                    problem,
                    profile,
                    parameter,
                    state,
                    ("left",),
                    solve_record,
                )
                observed_hash = array_record(profile)["sha256"]
                expected_hash = expected_hashes[str(h_step)]
                if observed_hash != expected_hash:
                    raise InterfaceError(
                        f"N={nodes}, T={h_step} profile differs from bound confirmation"
                    )
                if not certificate["all_checks_pass"]:
                    raise InterfaceError(
                        f"N={nodes}, T={h_step} complete leaf certificate failed"
                    )
                output_arrays[f"profile_T{h_step}"] = np.asarray(profile)
                output_arrays[f"mode_T{h_step}"] = np.asarray(
                    certificate_arrays["stability_4e-04_principal_mode"]
                )
                terminal_records[str(h_step)] = {
                    "expected_profile_sha256": expected_hash,
                    "observed_profile": array_record(profile),
                    "certificate": certificate_summary(certificate),
                }

            before, before_parameter = previous, previous_parameter
            previous, previous_parameter = profile, parameter

    if len(knot_summaries) != 80 or set(map(int, terminal_records)) != set(TERMINALS):
        raise InterfaceError(f"N={nodes} lineage inventory differs")
    record = {
        "schema": "p407-r3-resolution-unit-v1",
        "nodes": nodes,
        "parent_seed_resolutions": [primary_parent, alternate_parent],
        "parent_anchor_solve": solve_summary(anchor_solve),
        "knot_count": len(knot_summaries),
        "knot_summaries": knot_summaries,
        "terminals": terminal_records,
        "all_checks_pass": True,
    }
    return record, output_arrays


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
    units = output / "units"
    output.mkdir(parents=True, exist_ok=True)
    units.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(P407_ROOT))
    import mots_runner  # noqa: PLC0415
    import protocol407_schedule as schedule  # noqa: PLC0415
    import runner  # noqa: PLC0415

    runtime = mots_runner.runtime_preflight()
    authority = runner.authority_record()
    runner.verify_external_records(authority)
    modules = mots_runner.load_science_modules(authority, P401_ROOT)
    started = time.time()
    unit_records = {}
    unit_arrays = {}

    for nodes in RESOLUTIONS:
        unit_json = units / f"N{nodes}.json"
        unit_npz = units / f"N{nodes}.npz"
        expected = contract["expected_terminal_profile_sha256"][str(nodes)]
        existing = validate_existing_unit(
            nodes, unit_json, unit_npz, contract_sha, expected
        )
        if existing is None:
            print(f"N={nodes} full-lineage replay", flush=True)
            record, arrays = compute_resolution(
                nodes,
                authority,
                runner,
                mots_runner,
                schedule,
                modules,
                expected,
            )
            record["contract_sha256"] = contract_sha
            atomic_npz(unit_npz, arrays)
            record["archive_sha256"] = sha256(unit_npz)
            atomic_json(unit_json, record)
        else:
            print(f"N={nodes} authenticated checkpoint reused", flush=True)
            record, arrays = existing
        unit_records[str(nodes)] = record
        unit_arrays[nodes] = arrays

    interface_arrays = {
        "terminal_h_steps": np.asarray(TERMINALS, dtype=np.int64),
        "surface_resolutions": np.asarray(RESOLUTIONS, dtype=np.int64),
    }
    for nodes in RESOLUTIONS:
        interface_arrays[f"N{nodes}_profiles"] = np.asarray([
            unit_arrays[nodes][f"profile_T{terminal}"] for terminal in TERMINALS
        ])
        interface_arrays[f"N{nodes}_primary_modes"] = np.asarray([
            unit_arrays[nodes][f"mode_T{terminal}"] for terminal in TERMINALS
        ])

    interface_npz = output / "P407_R3_TERMINAL_SEED_INTERFACE.npz"
    interface_json = output / "P407_R3_TERMINAL_SEED_INTERFACE.json"
    if interface_npz.exists() or interface_json.exists():
        raise InterfaceError("refusing to overwrite terminal interface")
    atomic_npz(interface_npz, interface_arrays)
    result = {
        "schema": "p407-r3-stable-band-terminal-seed-interface-v1",
        "status": "COMPLETE",
        "classification": "P407-R3-STABLE-BAND-TERMINAL-SEED-INTERFACE-PASS",
        "contract_sha256": contract_sha,
        "runtime_seconds": time.time() - started,
        "runtime": runtime,
        "precision": {
            "surface_state_dtype": "float64",
            "numpy_float64_nmant": int(np.finfo(np.float64).nmant),
            "numpy_longdouble_nmant": int(np.finfo(np.longdouble).nmant),
            "longdouble_used_for_surface_claim": False,
        },
        "resolutions": list(RESOLUTIONS),
        "terminals": list(TERMINALS),
        "knot_checks_passed": 240,
        "terminal_leaf_certificates_passed": 12,
        "terminal_profile_hashes_matched": 12,
        "resolution_units": {
            str(nodes): {
                "record_sha256": sha256(units / f"N{nodes}.json"),
                "archive_sha256": sha256(units / f"N{nodes}.npz"),
            }
            for nodes in RESOLUTIONS
        },
        "archive_sha256": sha256(interface_npz),
        "archive_arrays": {
            name: array_record(value) for name, value in interface_arrays.items()
        },
        "historical_namespaces_written": False,
        "conditional_inherited_spacetime": True,
        "claim_firewall": {
            "p407_r2_retroactively_completed": False,
            "global_outermostness_claim_authorized": False,
            "event_horizon_claim_authorized": False,
            "escape_capture_claim_authorized": False,
            "continuum_spacetime_claim_authorized": False,
            "boundary_acceleration_compatibility_resolved": False,
        },
    }
    atomic_json(interface_json, result)
    print(json.dumps({
        "status": result["status"],
        "classification": result["classification"],
        "runtime_seconds": result["runtime_seconds"],
        "result": str(interface_json),
    }, sort_keys=True, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
