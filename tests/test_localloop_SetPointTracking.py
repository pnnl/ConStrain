import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd


class TestLocalLoopSetPointTracking(unittest.TestCase):
    def test_set_point_tracking_pass(self):
        points = ["feedback_sensor", "set_point"]
        timestamp = [
            datetime(2023, 5, 1, 18, 0, 0),
            datetime(2023, 5, 1, 18, 1, 0),
            datetime(2023, 5, 1, 18, 2, 0),
            datetime(2023, 5, 1, 18, 3, 0),
            datetime(2023, 5, 1, 18, 4, 0),
            datetime(2023, 5, 1, 18, 5, 0),
            datetime(2023, 5, 1, 18, 6, 0),
            datetime(2023, 5, 1, 18, 7, 0),
            datetime(2023, 5, 1, 18, 8, 0),
            datetime(2023, 5, 1, 18, 9, 0),
            datetime(2023, 5, 1, 18, 10, 0),
            datetime(2023, 5, 1, 18, 11, 0),
            datetime(2023, 5, 1, 18, 12, 0),
            datetime(2023, 5, 1, 18, 13, 0),
            datetime(2023, 5, 1, 18, 14, 0),
            datetime(2023, 5, 1, 18, 15, 0),
            datetime(2023, 5, 1, 18, 16, 0),
            datetime(2023, 5, 1, 18, 17, 0),
            datetime(2023, 5, 1, 18, 18, 0),
            datetime(2023, 5, 1, 18, 19, 0),
            datetime(2023, 5, 1, 18, 20, 0),
        ]

        data = [
            [96, 100],
            [97, 100],
            [98, 100],
            [99, 100],
            [100, 100],
            [101, 100],
            [102, 100],
            [103, 100],
            [104, 100],
            [105.1, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
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
                False,
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
            "LocalLoopSetPointTracking", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_set_point_tracking_fail_samplepct(self):
        points = ["feedback_sensor", "set_point"]
        timestamp = [
            datetime(2023, 5, 1, 18, 0, 0),
            datetime(2023, 5, 1, 18, 1, 0),
            datetime(2023, 5, 1, 18, 2, 0),
            datetime(2023, 5, 1, 18, 3, 0),
            datetime(2023, 5, 1, 18, 4, 0),
            datetime(2023, 5, 1, 18, 5, 0),
            datetime(2023, 5, 1, 18, 6, 0),
            datetime(2023, 5, 1, 18, 7, 0),
            datetime(2023, 5, 1, 18, 8, 0),
            datetime(2023, 5, 1, 18, 9, 0),
        ]

        data = [
            [96, 100],
            [97, 100],
            [98, 100],
            [99, 100],
            [100, 100],
            [101, 100],
            [102, 100],
            [103, 100],
            [104, 100],
            [105.1, 100],
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
                False,
            ]
        )

        verification_obj = run_test_verification_with_data(
            "LocalLoopSetPointTracking", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_set_point_tracking_pass(self):
        points = ["feedback_sensor", "set_point"]
        timestamp = [
            datetime(2023, 5, 1, 18, 0, 0),
            datetime(2023, 5, 1, 18, 1, 0),
            datetime(2023, 5, 1, 18, 2, 0),
            datetime(2023, 5, 1, 18, 3, 0),
            datetime(2023, 5, 1, 18, 4, 0),
            datetime(2023, 5, 1, 18, 5, 0),
            datetime(2023, 5, 1, 18, 6, 0),
            datetime(2023, 5, 1, 18, 7, 0),
            datetime(2023, 5, 1, 18, 8, 0),
            datetime(2023, 5, 1, 18, 9, 0),
            datetime(2023, 5, 1, 18, 10, 0),
            datetime(2023, 5, 1, 18, 11, 0),
            datetime(2023, 5, 1, 18, 12, 0),
            datetime(2023, 5, 1, 18, 13, 0),
            datetime(2023, 5, 1, 18, 14, 0),
            datetime(2023, 5, 1, 18, 15, 0),
            datetime(2023, 5, 1, 18, 16, 0),
            datetime(2023, 5, 1, 18, 17, 0),
            datetime(2023, 5, 1, 18, 18, 0),
            datetime(2023, 5, 1, 18, 19, 0),
            datetime(2023, 5, 1, 18, 20, 0),
        ]

        data = [
            [96, 100],
            [97, 100],
            [98, 100],
            [99, 100],
            [100, 100],
            [101, 100],
            [102, 100],
            [103, 100],
            [104, 100],
            [105.1, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
            [104, 100],
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
                False,
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
            "LocalLoopSetPointTracking", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()

        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)


if __name__ == "__main__":
    unittest.main()
