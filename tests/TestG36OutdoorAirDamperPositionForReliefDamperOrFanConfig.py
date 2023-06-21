import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *

import pandas as pd
import numpy as np


class TestG36OutdoorAirDamperPositionForReliefDamperOrFanConfig(unittest.TestCase):
    def test_return_air_damper_position(self):
        points = [
            "heating_output",
            "cooling_output",
            "ra_p",
            "max_ra_p",
            "ra_p_tol",
            "oa_p",
            "min_oa_p",
            "max_oa_p",
            "oa_p_tol",
            "economizer_high_limit_reached",
        ]
        data = [
            [1000, 0, 1.0, 1.0, 0.05, 0.8, 0.2, 1.0, 0.05, False],  # False
            [1000, 0, 1.0, 1.0, 0.05, 0.2, 0.2, 1.0, 0.05, False],  # True
            [0, 1000, 1.0, 1.0, 0.05, 0.2, 0.2, 1.0, 0.05, False],  # False
            [0, 1000, 1.0, 1.0, 0.05, 0.8, 0.2, 1.0, 0.05, False],  # False
            [0, 1000, 1.0, 1.0, 0.05, 0.98, 0.2, 1.0, 0.05, False],  # True
            [0, 1000, 1.0, 1.0, 0.05, 0.8, 0.2, 1.0, 0.05, True],  # False
            [0, 0, 1.0, 1.0, 0.05, 0.2, 0.2, 1.0, 0.05, False],  # False
            [0, 0, 1.0, 1.0, 0.05, 0.8, 0.2, 1.0, 0.05, False],  # True
            [0, 0, 0, 1.0, 0.05, 0.8, 0.2, 1.0, 0.05, False],  # False
            [0, 0, 0, 1.0, 0.05, 1.0, 0.2, 1.0, 0.05, False],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36OutdoorAirDamperPositionForReliefDamperOrFanConfig", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [False, True, False, False, True, False, False, True, False, True]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
