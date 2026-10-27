#!/usr/bin/env python3
"""Outcome-blind algebra and contract tests for the D1 wall discriminator."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("d1_wall_test_target", HERE / "d1_wall_discriminator.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def polynomial_derivative_matrix(x: np.ndarray, order: int, width: int):
    assert order == 1
    matrix = np.empty((len(x), len(x)))
    for index in range(len(x)):
        offsets = x - x[index]
        vandermonde = np.vstack([offsets ** power for power in range(len(x))])
        target = np.zeros(len(x))
        target[1] = 1.0
        matrix[index] = np.linalg.solve(vandermonde, target)
    return matrix


def background() -> dict[str, float]:
    return {
        "wall_stiffness": 2.0,
        "v0": 0.1,
        "v1": -0.2,
        "beta_a": 0.03,
        "beta_b": -0.04,
        "wall_potential_a": 0.0,
        "wall_potential_b": 0.0,
    }


def synthetic_position() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = np.linspace(1.0, 2.0, 7)
    r = np.linspace(0.0, 1.0, 5)
    q = np.zeros((len(z), len(r), 9))
    q[:, :, 2] = -(1.0 + 0.1 * z[:, None])
    q[:, :, 3] = 1.0 + 0.2 * z[:, None]
    q[:, :, 4] = 0.01
    q[:, :, 6] = 1.5 + 0.05 * z[:, None]
    q[:, :, 7] = 0.02 * z[:, None]
    return q, z, r


def test_frozen_contract() -> None:
    assert MODULE.A_GRIDS == ((65, 121), (97, 181), (129, 241))
    assert MODULE.B_NX == (129, 193, 257, 385, 513)
    assert MODULE.B_NR == 241
    assert MODULE.GATES["wall"] == 2e-6
    assert MODULE.GATES["wall_any"] == 2e-5


def test_background_subtraction_is_exactly_zero() -> None:
    q, z, r = synthetic_position()
    record = MODULE.summarize_wall_difference(
        q, q, z, r, background(), polynomial_derivative_matrix, 0,
    )
    assert record["maximum"] == 0.0
    for wall in record["walls"]:
        assert all(value == 0.0 for value in wall["rows"].values())


def test_generic_departure_is_not_projected_away() -> None:
    q, z, r = synthetic_position()
    candidate = q.copy()
    candidate[:, :, 3] += 1e-6 * np.sin(math.pi * (z[:, None] - 1.0))
    record = MODULE.summarize_wall_difference(
        candidate, q, z, r, background(), polynomial_derivative_matrix, 0,
    )
    assert np.isfinite(record["maximum"])
    assert record["maximum"] > 1e-12


def test_observed_order() -> None:
    ratio = (513 - 1) / (257 - 1)
    assert math.isclose(MODULE.observed_order(1.0, ratio ** -4, 257, 513), 4.0, abs_tol=1e-14)
    assert MODULE.observed_order(0.0, 1.0, 257, 513) is None


def test_wall_coefficients_follow_frozen_signs() -> None:
    phi = np.asarray([0.2])
    bg = background()
    lower_target, lower_beta = MODULE.wall_coefficients(phi, bg, False)
    upper_target, upper_beta = MODULE.wall_coefficients(phi, bg, True)
    assert lower_target == bg["v0"]
    assert upper_target == bg["v1"]
    assert np.allclose(lower_beta, bg["beta_a"] + 0.5 * bg["wall_stiffness"] * (phi - bg["v0"]) ** 2 / 6.0)
    assert np.allclose(upper_beta, bg["beta_b"] - 0.5 * bg["wall_stiffness"] * (phi - bg["v1"]) ** 2 / 6.0)

