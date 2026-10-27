#!/usr/bin/env python3

import importlib.util
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("adapter", HERE / "run_verifier_adapter.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_numpy_scalar_writer(tmp_path):
    path = tmp_path / "audit.json"
    MODULE.atomic_json(path, {"ok": np.bool_(True), "value": np.float64(1.25)})
    assert json.loads(path.read_text()) == {"ok": True, "value": 1.25}

