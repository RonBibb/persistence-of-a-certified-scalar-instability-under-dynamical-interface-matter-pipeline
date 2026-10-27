import math
import unittest

import numpy as np

import d1_background_admission as subject


class AlgebraControls(unittest.TestCase):
    def test_launch_satisfies_lower_rows(self):
        for value in (subject.ROOT_LO, 0.5 * (subject.ROOT_LO + subject.ROOT_HI), subject.ROOT_HI):
            state, curvature = subject.launch(value)
            self.assertGreater(curvature, 0.0)
            self.assertAlmostEqual(
                state[1] + (subject.LAMBDA_A + 0.5 * subject.GAMMA * (value - subject.V0) ** 2) / 6.0,
                0.0, places=15,
            )
            self.assertAlmostEqual(state[3] - 0.5 * subject.GAMMA * (value - subject.V0), 0.0, places=15)

    def test_represented_field_formulas(self):
        def sample(x):
            x = np.asarray(x)
            return {
                "A": np.zeros_like(x), "H": -np.ones_like(x),
                "phi": np.full_like(x, 0.1), "U": np.zeros_like(x),
                "s": x - 1.0, "w": np.ones_like(x),
            }

        fields = subject.represented_fields(9, 11, sample, 1e-4, 2.0)
        self.assertEqual(fields["q"].shape, (9, 11, 9))
        self.assertTrue(np.all(fields["f"] > 0.0))
        self.assertTrue(np.allclose(fields["q"][:, :, 6], 4.0))
        self.assertTrue(np.allclose(fields["source"][:, :, 1], 6.0))

    def test_gates_are_prospective_literals(self):
        self.assertEqual(subject.ADMISSION_GRIDS, ((65, 121), (97, 181), (129, 241)))
        self.assertEqual(subject.EVOLUTION_GRIDS, ((49, 91), (65, 121)))
        self.assertEqual(subject.STEPS, 4)
        self.assertEqual(subject.DT, 0.000125)
        self.assertEqual(subject.GATES["hamiltonian_full_finest"], 2e-6)


if __name__ == "__main__":
    unittest.main()
