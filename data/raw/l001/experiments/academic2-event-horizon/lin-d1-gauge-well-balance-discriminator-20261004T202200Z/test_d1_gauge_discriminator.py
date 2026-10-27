#!/usr/bin/env python3
"""Outcome-blind contract and reduction tests for the gauge discriminator."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("gauge_target", HERE / "d1_gauge_discriminator.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_frozen_grids_and_gate() -> None:
    assert MODULE.A_GRIDS == ((65, 121), (97, 181), (129, 241))
    assert MODULE.B_NX == (129, 193, 257)
    assert MODULE.B_NR == 241
    assert MODULE.GAUGE_GATE == 5e-5


def test_zero_constraint_summary_is_exact() -> None:
    constraints = np.zeros((3, 4, 5))
    contracted = np.ones_like(constraints)
    sources = np.ones_like(constraints)
    result = MODULE.summarize_constraints(constraints, contracted, sources, np.linspace(0.0, 1.0, 4))
    assert result["maximum_absolute"] == 0.0
    assert result["maximum_local_relative"] == 0.0
    assert result["global_relative"] == 0.0
    assert result["finite"]


def test_constraint_summary_localizes_known_component() -> None:
    constraints = np.zeros((3, 4, 5))
    constraints[1, 2, 4] = 0.25
    contracted = np.ones_like(constraints)
    sources = np.ones_like(constraints)
    result = MODULE.summarize_constraints(constraints, contracted, sources, np.linspace(0.0, 1.0, 4))
    assert result["maximum_index"] == [1, 2]
    assert result["maximum_component"] == 4
    assert math.isclose(result["maximum_absolute"], 0.25)


def test_observed_order() -> None:
    ratio = (257 - 1) / (129 - 1)
    assert math.isclose(MODULE.observed_order(1.0, ratio ** -4, 129, 257), 4.0, abs_tol=1e-14)
    assert MODULE.observed_order(1.0, 1.0, 129, 257) is None

