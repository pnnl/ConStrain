import unittest, sys
import datetime

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36SupplyFanStatus(unittest.TestCase):
    def test_supply_fan_pass(self):
        points = ["sys_mode", "supply_fan_status", "has_reheat_box_on_perimeter_zones"]
        data = [
            ["occupied", True, True],
            ["unoccupied", False, True],
            ["setup", True, True],
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data("G36SupplyFanStatus", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([True, True, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertTrue(binary_result)

    def test_supply_fan_fail(self):
        points = ["sys_mode", "supply_fan_status", "has_reheat_box_on_perimeter_zones"]
        data = [
            ["occupied", False, False],
            ["unoccupied", True, False],
            ["setup", False, False],
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data("G36SupplyFanStatus", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([False, True, False])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)

    def test_supply_fan_untest(self):
        points = ["sys_mode", "supply_fan_status", "has_reheat_box_on_perimeter_zones"]
        data = [
            ["occupied", True, False],
            ["occupied", True, False],
            ["setup", True, False],
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data("G36SupplyFanStatus", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([True, True, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertTrue(binary_result == "Untested")


if __name__ == "__main__":
    unittest.main()
