import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *


class TestHPWHSizing(unittest.TestCase):
    def test_HPWH_sizing(self):
        points = [
            "T_amb",
            "HeatingRate_dx_coil",
            "HeatingRate_waterheater1",
            "HeatingRate_waterheater2",
            "T_amb_parameter",
        ]

        data = [
            [3.0, 0, 0, 0, 3.7],  # untested - when T_amb <= T_amb_parameter,
            [0, 0, 0, 0, 0],  # untested - when total_hpwh_load == 0
            [
                5.0,
                30,
                0,
                0,
                3.7,
            ],  # pass - when `HeatingRate_dx_coil` can meet all the load
            [
                5.0,
                30,
                0,
                20,
                3.7,
            ],  # fail - when `HeatingRate_dx_coil` cannot meet all the load
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data("HPWH_sizing", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(["untested", "untested", True, False])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
