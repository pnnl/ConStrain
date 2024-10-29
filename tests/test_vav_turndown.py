import sys
import unittest

sys.path.append("./constrain")
import datetime

import pandas as pd
from lib_unit_test_runner import *


class TestVAVTurndown(unittest.TestCase):
    def test_vav_turndown_untested(self):
        points = [
            "reheat_coil_flag",
            "V_dot_VAV",
            "V_dot_VAV_max",
            "VAV_min_turndown_design",
            "turndown_tol",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [False, 0.005, 0.01, 0.3, 0.01],
            [False, 0.005, 0.01, 0.3, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("VAVTurndown", df)
        results = list(verification_obj.result)
        expected_results = [
            "Untested",
            "Untested",
        ]

        self.assertEqual(results, expected_results)

    def test_vav_turndown_pass(self):
        points = [
            "reheat_coil_flag",
            "V_dot_VAV",
            "V_dot_VAV_max",
            "VAV_min_turndown_design",
            "turndown_tol",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [True, 0.005, 0.06, 0.3, 0.01],
            [True, 0.005, 0.06, 0.3, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("VAVTurndown", df)

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
            "reheat_coil_flag",
            "V_dot_VAV",
            "V_dot_VAV_max",
            "VAV_min_turndown_design",
            "turndown_tol",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
        ]

        data = [
            [True, 0.005, 0.01, 0.3, 0.01],
            [True, 0.005, 0.01, 0.3, 0.01],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("VAVTurndown", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                False,
                False,
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
