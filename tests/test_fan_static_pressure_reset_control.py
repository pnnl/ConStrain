import sys
import unittest

sys.path.append("./constrain")
import datetime

import pandas as pd
from lib_unit_test_runner import *


class TestFanStaticPressureResetControl(unittest.TestCase):
    def test_fan_static_pressure_reset_control_pass(self):
        points = [
            "p_press_static_sp",
            "pos_damper_vav_1",
            "pos_damper_vav_2",
            "pos_damper_vav_3",
            "pos_damper_vav_4",
            "pos_damper_vav_5",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
            datetime(2024, 8, 1, 14, 0, 0),
            datetime(2024, 8, 1, 15, 0, 0),
        ]

        data = [
            [1.4, 0.75, 0.75, 0.75, 0.75, 0.75],
            [1.3, 0.75, 0.75, 0.75, 0.75, 0.75],
            [1.2, 0.75, 0.75, 0.75, 0.75, 0.75],
            [1.1, 0.75, 0.75, 0.75, 0.75, 0.75],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "FanStaticPressureResetControl", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                "Untested",
                True,
                True,
                True,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertTrue(binary_result)

    def test_fan_static_pressure_reset_control_fail(self):
        points = [
            "p_press_static_sp",
            "pos_damper_vav_1",
            "pos_damper_vav_2",
            "pos_damper_vav_3",
            "pos_damper_vav_4",
            "pos_damper_vav_5",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
            datetime(2024, 8, 1, 14, 0, 0),
            datetime(2024, 8, 1, 15, 0, 0),
        ]

        data = [
            [1.1, 0.75, 0.75, 0.75, 0.75, 0.75],
            [1.2, 0.75, 0.75, 0.75, 0.75, 0.75],
            [1.3, 0.75, 0.75, 0.75, 0.75, 0.75],
            [1.4, 0.75, 0.75, 0.75, 0.75, 0.75],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "FanStaticPressureResetControl", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                "Untested",
                False,
                False,
                False,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
