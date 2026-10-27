#!/usr/bin/env python3

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
R2 = HERE.parent / "lin-d1-raw-gh-dynamical-qualification-r2-roundoff-audit-20261005T004308Z"
SPEC = importlib.util.spec_from_file_location("frozen_r2_verifier", R2 / "independent_verify_r2.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import frozen R2 verifier")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            default=lambda item: item.item() if isinstance(item, np.generic) else str(item),
        )
        + "\n"
    )
    os.replace(temporary, path)


MODULE.atomic_json = atomic_json


def main():
    namespace_index = sys.argv.index("--namespace") + 1
    namespace = Path(sys.argv[namespace_index]).resolve()
    receipt_index = sys.argv.index("--receipt")
    receipt_path = Path(sys.argv[receipt_index + 1]).resolve()
    del sys.argv[receipt_index : receipt_index + 2]
    try:
        MODULE.main()
    except TypeError as error:
        if "bool_ is not JSON serializable" not in str(error):
            raise
    audit_path = namespace / "output/INDEPENDENT_AUDIT.json"
    audit = json.loads(audit_path.read_text())
    receipt = {
        "schema": "lin-d1-raw-gh-r3-audit-adapter-receipt-v1",
        "status": "COMPLETE",
        "classification": audit["classification"],
        "corrected_classification": audit["corrected_classification"],
        "audit_path": str(audit_path),
        "audit_sha256": sha256(audit_path),
        "r2_verifier_sha256": sha256(R2 / "independent_verify_r2.py"),
        "adapter_sha256": sha256(HERE / "run_verifier_adapter.py"),
    }
    atomic_json(receipt_path, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    raise SystemExit(0 if audit["classification"] == "VERIFIED" else 1)


if __name__ == "__main__":
    main()

