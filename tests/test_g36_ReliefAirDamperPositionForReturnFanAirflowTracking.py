import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36ReliefAirDamperPositionForReturnFanAirflowTracking(unittest.TestCase):
    tolerances = {
        "damper": {
            "unit": "%",
            "types": {
                "position": 0.05,
            },
        }
    }

    def test_relief_air_damper_position(self):
        points = [
            "output_coil_heating",
            "output_coil_cooling",
            "position_damper_relief",
            "position_damper_relief_max",
            "position_damper_air_return",
        ]
        data = [
            [1000, 0, 0.5, 1.0, 1.0],  # False
            [1000, 0, 0.02, 1.0, 1.0],  # True
            [0, 1000, 0.2, 1.0, 1.0],  # False
            [0, 1000, 0.99, 1.0, 1.0],  # True
            [0, 0, 0.05, 1.0, 0.8],  # False
            [0, 0, 0.2, 1.0, 0.8],  # True
            [0, 0, 0.5, 1.0, 0.5],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36ReliefAirDamperPositionForReturnFanAirflowTracking",
            df,
            tolerances=self.tolerances,
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([False, True, False, True, False, True, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
