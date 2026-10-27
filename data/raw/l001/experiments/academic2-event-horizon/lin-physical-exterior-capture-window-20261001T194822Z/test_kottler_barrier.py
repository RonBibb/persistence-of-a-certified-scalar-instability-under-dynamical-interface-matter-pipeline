from __future__ import annotations

import dataclasses
import itertools
import unittest

import mpmath as mp

from kottler_barrier import (
    BracketAuthority,
    barrier_expansion,
    barrier_remainder,
    candidate_curvature,
    cap_expansions,
    classify_authority,
    horizon_roots,
    horizon_surface_gravity,
    lapse_function,
    normalized_barrier_expansion,
    outgoing_arrival_time,
    tau_slice_bracket_width,
)


class KottlerGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mp.mp.dps = 70
        cls.mass = mp.mpf("1")
        cls.curvature = candidate_curvature()
        cls.rb, cls.rc = horizon_roots(cls.mass, cls.curvature)

    def test_sub_nariai(self) -> None:
        self.assertLess(27 * self.curvature * self.mass**2, 1)

    def test_two_positive_roots(self) -> None:
        self.assertLess(abs(lapse_function(self.rb, self.mass, self.curvature)), mp.mpf("1e-55"))
        self.assertLess(abs(lapse_function(self.rc, self.mass, self.curvature)), mp.mpf("1e-55"))
        self.assertLess(self.rb, self.rc)

    def test_black_hole_surface_gravity_positive(self) -> None:
        kappa = horizon_surface_gravity(self.rb, self.mass, self.curvature)
        self.assertGreater(kappa, 0)
        self.assertLess(abs(kappa - mp.mpf("0.2486904891542565175810500943792")), mp.mpf("1e-31"))

    def test_reference_radii_order(self) -> None:
        self.assertLess(mp.mpf("1.5"), self.rb)
        self.assertLess(self.rb, mp.mpf("4"))
        self.assertLess(mp.mpf("4"), mp.mpf("8"))
        self.assertLess(mp.mpf("8"), self.rc)

    def test_cap_is_future_trapped(self) -> None:
        outgoing, ingoing = cap_expansions(mp.mpf("1.5"), self.mass, self.curvature)
        self.assertLess(outgoing, 0)
        self.assertLess(ingoing, 0)

    def test_full_barrier_remainder_vanishes(self) -> None:
        self.assertEqual(barrier_remainder(), 0)
        self.assertEqual(normalized_barrier_expansion(mp.mpf("8")), mp.mpf("0.25"))

    def test_barrier_is_strictly_outgoing(self) -> None:
        theta = barrier_expansion(
            mp.mpf("8"), self.mass, self.curvature, mp.mpf("1")
        )
        self.assertGreater(theta, mp.mpf("0.21"))

    def test_visible_curve_reaches_barrier_in_finite_time(self) -> None:
        delta_v = outgoing_arrival_time(
            mp.mpf("4"), mp.mpf("8"), self.mass, self.curvature
        )
        self.assertTrue(mp.isfinite(delta_v))
        self.assertGreater(delta_v, 0)
        self.assertLess(delta_v, 13)

    def test_physical_bracket_width_shrinks(self) -> None:
        wide = tau_slice_bracket_width(
            self.rb - mp.mpf("0.01"),
            self.rb + mp.mpf("0.01"),
            self.mass,
            self.curvature,
            mp.mpf("1"),
        )
        narrow = tau_slice_bracket_width(
            self.rb - mp.mpf("0.001"),
            self.rb + mp.mpf("0.001"),
            self.mass,
            self.curvature,
            mp.mpf("1"),
        )
        self.assertLess(abs(wide - mp.mpf("0.0282843227305378556918589726423")), mp.mpf("1e-30"))
        self.assertLess(narrow, wide / 9)

    def test_invalid_barrier_outside_static_region_fails(self) -> None:
        with self.assertRaises(ValueError):
            barrier_expansion(self.rc + 1, self.mass, self.curvature, mp.mpf("1"))


class AuthorityLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.complete = BracketAuthority(*([True] * 13))

    def test_complete_exact_control_qualifies_one_bracket(self) -> None:
        self.assertEqual(
            classify_authority(self.complete),
            "ONE-CENTRAL-END-RELATIVE-BRACKET-QUALIFIED",
        )

    def test_numerical_background_candidate_stays_conditional(self) -> None:
        case = dataclasses.replace(self.complete, background_exact=False)
        self.assertEqual(classify_authority(case), "CONDITIONAL-MODEL-CONTROL-ONLY")

    def test_missing_causal_closedness_blocks_capture(self) -> None:
        case = dataclasses.replace(self.complete, closed_causal_future=False)
        self.assertEqual(classify_authority(case), "CAPTURE-AUTHORITY-INCOMPLETE")

    def test_missing_all_future_sign_blocks_capture(self) -> None:
        case = dataclasses.replace(self.complete, barrier_all_future_positive=False)
        self.assertEqual(classify_authority(case), "CAPTURE-AUTHORITY-INCOMPLETE")

    def test_missing_outer_end_transfer_fails_closed(self) -> None:
        case = dataclasses.replace(self.complete, exterior_causal_past_equality_proved=False)
        self.assertEqual(classify_authority(case), "OUTER-END-TRANSFER-INCOMPLETE")

    def test_discrete_ray_is_not_visible_authority(self) -> None:
        case = dataclasses.replace(self.complete, visible_continuum_curve_enclosed=False)
        self.assertEqual(classify_authority(case), "VISIBLE-ENDPOINT-INCOMPLETE")

    def test_mixed_exterior_ids_do_not_bracket(self) -> None:
        case = dataclasses.replace(self.complete, common_exterior_id=False)
        self.assertEqual(classify_authority(case), "CENTRAL-BRACKET-INCOMPLETE")

    def test_disconnected_endpoints_do_not_bracket(self) -> None:
        case = dataclasses.replace(self.complete, connected_launch_curve=False)
        self.assertEqual(classify_authority(case), "CENTRAL-BRACKET-INCOMPLETE")

    def test_only_complete_exact_authority_qualifies(self) -> None:
        field_names = [field.name for field in dataclasses.fields(BracketAuthority)]
        qualified = 0
        for bits in itertools.product((False, True), repeat=len(field_names)):
            case = BracketAuthority(**dict(zip(field_names, bits, strict=True)))
            result = classify_authority(case)
            if result == "ONE-CENTRAL-END-RELATIVE-BRACKET-QUALIFIED":
                qualified += 1
                self.assertTrue(all(bits))
        self.assertEqual(qualified, 1)


if __name__ == "__main__":
    unittest.main()
