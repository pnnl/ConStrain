import sys
import unittest

sys.path.append("./constrain")
import datetime

import pandas as pd
from lib_unit_test_runner import *


class TestVAVTurndown(unittest.TestCase):
    def test_vav_turndown_reheat_coil_flag_untested(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
            "ratio_turndown_min",
            "pressure_duct_setpoint",
            "tol_turndown",
            "tol_p_press",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [False, 0.005, 0.01, 0.3, 1.0, 0.01, 0.01],
            [False, 0.005, 0.01, 0.3, 1.1, 0.01, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVMinimumTurndownDuringReheatPressureReset", df
        )
        results = list(verification_obj.result)
        expected_results = [
            "Untested",
            "Untested",
        ]

        self.assertEqual(results, expected_results)
        self.assertEqual(verification_obj.check_bool(), "Untested")

    def test_vav_turndown_V_dot_max_zero_untested(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
            "ratio_turndown_min",
            "pressure_duct_setpoint",
            "tol_turndown",
            "tol_p_press",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [True, 0.005, 0.0, 0.3, 1.0, 0.01, 0.01],
            [True, 0.005, 0.0, 0.3, 1.1, 0.01, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVMinimumTurndownDuringReheatPressureReset", df
        )
        results = list(verification_obj.result)
        expected_results = [
            "Untested",
            "Untested",
        ]

        self.assertEqual(results, expected_results)
        self.assertEqual(verification_obj.check_bool(), "Untested")

    def test_vav_turndown_P_set_same_untested(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
            "ratio_turndown_min",
            "pressure_duct_setpoint",
            "tol_turndown",
            "tol_p_press",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [True, 0.005, 0.0, 0.3, 1.0, 0.01, 0.01],
            [True, 0.005, 0.0, 0.3, 1.0, 0.01, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVMinimumTurndownDuringReheatPressureReset", df
        )
        results = list(verification_obj.result)
        expected_results = [
            "Untested",
            "Untested",
        ]

        self.assertEqual(results, expected_results)
        self.assertEqual(verification_obj.check_bool(), "Untested")

    def test_vav_turndown_pass(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
            "ratio_turndown_min",
            "pressure_duct_setpoint",
            "tol_turndown",
            "tol_p_press",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [True, 0.005, 0.06, 0.3, 1.0, 0.01, 0.01],
            [True, 0.005, 0.06, 0.3, 1.1, 0.01, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVMinimumTurndownDuringReheatPressureReset", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                True,
                True,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertTrue(binary_result)

    def test_vav_turndown_fail(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
            "ratio_turndown_min",
            "pressure_duct_setpoint",
            "tol_turndown",
            "tol_p_press",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [True, 0.005, 0.01, 0.3, 1.0, 0.01, 0.01],
            [True, 0.005, 0.01, 0.3, 1.0, 0.01, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVMinimumTurndownDuringReheatPressureReset", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                "Untested",
                False,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
