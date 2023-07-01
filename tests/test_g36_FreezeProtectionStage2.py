import unittest, sys
import datetime

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36FreezeProtectionStage2(unittest.TestCase):
    def test_freeze_protection_2_pass(self):
        points = ["supply_air_temp", "outdoor_damper_command"]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 3, 15, 30),
            datetime(2023, 3, 1, 3, 18, 0),
            datetime(2023, 3, 1, 3, 22, 0),
        ]

        data = [[3, 90], [3, 0.5], [1, 0], [3, 20], [3, 20], [3, 0.1]]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, True, True, True, True, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage2", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_freeze_protection_2_fail(self):
        points = ["supply_air_temp", "outdoor_damper_command"]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 3, 1, 0),
            datetime(2023, 3, 1, 3, 5, 30),
            datetime(2023, 3, 1, 3, 18, 0),
            datetime(2023, 3, 1, 3, 22, 0),
            datetime(2023, 3, 1, 3, 24, 0),
        ]

        data = [[3, 90], [3, 50], [1, 50], [3, 20], [3, 20], [3, 20], [3, 20]]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, False, False, True, True, True, False])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage2", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_freeze_protection_2_untested(self):
        points = ["supply_air_temp", "outdoor_damper_command"]

        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 0),
            datetime(2023, 3, 1, 3, 15, 30),
            datetime(2023, 3, 1, 3, 18, 0),
            datetime(2023, 3, 1, 3, 22, 0),
        ]

        data = [[4, 90], [4, 0], [4, 0], [3, 20], [4, 20], [4, 0.1]]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        expected_results = pd.Series([True, True, True, True, True, True])

        verification_obj = run_test_verification_with_data(
            "G36FreezeProtectionStage2", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag == "Untested")


if __name__ == "__main__":
    unittest.main()
