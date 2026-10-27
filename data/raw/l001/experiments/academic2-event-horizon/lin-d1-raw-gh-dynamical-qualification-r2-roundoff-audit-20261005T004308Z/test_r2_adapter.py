#!/usr/bin/env python3

import importlib.util
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r2", HERE / "run_r2.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_numpy_boolean_serializes(tmp_path):
    path = tmp_path / "value.json"
    MODULE.atomic_json(path, {"value": np.bool_(True)})
    assert json.loads(path.read_text()) == {"value": True}

