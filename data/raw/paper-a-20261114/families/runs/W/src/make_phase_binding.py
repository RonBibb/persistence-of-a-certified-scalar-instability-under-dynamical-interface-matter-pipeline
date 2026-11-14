"""Write a family member's phase inputs from its primary background record.

The archived phase driver test1_phase_v3.py and both engines run unchanged.
Only inputs/central_bindings.json differs from the archived binding: its
launch interval A is the primary producer's exact parametric Newton image and
its wall interval D is that producer's exact box event bracket.  The model
parameters stay at the archived exact values, because the zero-mass,
zero-Hessian phase flow reads only m2, gamma, v0 and lambda_a; v1 and
lambda_b enter a family member only through A and D.  SOURCE_BINDINGS.json is
the archived file with the new binding hash substituted.

usage: make_phase_binding.py PRIMARY_RECORD TEMPLATE_BINDING TEMPLATE_SOURCES OUT_DIR
"""
import hashlib
import json
import os
import sys
from fractions import Fraction


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    primary_path, template_binding, template_sources, out_dir = sys.argv[1:5]
    with open(primary_path) as handle:
        record = json.load(handle)
    result = record["producer_result"]
    if result["status"] != "COMPLETE":
        raise RuntimeError("PRIMARY_INCOMPLETE")
    if result["classification"] != "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS":
        raise RuntimeError("PRIMARY_ROOT_NOT_ESTABLISHED")
    rows = result["all_results"]
    if len(rows) != 1 or rows[0]["qualified_newton_inclusion"] is not True:
        raise RuntimeError("PRIMARY_NEWTON_NOT_QUALIFIED")
    row = rows[0]
    image = row["interval_newton_image"]["exact_bounds"]
    bracket = row["box_event"]["event_bracket"]
    if not (Fraction(image[0]) < Fraction(image[1]) and Fraction(bracket[0]) < Fraction(bracket[1])):
        raise RuntimeError("EMPTY_INTERVAL")
    if not (0 < Fraction(bracket[0]) and Fraction(bracket[1]) < 2):
        raise RuntimeError("BRACKET_OUTSIDE_INTEGRATION_INTERVAL")
    with open(template_binding) as handle:
        binding = json.load(handle)
    binding["config"]["A"] = [str(Fraction(image[0])), str(Fraction(image[1]))]
    binding["config"]["D"] = [str(Fraction(bracket[0])), str(Fraction(bracket[1]))]
    binding["family_member"] = {
        "param": record["job"]["param"],
        "interval": [record["job"]["lo"], record["job"]["hi"]],
        "A_source": "primary exact parametric interval-Newton image",
        "D_source": "primary exact box event bracket",
        "unused_by_phase_flow": ["v1", "lambda_b"],
    }
    os.makedirs(os.path.join(out_dir, "inputs"), exist_ok=True)
    binding_path = os.path.join(out_dir, "inputs", "central_bindings.json")
    with open(binding_path, "w") as handle:
        json.dump(binding, handle, indent=2, sort_keys=True)
    with open(template_sources) as handle:
        sources = json.load(handle)
    sources["inputs/central_bindings.json"]["sha256"] = sha256(binding_path)
    with open(os.path.join(out_dir, "SOURCE_BINDINGS.json"), "w") as handle:
        json.dump(sources, handle, indent=2, sort_keys=True)
    print(json.dumps({"A": binding["config"]["A"], "D": binding["config"]["D"]}))


if __name__ == "__main__":
    main()
