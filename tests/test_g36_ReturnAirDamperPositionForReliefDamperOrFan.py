import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36ReturnAirDamperPositionForReliefDamperOrFan(unittest.TestCase):
    tolerances = {
        "damper": {
            "unit": "%",
            "general": 0.05,
            "types": {
                "position": 0.05,
            },
        }
    }

    def test_return_air_damper_position(self):
        points = [
            "heating_output",
            "cooling_output",
            "ra_p",
            "max_ra_p",
            "oa_p",
            "max_oa_p",
        ]
        data = [
            [
                1000,
                0,
                0.5,
                1.0,
                0.2,
                1.0,
            ],  # False
            [
                1000,
                0,
                1.0,
                1.0,
                0.2,
                1.0,
            ],  # True
            [
                0,
                1000,
                0.5,
                1.0,
                0.2,
                1.0,
            ],  # False
            [
                0,
                1000,
                0.02,
                1.0,
                0.2,
                1.0,
            ],  # True
            [
                0,
                0,
                0.5,
                1.0,
                0.2,
                1.0,
            ],  # False
            [
                0,
                0,
                1.0,
                1.0,
                0.2,
                1.0,
            ],  # True
            [
                0,
                0,
                1.0,
                1.0,
                1.0,
                1.0,
            ],  # False
            [
                0,
                0,
                0.5,
                1.0,
                1.0,
                1.0,
            ],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36ReturnAirDamperPositionForReliefDamperOrFan",
            df,
            tolerances=self.tolerances,
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [False, True, False, True, False, True, False, True]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
