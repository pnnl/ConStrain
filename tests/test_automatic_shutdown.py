import sys
import unittest

sys.path.append("./constrain")
import datetime

import pandas as pd
from lib_unit_test_runner import *


class AutomaticShutdown(unittest.TestCase):
    def test_Automatic_Shutdown_pass(self):
        points = [
            "schedule_hvac",
        ]

        timestamp = [
            datetime(2024, 1, i, j, 0, 0) for i in range(1, 3) for j in range(0, 24)
        ]

        day_ranges = [
            (8, 18),  # Day 1 HVAC operation: 8:00 to 18:00
            (9, 17),  # Day 2 HVAC operation: 9:00 to 17:00
        ]

        # Generate data for both days
        data = [
            1 if day_start <= hour <= day_end else 0
            for day_start, day_end in day_ranges
            for hour in range(24)
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("AutomaticShutdown", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                True,
            ]
            * 48
        )

        self.assertTrue(results.equals(expected_results))
        binary_result = verification_obj.check_bool()
        self.assertTrue(binary_result)

    def test_Automatic_Shutdown_fail(self):
        points = [
            "schedule_hvac",
        ]

        timestamp = [
            datetime(2024, 1, i, j, 0, 0) for i in range(1, 3) for j in range(0, 24)
        ]

        day_ranges = [
            (8, 18),  # Day 1 HVAC operation: 8:00 to 18:00
            (8, 18),  # Day 2 HVAC operation: 8:00 to 18:00
        ]

        # Generate data for both days
        data = [
            1 if day_start <= hour <= day_end else 0
            for day_start, day_end in day_ranges
            for hour in range(24)
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        verification_obj = run_test_verification_with_data("AutomaticShutdown", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                False,
            ]
            * 48
        )

        self.assertTrue(results.equals(expected_results))
        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
