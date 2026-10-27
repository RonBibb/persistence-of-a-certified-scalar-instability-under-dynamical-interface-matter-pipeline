#!/usr/bin/env python3
"""Fast contract tests for the parameter-neighborhood runner."""

from __future__ import annotations

import unittest

import parameter_neighborhood as pn
from flint import fmpq


class ParameterNeighborhoodTests(unittest.TestCase):
    def aggregate(self):
        return pn.parameter_cell(
            0,
            pn.qpair(pn.CONFIG["parameter_box"]["v1"]),
            pn.qpair(pn.CONFIG["parameter_box"]["lambda_b"]),
        )

    def test_root_center_strictly_inside(self):
        lo, hi = pn.qpair(pn.CONFIG["root_box"])
        center = pn.parse_q(pn.CONFIG["root_center"])
        self.assertLess(lo, center)
        self.assertLess(center, hi)

    def test_first_split_is_v1_and_exact(self):
        parent = self.aggregate()
        children = pn.split_parameter_cell(parent)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0]["lambda_b"], parent["lambda_b"])
        self.assertEqual(children[1]["lambda_b"], parent["lambda_b"])
        self.assertEqual(children[0]["v1"][0], parent["v1"][0])
        self.assertEqual(children[0]["v1"][1], children[1]["v1"][0])
        self.assertEqual(children[1]["v1"][1], parent["v1"][1])
        self.assertEqual(sum((pn.parameter_volume(c) for c in children), fmpq(0)), pn.parameter_volume(parent))

    def test_second_split_is_lambda_b_and_exact(self):
        first = pn.split_parameter_cell(self.aggregate())[0]
        children = pn.split_parameter_cell(first)
        self.assertEqual(children[0]["v1"], first["v1"])
        self.assertEqual(children[1]["v1"], first["v1"])
        self.assertEqual(children[0]["lambda_b"][1], children[1]["lambda_b"][0])
        self.assertEqual(sum((pn.parameter_volume(c) for c in children), fmpq(0)), pn.parameter_volume(first))

    def test_distance_from_zero(self):
        self.assertEqual(pn.distance_from_zero((fmpq(2), fmpq(3))), fmpq(2))
        self.assertEqual(pn.distance_from_zero((fmpq(-3), fmpq(-2))), fmpq(2))
        self.assertEqual(pn.distance_from_zero((fmpq(-1), fmpq(1))), fmpq(0))

    def test_launch_coverage(self):
        rows = [
            {"a_exact_bounds": ["0", "1/4"], "classification": "NEGATIVE_CURVATURE_EXCLUDED"},
            {"a_exact_bounds": ["1/4", "1/2"], "classification": "CERTIFIED_PARAMETRIC_ROOT_CONTAINER"},
            {"a_exact_bounds": ["1/2", "1"], "classification": "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED"},
        ]
        audit = pn.launch_coverage(rows, fmpq(1))
        self.assertTrue(audit["exact_contiguous_cover"])
        self.assertTrue(audit["all_boxes_positive_width"])
        self.assertEqual(audit["certified_root_box_count"], 1)

    def test_parameter_faces(self):
        self.assertEqual(
            set(pn.cell_faces(self.aggregate())),
            {"v1_lower", "v1_upper", "lambda_b_lower", "lambda_b_upper"},
        )

    def test_checkpoint_payload_is_deterministic(self):
        guard = {"x": "y"}
        state = {"pending_cells": [self.aggregate()], "current": None}
        first = pn.sha256_bytes(pn.canonical_bytes(pn.checkpoint_payload(guard, state)))
        second = pn.sha256_bytes(pn.canonical_bytes(pn.checkpoint_payload(guard, state)))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
