#!/usr/bin/env python3
"""Technical adapter and immutable launcher for the frozen D1 wall test."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compatible_stage_source_class(base_class):
    class CompatibleStageRegularGaugeSource(base_class):
        """Expose legacy zero-time diagnostic names without changing `at`."""

        def __init__(self, source, source_time, z, r, stencil_width=7):
            super().__init__(source, source_time, z, r, stencil_width)
            self.source_time_reduced = np.asarray(self.source_time, dtype=float)
            self.source_time_z = np.zeros_like(self.source_time_reduced)
            self.source_time_r = np.zeros_like(self.source_time_reduced)

    CompatibleStageRegularGaugeSource.__name__ = "CompatibleStageRegularGaugeSource"
    return CompatibleStageRegularGaugeSource


def argument_value(name: str) -> Path:
    try:
        return Path(sys.argv[sys.argv.index(name) + 1]).resolve()
    except (ValueError, IndexError) as error:
        raise RuntimeError(f"missing required launcher argument {name}") from error


def main() -> None:
    root = argument_value("--root")
    source_root = root / "branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src"
    sys.path.insert(0, str(source_root))
    import bhps.nonlinear_regular_so3_evolution as evolution

    original_stage_class = evolution.StageRegularGaugeSource
    evolution.StageRegularGaugeSource = compatible_stage_source_class(original_stage_class)

    parent_path = root / "branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-20261004T200437Z/d1_wall_discriminator.py"
    parent = import_file("d1_wall_discriminator_r1_parent", parent_path)
    # Make the frozen parent main authenticate the R1 contract and bindings.
    parent.__file__ = str(Path(__file__).resolve())
    parent.main()


if __name__ == "__main__":
    main()

