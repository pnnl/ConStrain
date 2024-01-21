import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36ReliefDamperStatus(unittest.TestCase):
    def test_relief_damper_status_pass_fail(self):
        points = ["relief_damper_command", "supply_fan_status"]
        data = [[20, 1], [0, 0], [0, 1]]

        expected_results = pd.Series([True, True, False])

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data("G36ReliefDamperStatus", df)
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_relief_damper_status_finalflag_pass(self):
        points = ["relief_damper_command", "supply_fan_status"]
        data = [[20, 1], [0, 0]]

        df = pd.DataFrame(data, columns=points)

        result = run_test_verification_with_data(
            "G36ReliefDamperStatus", df
        ).check_bool()

        self.assertTrue(result)

    def test_relief_damper_status_finalflag_untested(self):
        points = ["relief_damper_command", "supply_fan_status"]
        data = [[20, 1], [30, 1]]

        df = pd.DataFrame(data, columns=points)

        result = run_test_verification_with_data(
            "G36ReliefDamperStatus", df
        ).check_bool()

        self.assertTrue(result == "Untested")


if __name__ == "__main__":
    unittest.main()
