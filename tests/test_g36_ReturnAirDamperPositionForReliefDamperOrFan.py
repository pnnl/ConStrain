import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36ReturnAirDamperPositionForReliefDamperOrFan(unittest.TestCase):
    def test_return_air_damper_position(self):
        points = [
            "q_heat",
            "q_cool",
            "pos_damper_ra",
            "pos_damper_ra_max",
            "tol_pos_damper_ra",
            "pos_damper_oa",
            "pos_damper_oa_max",
            "tol_pos_damper_oa",
        ]
        data = [
            [1000, 0, 0.5, 1.0, 0.05, 0.2, 1.0, 0.05],  # False
            [1000, 0, 1.0, 1.0, 0.05, 0.2, 1.0, 0.05],  # True
            [0, 1000, 0.5, 1.0, 0.05, 0.2, 1.0, 0.05],  # False
            [0, 1000, 0.02, 1.0, 0.05, 0.2, 1.0, 0.05],  # True
            [0, 0, 0.5, 1.0, 0.05, 0.2, 1.0, 0.05],  # False
            [0, 0, 1.0, 1.0, 0.05, 0.2, 1.0, 0.05],  # True
            [0, 0, 1.0, 1.0, 0.05, 1.0, 1.0, 0.05],  # False
            [0, 0, 0.5, 1.0, 0.05, 1.0, 1.0, 0.05],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36ReturnAirDamperPositionForReliefDamperOrFan", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [False, True, False, True, False, True, False, True]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
