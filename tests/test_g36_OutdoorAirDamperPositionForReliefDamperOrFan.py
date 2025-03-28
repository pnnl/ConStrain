import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36OutdoorAirDamperPositionForReliefDamperOrFan(unittest.TestCase):
    tolerances = {
        "damper": {
            "unit": "%",
            "types": {
                "position": 0.05,
            },
        }
    }

    def test_return_air_damper_position(self):
        points = [
            "output_coil_heating",
            "output_coil_cooling",
            "position_damper_air_return",
            "position_damper_air_return_max",
            "position_damper_air_outdoor",
            "position_damper_air_outdoor_min",
            "position_damper_air_outdoor_max",
            "flag_economizer_limit",
        ]
        data = [
            [1000, 0, 1.0, 1.0, 0.8, 0.2, 1.0, False],  # False
            [1000, 0, 1.0, 1.0, 0.2, 0.2, 1.0, False],  # True
            [0, 1000, 1.0, 1.0, 0.2, 0.2, 1.0, False],  # False
            [0, 1000, 1.0, 1.0, 0.8, 0.2, 1.0, False],  # False
            [0, 1000, 1.0, 1.0, 0.98, 0.2, 1.0, False],  # True
            [0, 1000, 1.0, 1.0, 0.8, 0.2, 1.0, True],  # False
            [0, 0, 1.0, 1.0, 0.2, 0.2, 1.0, False],  # False
            [0, 0, 1.0, 1.0, 0.8, 0.2, 1.0, False],  # True
            [0, 0, 0, 1.0, 0.8, 0.2, 1.0, False],  # False
            [0, 0, 0, 1.0, 1.0, 0.2, 1.0, False],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36OutdoorAirDamperPositionForReliefDamperOrFan",
            df,
            tolerances=self.tolerances,
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [False, True, False, False, True, False, False, True, False, True]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
