import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36OutputChangeRateLimit(unittest.TestCase):
    def test_output_change_rate_pass(self):
        points = ["command", "max_rate_of_change_per_min"]
        data = [[50, 25], [40, 25], [30, 25], [50, 25], [74, 25], [44, 25]]
        timestamp = [
            datetime(2023, 1, 1, 15, 0, 2),
            datetime(2023, 1, 1, 15, 1, 2),
            datetime(2023, 1, 1, 15, 2, 2),
            datetime(2023, 1, 1, 15, 3, 2),
            datetime(2023, 1, 1, 15, 4, 2),
            datetime(2023, 1, 1, 15, 5, 32),
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(run_test_verification_with_data("G36OutputChangeRateLimit", df).result)
        )

        expected_results = pd.Series([np.nan, True, True, True, True, True])

        self.assertTrue(results.equals(expected_results))

    def test_output_change_rate_fail(self):
        points = ["command", "max_rate_of_change_per_min"]
        data = [[50, 25], [40, 25], [30, 25], [50, 25], [74, 25], [44, 25]]
        timestamp = [
            datetime(2023, 1, 1, 15, 0, 2),
            datetime(2023, 1, 1, 15, 1, 2),
            datetime(2023, 1, 1, 15, 2, 2),
            datetime(2023, 1, 1, 15, 3, 2),
            datetime(2023, 1, 1, 15, 4, 2),
            datetime(2023, 1, 1, 15, 5, 0),
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(run_test_verification_with_data("G36OutputChangeRateLimit", df).result)
        )

        expected_results = pd.Series([np.nan, True, True, True, True, False])

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
