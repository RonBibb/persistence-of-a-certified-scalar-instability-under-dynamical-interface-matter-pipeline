#!/usr/bin/env python3
"""Outcome-blind tests for the source-time compatibility adapter."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r1_adapter", HERE / "d1_wall_discriminator_r1.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeStage:
    def __init__(self, source, source_time, z, r, stencil_width=7):
        self.source = np.asarray(source)
        self.source_time = np.asarray(source_time)
        self.z = np.asarray(z)
        self.r = np.asarray(r)
        self.stencil_width = stencil_width

    def at(self, i, j, time=0.0):
        return self.source[i, j] + time * self.source_time[i, j]


def test_adapter_exposes_exact_zero_time_diagnostics() -> None:
    source = np.ones((3, 4, 3))
    source_time = np.zeros_like(source)
    compatible = MODULE.compatible_stage_source_class(FakeStage)
    instance = compatible(source, source_time, np.arange(3.0), np.arange(4.0), 7)
    assert np.array_equal(instance.source_time_reduced, source_time)
    assert np.count_nonzero(instance.source_time_z) == 0
    assert np.count_nonzero(instance.source_time_r) == 0


def test_adapter_does_not_change_public_stage_evaluation() -> None:
    source = np.arange(36.0).reshape(3, 4, 3)
    source_time = np.full_like(source, 0.25)
    base = FakeStage(source, source_time, np.arange(3.0), np.arange(4.0), 7)
    compatible = MODULE.compatible_stage_source_class(FakeStage)(
        source, source_time, np.arange(3.0), np.arange(4.0), 7
    )
    assert np.array_equal(base.at(1, 2, 0.5), compatible.at(1, 2, 0.5))

