import sys
import unittest

sys.path.append("./constrain")
import datetime

import pandas as pd
from lib_unit_test_runner import *


class TestHPWHSizing(unittest.TestCase):
    def test_HPWH_sizing_pass(self):
        points = [
            "T_amb",
            "HeatingRate_dx_coil",
            "HeatingRate_waterheater1",
            "HeatingRate_waterheater2",
            "T_amb_parameter",
            "HPWH_output_target_percent",
        ]

        timestamp = [
            datetime(2024, 1, 1, 12, 0, 0),
            datetime(2024, 1, 1, 13, 0, 0),
            datetime(2024, 1, 1, 14, 0, 0),
            datetime(2024, 1, 1, 15, 0, 0),
        ]

        data = [
            [3.0, 50, 0, 50, 2.7, 50],
            [3.0, 60, 0, 60, 2.7, 50],
            [5.0, 60, 10, 30, 2.7, 50],
            [5.0, 80, 40, 40, 2.7, 50],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HPWH_sizing", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                True,
                True,
                True,
                True,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertTrue(binary_result)

    def test_HPWH_sizing_fail(self):
        points = [
            "T_amb",
            "HeatingRate_dx_coil",
            "HeatingRate_waterheater1",
            "HeatingRate_waterheater2",
            "T_amb_parameter",
            "HPWH_output_target_percent",
        ]

        timestamp = [
            datetime(2024, 1, 1, 12, 0, 0),
            datetime(2024, 1, 1, 13, 0, 0),
            datetime(2024, 1, 1, 14, 0, 0),
            datetime(2024, 1, 1, 15, 0, 0),
        ]

        data = [
            [3.0, 50, 0, 50, 2.7, 50],
            [3.0, 60, 0, 60, 2.7, 50],
            [5.0, 60, 10, 30, 2.7, 50],
            [
                5.0,
                30,
                40,
                40,
                2.7,
                50,
            ],  # fail because of this line (e.g., 30 / (30+40+40) < 50)
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HPWH_sizing", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                False,
                False,
                False,
                False,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)

    def test_HPWH_sizing_fail_all_temps_less_than_temp_param(self):
        points = [
            "T_amb",
            "HeatingRate_dx_coil",
            "HeatingRate_waterheater1",
            "HeatingRate_waterheater2",
            "T_amb_parameter",
            "HPWH_output_target_percent",
        ]

        timestamp = [
            datetime(2024, 1, 1, 12, 0, 0),
            datetime(2024, 1, 1, 13, 0, 0),
            datetime(2024, 1, 1, 14, 0, 0),
            datetime(2024, 1, 1, 15, 0, 0),
        ]

        data = [
            [1.0, 50, 0, 50, 2.7, 50],
            [1.0, 60, 0, 60, 2.7, 50],
            [2.0, 60, 10, 30, 2.7, 50],
            [
                2.0,
                30,
                40,
                40,
                2.7,
                50,
            ],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("HPWH_sizing", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                False,
                False,
                False,
                False,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
