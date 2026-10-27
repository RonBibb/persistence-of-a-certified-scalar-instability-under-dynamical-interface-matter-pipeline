#!/usr/bin/env python3

import importlib.util
import json
import os
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
R1 = HERE.parent / "lin-d1-raw-gh-dynamical-qualification-r1-roundoff-audit-20261005T003908Z"
SPEC = importlib.util.spec_from_file_location("frozen_roundoff_audit", R1 / "roundoff_audit.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import frozen R1 audit")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


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


if __name__ == "__main__":
    MODULE.main()
