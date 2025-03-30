import sys
import unittest

sys.path.append("./constrain")
import datetime

import pandas as pd
from lib_unit_test_runner import *


class TestVAVTurndown(unittest.TestCase):
    tolerances = {
        "ratio": {
            "unit": "%",
            "types": {
                "flow": 0.01,
            },
        }
    }

    def test_vav_turndown_during_reheat_pass(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
            datetime(2024, 8, 1, 14, 0, 0),
            datetime(2024, 8, 1, 15, 0, 0),
        ]

        data = [
            [True, 350, 620],
            [True, 370, 620],
            [False, 360, 620],
            [False, 380, 620],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVTurndownDuringReheat", df, tolerances=self.tolerances
        )

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

    def test_vav_turndown_during_reheat_fail(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
            datetime(2024, 8, 1, 14, 0, 0),
            datetime(2024, 8, 1, 15, 0, 0),
        ]

        data = [
            [False, 350, 620],
            [False, 370, 620],
            [True, 360, 620],
            [True, 380, 620],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVTurndownDuringReheat", df, tolerances=self.tolerances
        )

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

    def test_vav_turndown_during_reheat_untested(self):
        points = [
            "flag_coil_reheat",
            "flow_volumetric_air_vav",
            "flow_volumetric_air_max",
        ]

        timestamp = [
            datetime(2024, 8, 1, 12, 0, 0),
            datetime(2024, 8, 1, 13, 0, 0),
            datetime(2024, 8, 1, 14, 0, 0),
            datetime(2024, 8, 1, 15, 0, 0),
        ]

        data = [
            [False, 350, 620],
            [False, 370, 620],
            [False, 360, 620],
            [False, 380, 620],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data(
            "VAVTurndownDuringReheat", df, tolerances=self.tolerances
        )
        results = list(verification_obj.result)
        expected_results = [
            "Untested",
            "Untested",
            "Untested",
            "Untested",
        ]

        self.assertEqual(results, expected_results)
        self.assertEqual(verification_obj.check_bool(), "Untested")
