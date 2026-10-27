#!/usr/bin/env python3

import importlib.util
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "qualification", HERE / "d1_raw_gh_qualification.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def order(coarse, fine, coarse_n, fine_n):
    return math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1))


def levels(values):
    grids = [65, 97, 129, 193, 257, 385, 513]
    return [
        {"grid": [nx, 241], "finite": True, "maximum_normalized": value}
        for nx, value in zip(grids, values)
    ]


def test_frozen_inventory():
    assert MODULE.ANCHOR_NX == 257
    assert MODULE.NEW_NX == (385, 513)
    assert MODULE.NR == 241
    assert MODULE.PERTURB_GRID == (97, 181)
    assert MODULE.PERTURB_STEPS == 8
    assert MODULE.DT == 0.000125


def test_shape_respects_boundaries_and_support():
    x = np.linspace(1.0, math.e, 97)
    r = np.linspace(0.0, 10.0, 181)
    shape = MODULE.perturbation_shape(x, r)
    assert np.count_nonzero(shape[0]) == 0
    assert np.count_nonzero(shape[-1]) == 0
    assert np.count_nonzero(shape[:, r >= 4.0]) == 0
    assert np.max(shape) <= 1.0
    assert np.max(shape) > 0.5
    assert np.all(np.isfinite(shape))


def test_raw_gate_requires_two_consecutive_passes():
    data = levels([1e-2, 2e-3, 7e-4, 1.5e-4, 4e-5, 8e-6, 2e-6])
    gates, _, passing = MODULE.raw_gate(data, order)
    assert all(gates.values())
    assert passing[-2:] == [5, 6]


def test_raw_gate_rejects_only_one_pass():
    data = levels([1e-2, 2e-3, 7e-4, 3e-4, 2e-4, 1.2e-4, 5e-5])
    gates, _, passing = MODULE.raw_gate(data, order)
    assert passing == [6]
    assert not gates["two_consecutive"]


def test_normalized_departure_detects_velocity():
    q = np.ones((2, 3, 9))
    v = np.zeros_like(q)
    v[:, :, 7] = 2e-9
    assert MODULE.normalized_departure(q, v, q) == 2e-9

