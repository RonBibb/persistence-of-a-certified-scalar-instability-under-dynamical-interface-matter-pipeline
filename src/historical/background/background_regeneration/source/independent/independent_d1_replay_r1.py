#!/usr/bin/env python3
"""R1 refinement wrapper for the frozen producer-independent D1 engine."""

import independent_d1_replay as replay


replay.STEP_COUNTS = (8192, 16384)


if __name__ == "__main__":
    replay.main()

