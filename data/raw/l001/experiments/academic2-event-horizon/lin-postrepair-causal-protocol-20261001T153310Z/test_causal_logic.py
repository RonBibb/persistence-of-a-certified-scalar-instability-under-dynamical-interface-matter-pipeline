import itertools
import json
from pathlib import Path
import unittest

from causal_logic import BracketStatus, Evidence, TerminalStatus, classify


class CausalLogicTests(unittest.TestCase):
    def test_unqualified_companion_blocks_everything(self):
        e = Evidence(
            False,
            TerminalStatus.LOCALIZED,
            BracketStatus.CERTIFIED,
            True,
            True,
            True,
        )
        self.assertEqual(classify(e), "BLOCKED-UNQUALIFIED-COMPANION")

    def test_terminal_only_never_authorizes_horizon(self):
        e = Evidence(True, TerminalStatus.LOCALIZED, BracketStatus.ABSENT)
        self.assertEqual(
            classify(e),
            "REPRESENTED-TERMINAL-LOCALIZATION__CAUSAL-IDENTITY-UNRESOLVED",
        )

    def test_bracket_survives_bad_terminal_estimator(self):
        e = Evidence(True, TerminalStatus.NOT_LOCALIZED, BracketStatus.CERTIFIED)
        self.assertEqual(
            classify(e),
            "CERTIFIED-END-RELATIVE-HORIZON-BRACKET__TERMINAL-ESTIMATOR-NOT-LOCALIZED",
        )

    def test_location_needs_both_lanes_and_identification(self):
        e = Evidence(
            True,
            TerminalStatus.LOCALIZED,
            BracketStatus.CERTIFIED,
            True,
            True,
            True,
            bracket_meets_physical_target=True,
        )
        self.assertEqual(
            classify(e),
            "TERMINAL-FRONT-LOCATOR-SUPPORTED-WITHIN-CERTIFIED-BRACKET-ATLAS",
        )

    def test_unresolved_bracket_width_cannot_locate_front(self):
        e = Evidence(
            True,
            TerminalStatus.LOCALIZED,
            BracketStatus.CERTIFIED,
            True,
            True,
            True,
            bracket_meets_physical_target=False,
        )
        self.assertIn("BRACKET-ATLAS__FRONT-IDENTITY-NOT-ESTABLISHED", classify(e))

    def test_single_intersection_bracket_cannot_locate_full_front(self):
        e = Evidence(
            True,
            TerminalStatus.LOCALIZED,
            BracketStatus.CERTIFIED,
            False,
            True,
            True,
        )
        self.assertIn("INTERSECTION-BRACKET__FRONT-IDENTITY-UNRESOLVED", classify(e))

    def test_no_heldout_terminal_no_location(self):
        e = Evidence(True, TerminalStatus.LOCALIZED, BracketStatus.CERTIFIED, True, True, False)
        self.assertIn("BRACKET-ATLAS__FRONT-IDENTITY-NOT-ESTABLISHED", classify(e))

    def test_front_outside_bracket_no_location(self):
        e = Evidence(True, TerminalStatus.LOCALIZED, BracketStatus.CERTIFIED, True, False, True)
        self.assertIn("BRACKET-ATLAS__FRONT-IDENTITY-NOT-ESTABLISHED", classify(e))

    def test_numerical_witness_is_not_certified_bracket(self):
        e = Evidence(True, TerminalStatus.NOT_LOCALIZED, BracketStatus.NUMERICAL_CANDIDATE)
        self.assertEqual(classify(e), "NO-CAUSAL-CONCLUSION")

    def test_later_ray_entry_cannot_certify_launch_capture(self):
        e = Evidence(
            True,
            TerminalStatus.LOCALIZED,
            BracketStatus.CERTIFIED,
            True,
            True,
            True,
            capture_is_only_later_ray_entry=True,
        )
        self.assertIn("CAUSAL-IDENTITY-UNRESOLVED", classify(e))

    def test_finite_wall_substitution_fails_closed(self):
        e = Evidence(
            True,
            TerminalStatus.LOCALIZED,
            BracketStatus.CERTIFIED,
            True,
            True,
            True,
            finite_wall_used_as_exterior_without_authority=True,
        )
        self.assertEqual(classify(e), "INVALID-EXTERIOR-AUTHORITY")

    def test_cross_lineage_bracket_fails_closed(self):
        e = Evidence(
            True,
            TerminalStatus.NOT_LOCALIZED,
            BracketStatus.CERTIFIED,
            same_development=False,
        )
        self.assertEqual(classify(e), "INVALID-CROSS-LINEAGE-OR-EXTERIOR-BRACKET")

    def test_different_exterior_bracket_fails_closed(self):
        e = Evidence(
            True,
            TerminalStatus.NOT_LOCALIZED,
            BracketStatus.CERTIFIED,
            same_exterior=False,
        )
        self.assertEqual(classify(e), "INVALID-CROSS-LINEAGE-OR-EXTERIOR-BRACKET")

    def test_reviewed_causal_past_equality_allows_end_transfer(self):
        e = Evidence(
            True,
            TerminalStatus.NOT_LOCALIZED,
            BracketStatus.CERTIFIED,
            same_exterior=False,
            causal_past_equality_authorized=True,
        )
        self.assertEqual(
            classify(e),
            "CERTIFIED-END-RELATIVE-HORIZON-BRACKET__TERMINAL-ESTIMATOR-NOT-LOCALIZED",
        )

    def test_incomplete_terminal_does_not_erase_certified_bracket(self):
        e = Evidence(True, TerminalStatus.INCOMPLETE, BracketStatus.CERTIFIED)
        self.assertEqual(
            classify(e),
            "CERTIFIED-END-RELATIVE-HORIZON-BRACKET__TERMINAL-ESTIMATOR-INCOMPLETE",
        )

    def test_all_decision_outputs_are_declared(self):
        declared = set(
            json.loads((Path(__file__).with_name("PORTABLE_CONTRACT.json")).read_text())[
                "outcomes"
            ]
        )
        for values in itertools.product(
            (False, True),
            tuple(TerminalStatus),
            tuple(BracketStatus),
            (False, True),
            (False, True),
            (False, True),
            (False, True),
            (False, True),
            (False, True),
            (False, True),
            (False, True),
            (False, True),
        ):
            self.assertIn(classify(Evidence(*values)), declared)


if __name__ == "__main__":
    unittest.main()
