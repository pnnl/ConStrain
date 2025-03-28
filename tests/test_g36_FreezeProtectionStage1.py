import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd


class TestG36FreezeProtectionStage1(unittest.TestCase):

    tolerances = {
        "damper": {
            "unit": "%",
            "types": {"position": 0.0, "command": 0.01, "general": 0.0},
        },
        "temperature": {
            "unit": "deg. C",
            "types": {"supply_air": 0.0, "general": 0.0},
        },
    }

    def test_freeze_protection_1_pass(self):
        points = [
            "temperature_air_supply_setpoint",
            "position_damper_air_outdoor",
            "position_damper_air_outdoor_min",
        ]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 2, 15, 30),
            datetime(2023, 3, 1, 2, 18, 0),
        ]

        data = [[4, 30, 20], [4, 20, 20], [8, 20, 20], [9, 20, 20], [10, 30, 20]]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, True, True, True, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage1", df, tolerances=self.tolerances
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_freeze_protection_1_fail(self):
        points = [
            "temperature_air_supply_setpoint",
            "position_damper_air_outdoor",
            "position_damper_air_outdoor_min",
        ]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 2, 14, 30),
            datetime(2023, 3, 1, 2, 18, 0),
        ]

        data = [[4, 30, 20], [4, 30, 20], [8, 30, 20], [9, 40, 20], [10, 30, 20]]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, False, False, False, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage1", df, tolerances=self.tolerances
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_freeze_protection_1_untested(self):
        points = [
            "temperature_air_supply_setpoint",
            "position_damper_air_outdoor",
            "position_damper_air_outdoor_min",
        ]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 2, 14, 30),
            datetime(2023, 3, 1, 2, 18, 0),
        ]

        data = [[8, 30, 20], [10, 30, 20], [5, 30, 20], [5, 40, 20], [5, 30, 20]]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, True, True, True, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage1", df, tolerances=self.tolerances
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag == "Untested")


if __name__ == "__main__":
    unittest.main()
