import unittest, sys
import datetime

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *
import pandas as pd


class TestLocalLoopSaturationDirectActingMax(unittest.TestCase):
    def test_saturation_damax_pass(self):
        points = ["feedback_sensor", "set_point", "cmd", "cmd_max"]
        timestamp = [
            datetime(2023, 5, 1, 0, 5, 0),
            datetime(2023, 5, 1, 1, 5, 10),
            datetime(2023, 5, 1, 2, 5, 0),
            datetime(2023, 5, 1, 3, 5, 30),
            datetime(2023, 5, 1, 4, 5, 0),
            datetime(2023, 5, 1, 5, 5, 0),
            datetime(2023, 5, 1, 6, 5, 0),
            datetime(2023, 5, 1, 7, 5, 0),
            datetime(2023, 5, 1, 8, 5, 5),
            datetime(2023, 5, 1, 9, 5, 0),
            datetime(2023, 5, 1, 10, 5, 0),
        ]

        data = [
            [100, 100, 50, 100],
            [106, 100, 99.99, 100],
            [107, 100, 100, 100],
            [103, 100, 100, 100],
            [102, 100, 100, 100],
            [103, 100, 100, 100],
            [103, 100, 100, 100],
            [99, 100, 98, 100],
            [100, 100, 55, 100],
            [100, 100, 30, 100],
            [100, 100, 100, 100],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(
            [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            ]
        )

        verification_obj = run_test_verification_with_data(
            "LocalLoopSaturationDirectActingMax", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        verification_obj.check_detail()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_saturation_damax_pass(self):
        points = ["feedback_sensor", "set_point", "cmd", "cmd_max"]
        timestamp = [
            datetime(2023, 5, 1, 0, 5, 0),
            datetime(2023, 5, 1, 1, 5, 10),
            datetime(2023, 5, 1, 2, 5, 0),
            datetime(2023, 5, 1, 3, 5, 30),
            datetime(2023, 5, 1, 4, 5, 0),
            datetime(2023, 5, 1, 5, 5, 0),
            datetime(2023, 5, 1, 6, 5, 0),
            datetime(2023, 5, 1, 7, 5, 0),
            datetime(2023, 5, 1, 8, 5, 5),
            datetime(2023, 5, 1, 9, 5, 0),
            datetime(2023, 5, 1, 11, 5, 0),
        ]

        data = [
            [100, 100, 50, 100],
            [106, 100, 99.99, 100],
            [107, 100, 99, 100],
            [103, 100, 99, 100],
            [102, 100, 100, 100],
            [103, 100, 100, 100],
            [103, 100, 100, 100],
            [99, 100, 98, 100],
            [100, 100, 55, 100],
            [101, 100, 30, 100],
            [101, 100, 90, 100],
        ]

        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(
            [
                True,
                True,
                True,
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
            ]
        )

        verification_obj = run_test_verification_with_data(
            "LocalLoopSaturationDirectActingMax", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        verification_obj.check_detail()

        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)


if __name__ == "__main__":
    unittest.main()
