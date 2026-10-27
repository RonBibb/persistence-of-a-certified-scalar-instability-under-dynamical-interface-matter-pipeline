#!/usr/bin/env python3
"""Outcome-blind contract and algebra tests for the D1 discriminator."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "d1_curvature_discriminator_under_test", HERE / "d1_curvature_discriminator.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_frozen_grid_contract() -> None:
    assert MODULE.A_GRIDS == ((65, 121), (97, 181), (129, 241))
    assert MODULE.B_NX == (257, 513, 1025, 1537, 2049)
    assert MODULE.B_NR == 241
    assert MODULE.STENCIL == 7


def test_frozen_gate_contract() -> None:
    assert MODULE.GATES == {
        "hamiltonian_full": 2e-6,
        "hamiltonian_interior": 5e-7,
        "wall": 2e-6,
        "wall_any": 2e-5,
        "axis": 5e-12,
        "gauge": 5e-5,
        "source": 1e-12,
        "outer": 1e-12,
        "adm_acceleration": 5e-5,
        "gh_acceleration": 1e-4,
    }


def test_observed_order_on_exact_fourth_order_pair() -> None:
    coarse_n, fine_n = 257, 513
    ratio = (fine_n - 1) / (coarse_n - 1)
    assert math.isclose(
        MODULE.observed_order(1.0, ratio ** -4, coarse_n, fine_n),
        4.0,
        rel_tol=0.0,
        abs_tol=1e-14,
    )


def test_observed_order_rejects_zero_and_equal_values() -> None:
    assert MODULE.observed_order(0.0, 1.0, 5, 9) is None
    assert MODULE.observed_order(1.0, 0.0, 5, 9) is None
    assert MODULE.observed_order(1.0, 1.0, 5, 9) is None


def test_exact_geometry_matches_frozen_continuum_identities() -> None:
    profile = {
        "w": np.asarray([2.0, 4.0]),
        "H": np.asarray([0.25, -0.5]),
        "U": np.asarray([0.3, -0.6]),
    }
    shape = (2, 3)
    r = np.asarray([0.0, 0.5, 1.0])
    q = np.zeros((*shape, 9))
    q[:, :, 6] = 3.0
    q[:, :, 3] = 5.0
    q[:, :, 4] = 0.2
    fields = {
        "profile": profile,
        "psi": np.ones(shape),
        "q": q,
        "r": r,
    }
    k = 0.02
    exact = MODULE.exact_geometry(fields, {"k": k})
    hs = -profile["U"] ** 2 / 3.0 - k / profile["w"] ** 2
    compact = -3.0 * (hs + profile["H"] ** 2)
    brane = 2.0 * k / profile["w"] ** 2 - hs - 3.0 * profile["H"] ** 2
    compact_grid = np.broadcast_to(compact[:, None], shape)
    brane_grid = np.broadcast_to(brane[:, None], shape)
    np.testing.assert_allclose(exact["compact_contribution"], compact_grid)
    np.testing.assert_allclose(exact["radial_contribution"], brane_grid)
    np.testing.assert_allclose(exact["transverse_contribution"], brane_grid)
    np.testing.assert_allclose(
        exact["scalar_curvature"], np.broadcast_to((compact + 3.0 * brane)[:, None], shape)
    )
    np.testing.assert_allclose(exact["ricci_zz"], compact_grid * 3.0)
    radial_metric = 5.0 + r[None, :] ** 2 * 0.2
    np.testing.assert_allclose(exact["ricci_radial"], brane_grid * radial_metric)
    np.testing.assert_allclose(exact["ricci_transverse"], brane_grid * 5.0)
    assert np.count_nonzero(exact["ricci_zr"]) == 0


def test_arm_orders_preserves_declared_resolution_pairs() -> None:
    levels = [
        {"grid": [257, 241], "hamiltonian_full": 16.0, "hamiltonian_interior": 8.0},
        {"grid": [513, 241], "hamiltonian_full": 1.0, "hamiltonian_interior": 0.5},
    ]
    record = MODULE.arm_orders(levels)
    assert record[0]["from_Nx"] == 257
    assert record[0]["to_Nx"] == 513
    assert math.isclose(record[0]["full_order"], 4.0)
    assert math.isclose(record[0]["interior_order"], 4.0)
