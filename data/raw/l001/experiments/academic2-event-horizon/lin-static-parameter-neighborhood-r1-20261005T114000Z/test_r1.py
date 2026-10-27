#!/usr/bin/env python3

from __future__ import annotations

import unittest
import copy

import r1_runner as r1
from flint import fmpq


class R1ContractTests(unittest.TestCase):
    def test_half_width_exact(self):
        lo, hi = r1.base.qpair(r1.CONFIG["root_box"])
        center = r1.base.parse_q(r1.CONFIG["root_center"])
        self.assertEqual(center - lo, fmpq(1, 50_000_000))
        self.assertEqual(hi - center, fmpq(1, 50_000_000))

    def test_only_intended_base_config_changes(self):
        old = copy.deepcopy(r1.CONFIG)
        old["schema"] = "lin-static-parameter-neighborhood-config-v1"
        old["root_box"] = [
            "222948145784121/2251799813685248",
            "891828611933503/9007199254740992",
        ]
        old.pop("root_tube_half_width_exact")
        old.pop("root_tube_design_basis")
        self.assertEqual(old, r1.BASE_CONFIG)

    def test_subdivision_rule_unchanged(self):
        self.assertEqual(r1.CONFIG["maximum_parameter_subdivision_depth"], 2)
        self.assertEqual(r1.CONFIG["parameter_split_axes"], ["v1", "lambda_b"])


if __name__ == "__main__":
    unittest.main()
