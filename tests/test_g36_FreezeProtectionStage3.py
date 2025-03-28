import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd


class TestG36FreezeProtectionStage2(unittest.TestCase):
    def test_freeze_protection_2_pass(self):
        points = [
            "freeze_stat",
            "supply_air_temp",
            "outdoor_damper_command",
            "supply_fan_status",
            "return_fan_status",
            "relief_fan_status",
            "cooling_coil_command",
            "heating_coil_command",
        ]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 3, 15, 30),
            datetime(2023, 3, 1, 3, 18, 0),
            datetime(2023, 3, 1, 3, 22, 0),
        ]

        data = [
            [False, 0.5, 20, True, False, False, 0, 100],
            [False, 0.5, 0, False, False, False, 100, 100],
            [False, 8, 0, False, False, False, 100, 100],
            [False, 8, 20, True, True, True, 0, 100],
            [False, 8, 20, True, True, True, 0, 100],
            [False, 8, 20, True, True, True, 0, 100],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, True, True, True, True, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage3", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_freeze_protection_2_Fail(self):
        points = [
            "freeze_stat",
            "supply_air_temp",
            "outdoor_damper_command",
            "supply_fan_status",
            "return_fan_status",
            "relief_fan_status",
            "cooling_coil_command",
            "heating_coil_command",
        ]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 3, 15, 30),
            datetime(2023, 3, 1, 3, 18, 0),
            datetime(2023, 3, 1, 3, 22, 0),
        ]

        data = [
            [False, 0.5, 20, True, False, False, 0, 100],
            [False, 0.5, 20, False, False, False, 100, 100],
            [False, 0, 0, True, False, False, 100, 100],
            [False, 0, 0, False, True, True, 0, 100],
            [False, 0, 0, False, False, True, 0, 100],
            [False, 0, 0, False, False, False, 0, 100],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, False, False, False, False, False])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage3", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_freeze_protection_2_pass(self):
        points = [
            "freeze_stat",
            "supply_air_temp",
            "outdoor_damper_command",
            "supply_fan_status",
            "return_fan_status",
            "relief_fan_status",
            "cooling_coil_command",
            "heating_coil_command",
        ]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 3, 15, 30),
            datetime(2023, 3, 1, 3, 18, 0),
            datetime(2023, 3, 1, 3, 22, 0),
        ]

        data = [
            [False, 8, 20, True, False, False, 0, 100],
            [False, 8, 0, False, False, False, 100, 100],
            [False, 8, 0, False, False, False, 100, 100],
            [False, 8, 20, True, True, True, 0, 100],
            [False, 8, 20, True, True, True, 0, 100],
            [False, 8, 20, True, True, True, 0, 100],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, True, True, True, True, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage3", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag == "Untested")


if __name__ == "__main__":
    unittest.main()
