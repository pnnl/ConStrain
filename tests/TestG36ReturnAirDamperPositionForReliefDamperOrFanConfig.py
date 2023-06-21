import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReturnAirDamperPositionForReliefDamperOrFanConfig(unittest.TestCase):
    def test_return_air_damper_positiong(self):
        points = [
            "heating_output",
            "cooling_output",
            "ra_p",
            "max_ra_p",
            "ra_p_tol",
            "oa_p",
            "max_oa_p",
            "oa_p_tol",
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
            "G36ReturnAirDamperPositionForReliefDamperOrFanConfig", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [False, True, False, True, False, True, False, True]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
