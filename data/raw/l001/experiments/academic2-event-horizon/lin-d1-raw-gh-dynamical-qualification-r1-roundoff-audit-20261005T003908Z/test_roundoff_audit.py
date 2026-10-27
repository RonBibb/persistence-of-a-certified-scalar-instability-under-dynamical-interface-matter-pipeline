#!/usr/bin/env python3

import importlib.util
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("audit", HERE / "roundoff_audit.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_declared_roundoff_allowance_exceeds_one_ulp():
    allowance = 8.0 * np.finfo(np.float64).eps
    assert allowance > np.spacing(1.0)
    assert allowance < 1e-14


def test_binary64_add_subtract_can_overshoot_declared_increment():
    background = np.asarray([0.1], dtype=np.float64)
    stored = background + MODULE.EPSILON
    measured = float(np.max(np.abs(stored - background)))
    allowance = 8.0 * np.finfo(np.float64).eps
    assert measured <= MODULE.EPSILON + allowance

