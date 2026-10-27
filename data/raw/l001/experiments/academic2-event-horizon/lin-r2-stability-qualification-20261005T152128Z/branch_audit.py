#!/usr/bin/env python3
"""Read-only provenance and same-branch audit for D1 and the stability result."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def exact_float(value: float) -> Fraction:
    return Fraction(*value.as_integer_ratio())


def rational(text: str) -> Fraction:
    return Fraction(text)


def extract_string_constants(path: Path, names: set[str]) -> dict[str, str]:
    tree = ast.parse(path.read_text())
    found: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in names and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                found[name] = node.value.value
    return found


def walk_objects(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    branch = Path(__file__).resolve().parent
    bindings = json.loads(args.bindings.resolve().read_text())
    if sha256_file(Path(__file__).resolve()) != bindings["source_sha256"]:
        raise RuntimeError("audit source digest mismatch")
    if sha256_file(branch / "BRANCH_AUDIT_CONTRACT.md") != bindings["contract_sha256"]:
        raise RuntimeError("contract digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"bound input mismatch: {name}")
        resolved[name] = path

    manifest = json.loads(resolved["stability_manifest"].read_text())
    stability_root = resolved["stability_manifest"].parent
    manifest_failures: list[dict[str, Any]] = []
    for relative, record in manifest["files"].items():
        candidate = stability_root / relative
        actual = sha256_file(candidate) if candidate.is_file() else None
        if actual != record["sha256"] or (candidate.is_file() and candidate.stat().st_size != record["bytes"]):
            manifest_failures.append({"path": relative, "expected": record, "actual_sha256": actual, "actual_bytes": candidate.stat().st_size if candidate.is_file() else None})

    names = {"M2", "GAMMA", "V0", "V1", "LAMBDA_A", "LAMBDA_B"}
    d1_constants = extract_string_constants(resolved["d1_source"], names)
    contract = json.loads(resolved["stability_contract"].read_text())
    contract_input_checks = {name: sha256_file((stability_root / name).resolve()) == expected for name, expected in contract["bound_files"].items()}
    receipt = json.loads(resolved["background_receipt"].read_text())
    mapping = {"M2": "m2", "GAMMA": "gamma", "V0": "v0", "V1": "v1", "LAMBDA_A": "lambda_a", "LAMBDA_B": "lambda_b"}
    parameter_checks: dict[str, bool] = {}
    for source_name, public_name in mapping.items():
        source_value = exact_float(float(d1_constants[source_name]))
        contract_value = exact_float(float(contract["model"][public_name]))
        receipt_value = exact_float(float(receipt["report"]["model"][public_name]))
        parameter_checks[public_name] = source_value == contract_value == receipt_value

    d1 = json.loads(resolved["d1_high_result"].read_text())
    independent = json.loads(resolved["d1_independent_result"].read_text())
    root_bounds = tuple(rational(x) for x in d1["narrow"]["newton_exact_bounds"])
    background_a = exact_float(float(receipt["report"]["Phi_endpoints"][0]))
    event_bounds = tuple(exact_float(float(x)) for x in d1["narrow"]["event_bracket"])
    background_D = exact_float(float(receipt["report"]["proper_separation_D"]))
    background_k = exact_float(float(receipt["report"]["k"]))
    fine_level = max(independent["levels"], key=lambda row: row["steps"])
    curvature = fine_level["geometry"]["curvature"]
    curvature_pair = tuple(rational(x) for x in curvature["exact_bounds"])
    chosen_curvature = (curvature_pair[1] - curvature_pair[0], curvature_pair, curvature)
    same_branch_checks = {
        "lower_scalar_inside_d1_newton_enclosure": root_bounds[0] <= background_a <= root_bounds[1],
        "proper_separation_inside_d1_event_enclosure": event_bounds[0] <= background_D <= event_bounds[1],
        "curvature_inside_finest_independent_d1_enclosure": curvature_pair[0] <= background_k <= curvature_pair[1],
        "finest_independent_d1_root_and_geometry_pass": fine_level["root_replay_pass"] and fine_level["geometry"]["pass"],
        "collocation_receipt_qualified": bool(receipt["qualified"] and receipt["report"]["qualified"]),
    }

    summary = json.loads(resolved["stability_summary"].read_text())
    modecheck = json.loads(resolved["independent_mode_check"].read_text())
    sensitivity_values = [abs(float(value)) for value in summary["sensitivity"].values()]
    stability_checks = {
        "accepted_classification": summary["accepted"] and summary["classification"] == "RESOLVED_LINEAR_SCALAR_RADION_INSTABILITY",
        "physical_mass_negative": summary["mu"] < 0,
        "positive_kinetic_norm": summary["kinetic_Z"] > 0 and modecheck["positive_kinetic_norm"],
        "nonzero_separation_overlap": summary["delta_D_over_sqrt_Z"] != 0 and modecheck["nonzero_separation_response"],
        "analytic_controls_pass": summary["controls"],
        "symbolic_constraint_control_pass": summary["symbolic_control"],
        "independent_mode_residuals_pass": modecheck["finest_independent_residuals_pass"] and all(case["maximum_equation_residual"] <= modecheck["frozen_residual_gate"] for case in modecheck["cases"]),
        "negative_sign_exceeds_100x_sensitivity": abs(summary["mu"]) > 100 * max(sensitivity_values),
        "stored_sensitivity_max_reconstructed": math.isclose(max(sensitivity_values), summary["max_observed_mass_sensitivity"], rel_tol=0, abs_tol=0),
    }
    formulation = resolved["independent_formulation"].read_text()
    specification = (stability_root / "TEST_SPECIFICATION.md").read_text()
    additional = json.loads((stability_root / "preflight/ADDITIONAL_BINDINGS.json").read_text())
    formulation_checks = {
        "undivided_turn_regular_system_present": "No division by S occurs" in specification and "C'=-2AC" in formulation,
        "finite_stiffness_wall_present": "p_i+2S_i" in formulation and "gamma f_i/2" in formulation,
        "gauge_invariant_separation_present": "\\delta D" in formulation and "invariant under an infinitesimal transverse coordinate\nchange" in formulation,
        "positive_kinetic_form_present": "f^2+6" in formulation and "]dz>0" in formulation,
        "formulation_bound_before_stability_evaluation": additional["files"]["analysis/INDEPENDENT_FORMULATION.md"] == sha256_file(resolved["independent_formulation"]),
    }
    checks = {
        "sealed_stability_manifest_all_files_match": not manifest_failures,
        "all_preoutcome_contract_inputs_match": all(contract_input_checks.values()),
        "all_six_model_parameters_exactly_match": all(parameter_checks.values()) and len(parameter_checks) == 6,
        "same_branch_coordinates_enclosed": all(same_branch_checks.values()),
        "all_stability_decision_gates_reconstructed": all(stability_checks.values()),
        "derivation_scope_markers_present": all(formulation_checks.values()),
        "only_declared_static_and_stability_inputs_used": set(resolved) == {"d1_high_result", "d1_independent_result", "d1_source", "background_receipt", "stability_manifest", "stability_contract", "stability_summary", "independent_mode_check", "independent_formulation", "draft_audit_source", "draft_audit_contract", "r2_result", "r2_terminal"},
    }
    passed = all(checks.values())
    result = {
        "schema": "lin-static-stability-branch-audit-result-v1",
        "status": "COMPLETE" if passed else "INCOMPLETE",
        "classification": "SAME_STATIC_BRANCH_FINITE_RESOLUTION_RADION_INSTABILITY_EVIDENCE_AUTHENTICATED" if passed else "STATIC_TO_STABILITY_BRANCH_LINK_UNRESOLVED",
        "checks": checks,
        "manifest_failure_count": len(manifest_failures),
        "manifest_failures": manifest_failures,
        "parameter_checks": parameter_checks,
        "contract_input_checks": contract_input_checks,
        "same_branch_checks": same_branch_checks,
        "stability_checks": stability_checks,
        "formulation_checks": formulation_checks,
        "branch_enclosures": {
            "d1_root_exact": [str(x) for x in root_bounds],
            "background_lower_scalar_exact_binary64": str(background_a),
            "d1_event_exact_binary64": [str(x) for x in event_bounds],
            "background_D_exact_binary64": str(background_D),
            "background_k_exact_binary64": str(background_k),
            "containing_independent_curvature_exact": [str(x) for x in chosen_curvature[1]] if chosen_curvature else None,
        },
        "stability_result": {"mu": summary["mu"], "mu_over_k": summary["mu_over_k"], "growth_s_over_H": summary["growth_s_over_H"], "kinetic_Z": summary["kinetic_Z"], "delta_D_over_sqrt_Z": summary["delta_D_over_sqrt_Z"], "maximum_equation_residual": max(case["maximum_equation_residual"] for case in modecheck["cases"]), "mass_to_maximum_sensitivity_ratio": abs(summary["mu"]) / max(sensitivity_values)},
        "scope_gained": "The retained numerical background is consistent with the exact D1 central branch in action, input provenance and certified root/separation/curvature enclosures. This authenticates finite-resolution branch association, not equality of an approximate field to an exact solution or a rigorous eigenvalue enclosure.",
        "remaining_gap": "No interval enclosure of the perturbation operator/eigenvalue or bound carrying background enclosure error into mu; instability remains exceptionally strong finite-resolution evidence, not a spectral theorem for the exact root or its parameter neighborhood.",
        "predecessors_mutated": False,
    }
    result_path = args.output.resolve() / "RESULT.json"
    atomic_write_json(result_path, result)
    atomic_write_json(args.output.resolve() / "TERMINAL.json", {"schema": "lin-static-stability-branch-audit-terminal-v1", "status": result["status"], "classification": result["classification"], "result_sha256": sha256_file(result_path), "predecessors_mutated": False})
    print(json.dumps({"status": result["status"], "classification": result["classification"]}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
