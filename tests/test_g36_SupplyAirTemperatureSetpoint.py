import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *

import pandas as pd
import numpy as np


class TestG36SupplyAirTemperatureSetpointg(unittest.TestCase):
    def test_heating_cooling(self):
        points = [
            "operation_mode",
            "t_max",
            "max_clg_sa_t_sp",
            "min_clg_sa_t_sp",
            "oa_t",
            "oa_t_min",
            "oa_t_max",
            "sa_t_sp_ac",
            "sa_sp_tol",
        ]
        data = [
            ["cooldown", 14, 13, 12, 9, 10, 21, 12, 0.2],  # False
            ["cooldown", 14, 16, 12, 9, 10, 21, 11.9, 0.2],  # True
            ["warmup", 14, 16, 12, 9, 10, 21, 35.1, 0.2],  # True
            ["setback", 14, 16, 12, 9, 10, 21, 34.9, 0.2],  # True
            ["warmup", 14, 16, 12, 9, 10, 21, 32, 0.2],  # False
            ["setback", 14, 16, 12, 9, 10, 21, 42, 0.2],  # False
            ["occupied", 14, 16, 12, 9, 10, 21, 14, 0.2],  # True
            ["occupied", 14, 16, 12, 9, 10, 21, 15, 0.2],  # False
            ["occupied", 14, 16, 12, 22, 10, 21, 11.9, 0.2],  # True
            ["occupied", 14, 16, 12, 22, 10, 21, 15, 0.2],  # False
            ["occupied", 14, 16, 12, 16, 10, 21, 12.9, 0.2],  # True
            ["occupied", 14, 16, 12, 16, 10, 21, 12.5, 0.2],  # False
            ["setup", 14, 16, 12, 9, 10, 21, 14, 0.2],  # True
            ["setup", 14, 16, 12, 9, 10, 21, 15, 0.2],  # False
            ["setup", 14, 16, 12, 22, 10, 21, 11.9, 0.2],  # True
            ["setup", 14, 16, 12, 22, 10, 21, 15, 0.2],  # True
            ["setup", 14, 16, 12, 16, 10, 21, 12.9, 0.2],  # True
            ["setup", 14, 16, 12, 16, 10, 21, 12.5, 0.2],  # False
            ["wrong", 14, 16, 12, 16, 10, 21, 12.5, 0.2],  # Untested
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36SupplyAirTemperatureSetpoint", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                False,
                True,
                True,
                True,
                False,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                np.nan,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
