#!/usr/bin/env python3
"""Pre-production structural tests for the global uniqueness cover."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from flint import fmpq

import global_uniqueness_cover as cover


class CoverTests(unittest.TestCase):
    def test_exact_dyadic_root_order(self) -> None:
        lo, hi = map(cover.dyadic, cover.CONFIG["root_box_decimal_labels"])
        self.assertLess(fmpq(0), lo)
        self.assertLess(lo, hi)
        self.assertLess(hi, cover.dyadic("0.1"))

    def test_target_width_is_exact(self) -> None:
        self.assertEqual(cover.parse_q(cover.CONFIG["target_launch_width"]), fmpq(1, 65536))

    def test_canonical_json_stable(self) -> None:
        self.assertEqual(cover.canonical_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}\n')

    def test_exact_rational_roundtrip(self) -> None:
        for value in (fmpq(0), fmpq(1, 7), fmpq(3602879701896397, 36028797018963968)):
            self.assertEqual(cover.parse_q(str(value)), value)

    def test_valid_synthetic_cover(self) -> None:
        rows = [
            {"a_exact_bounds": ["0", "1/3"], "classification": "NEGATIVE_CURVATURE_EXCLUDED"},
            {"a_exact_bounds": ["1/3", "2/3"], "classification": "CERTIFIED_D1_UNIQUE_ROOT"},
            {"a_exact_bounds": ["2/3", "1"], "classification": "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED"},
        ]
        audit = cover.coverage_audit(rows, fmpq(0), fmpq(1))
        self.assertTrue(audit["exact_contiguous_cover"])
        self.assertTrue(audit["all_boxes_positive_width"])
        self.assertEqual(audit["certified_root_box_count"], 1)

    def test_gap_detected(self) -> None:
        rows = [
            {"a_exact_bounds": ["0", "1/3"], "classification": "NEGATIVE_CURVATURE_EXCLUDED"},
            {"a_exact_bounds": ["1/2", "1"], "classification": "CERTIFIED_D1_UNIQUE_ROOT"},
        ]
        self.assertFalse(cover.coverage_audit(rows, fmpq(0), fmpq(1))["exact_contiguous_cover"])

    def test_checkpoint_content_address(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            payload = cover.state_payload({"x": "y"}, [(fmpq(0), fmpq(1), 0)], [], [], 0, 0, 0, 0.0)
            first = cover.publish_checkpoint(output, payload)
            second = cover.publish_checkpoint(output, payload)
            self.assertEqual(first, second)
            latest = json.loads((output / "CHECKPOINT.json").read_text())
            self.assertEqual(latest["checkpoint_sha256"], first)

    def test_success_and_unresolved_labels_distinct(self) -> None:
        self.assertNotEqual(cover.SUCCESS_CLASSIFICATION, cover.UNRESOLVED_CLASSIFICATION)


if __name__ == "__main__":
    unittest.main()
