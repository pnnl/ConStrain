import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure(
    unittest.TestCase
):
    tolerances = {
        "damper": {
            "unit": "%",
            "types": {
                "command": 0.05,
            },
        }
    }

    def test_return_air_damper_position(self):
        points = [
            "position_damper_air_outdoor",
            "position_damper_air_outdoor_max",
        ]
        data = [
            [0.1, 1],  # False
            [0.98, 1],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure",
            df,
            tolerances=self.tolerances,
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([False, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
