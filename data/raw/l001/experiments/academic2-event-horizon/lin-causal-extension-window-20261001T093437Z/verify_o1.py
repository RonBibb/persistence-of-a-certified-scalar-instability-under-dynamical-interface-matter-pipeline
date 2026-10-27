#!/usr/bin/env python3
"""Independent structural and numerical verifier for the O1 interface."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_sha(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(0o444)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def require(checks: dict[str, bool], name: str, condition: bool) -> None:
    checks[name] = bool(condition)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    result_path = args.output / "P407_R3_TERMINAL_SEED_INTERFACE.json"
    archive_path = args.output / "P407_R3_TERMINAL_SEED_INTERFACE.npz"
    result = json.loads(result_path.read_text())
    checks: dict[str, bool] = {}

    require(checks, "contract_schema", contract.get("schema") == "p407-r3-stable-band-interface-contract-v1")
    require(checks, "result_schema", result.get("schema") == "p407-r3-stable-band-terminal-seed-interface-v1")
    require(checks, "result_complete", result.get("status") == "COMPLETE")
    require(checks, "classification_exact", result.get("classification") == "P407-R3-STABLE-BAND-TERMINAL-SEED-INTERFACE-PASS")
    require(checks, "contract_binding", result.get("contract_sha256") == sha256(args.contract))
    require(checks, "archive_binding", result.get("archive_sha256") == sha256(archive_path))
    require(checks, "count_240_knots", result.get("knot_checks_passed") == 240)
    require(checks, "count_12_certificates", result.get("terminal_leaf_certificates_passed") == 12)
    require(checks, "count_12_profile_hashes", result.get("terminal_profile_hashes_matched") == 12)
    require(checks, "binary64_disclosed", result.get("precision", {}).get("surface_state_dtype") == "float64")
    require(checks, "no_longdouble_surface_claim", result.get("precision", {}).get("longdouble_used_for_surface_claim") is False)
    require(checks, "historical_namespace_not_written", result.get("historical_namespaces_written") is False)
    firewall = result.get("claim_firewall", {})
    require(checks, "event_horizon_firewall", firewall.get("event_horizon_claim_authorized") is False)
    require(checks, "boundary_compatibility_unresolved", firewall.get("boundary_acceleration_compatibility_resolved") is False)

    root = args.contract.resolve().parent
    for relative, expected in contract["local_files"].items():
        candidate = root / relative
        require(checks, f"local_unchanged:{relative}", candidate.is_file() and sha256(candidate) == expected)
    for raw, expected in contract["external_files"].items():
        candidate = Path(raw)
        require(checks, f"external_unchanged:{raw}", candidate.is_file() and sha256(candidate) == expected)

    with np.load(archive_path, allow_pickle=False) as interface:
        require(checks, "terminal_schedule_exact", np.array_equal(interface["terminal_h_steps"], np.asarray(contract["terminals"], dtype=np.int64)))
        require(checks, "resolution_schedule_exact", np.array_equal(interface["surface_resolutions"], np.asarray(contract["resolutions"], dtype=np.int64)))
        for nodes in contract["resolutions"]:
            unit_json = args.output / "units" / f"N{nodes}.json"
            unit_npz = args.output / "units" / f"N{nodes}.npz"
            unit = json.loads(unit_json.read_text())
            require(checks, f"N{nodes}:record_bound", result["resolution_units"][str(nodes)]["record_sha256"] == sha256(unit_json))
            require(checks, f"N{nodes}:archive_bound", unit.get("archive_sha256") == sha256(unit_npz) == result["resolution_units"][str(nodes)]["archive_sha256"])
            require(checks, f"N{nodes}:unit_pass", unit.get("all_checks_pass") is True)
            require(checks, f"N{nodes}:knot_count", unit.get("knot_count") == 80 and len(unit.get("knot_summaries", [])) == 80)
            require(checks, f"N{nodes}:all_knot_checks", all(item.get("all_checks_pass") is True for item in unit.get("knot_summaries", [])))
            with np.load(unit_npz, allow_pickle=False) as arrays:
                profiles = interface[f"N{nodes}_profiles"]
                modes = interface[f"N{nodes}_primary_modes"]
                require(checks, f"N{nodes}:interface_profile_count", profiles.shape[0] == 4)
                require(checks, f"N{nodes}:interface_mode_count", modes.shape[0] == 4)
                require(checks, f"N{nodes}:finite_profiles", bool(np.all(np.isfinite(profiles))))
                require(checks, f"N{nodes}:finite_modes", bool(np.all(np.isfinite(modes))))
                for index, terminal in enumerate(contract["terminals"]):
                    expected = contract["expected_terminal_profile_sha256"][str(nodes)][str(terminal)]
                    profile = arrays[f"profile_T{terminal}"]
                    mode = arrays[f"mode_T{terminal}"]
                    require(checks, f"N{nodes}:T{terminal}:expected_hash", array_sha(profile) == expected)
                    require(checks, f"N{nodes}:T{terminal}:interface_profile_exact", np.array_equal(profile, profiles[index]))
                    require(checks, f"N{nodes}:T{terminal}:interface_mode_exact", np.array_equal(mode, modes[index]))
                    terminal_record = unit["terminals"][str(terminal)]
                    require(checks, f"N{nodes}:T{terminal}:certificate_pass", terminal_record["certificate"]["all_checks_pass"] is True)
                    require(checks, f"N{nodes}:T{terminal}:record_hash", terminal_record["observed_profile"]["sha256"] == expected)

    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema": "p407-r3-independent-interface-verification-v1",
        "classification": "VERIFIED" if not failed else "NOT_VERIFIED",
        "contract_sha256": sha256(args.contract),
        "producer_result_sha256": sha256(result_path),
        "producer_archive_sha256": sha256(archive_path),
        "verifier_sha256": sha256(Path(__file__)),
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
        "scientific_scope": {
            "terminal_seed_interface_verified": not failed,
            "event_horizon_established": False,
            "boundary_acceleration_compatibility_resolved": False
        }
    }
    if args.report.exists():
        raise SystemExit("refusing to overwrite verification report")
    atomic_json(args.report, report)
    print(json.dumps({"classification": report["classification"], "check_count": len(checks), "failed_checks": failed}, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
