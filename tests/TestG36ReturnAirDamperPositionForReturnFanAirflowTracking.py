import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReturnAirDamperPositionForReturnFanAirflowTracking(unittest.TestCase):
    def test_return_air_damper_positiong(self):
        points = [
            "heating_output",
            "cooling_output",
            "ra_p",
            "max_ra_p",
            "ra_p_tol",
            "rea_p",
        ]
        data = [
            [1000, 0, 0.5, 1.0, 0.05, 1.0],  # False
            [1000, 0, 1.0, 1.0, 0.05, 1.0],  # True
            [0, 1000, 1.0, 1.0, 0.05, 1.0],  # False
            [0, 1000, 0.01, 1.0, 0.05, 1.0],  # True
            [0, 0, 0.5, 1.0, 0.05, 0.5],  # True
            [0, 0, 0.3, 1.0, 0.05, 0.4],  # False
            [0, 0, 0.17, 1.0, 0.05, 0.8],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36ReturnAirDamperPositionForReturnFanAirflowTracking", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([False, True, False, True, True, False, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
