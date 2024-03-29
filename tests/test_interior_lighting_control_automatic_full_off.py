import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd


class TestInteriorLightingControlAutomaticFullOff(unittest.TestCase):
    def test_interior_lighting_control_automatic_full_off_area_fail(self):
        points = [
            "o",
            "total_lighting_power",
            "lighted_floor_area",
            "tol_o",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
        ]
        data = [
            [0.1, 1400, 5000, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([False])
        verification_obj = run_test_verification_with_data(
            "InteriorLightingControlAutomaticFullOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_interior_lighting_control_automatic_full_off_fail(self):
        points = [
            "o",
            "total_lighting_power",
            "lighted_floor_area",
            "tol_o",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 26, 0),
        ]
        data = [
            [0.5, 1400, 500, 0.1],
            [0.05, 1400, 500, 0.1],
            [0.05, 50, 500, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, False])
        verification_obj = run_test_verification_with_data(
            "InteriorLightingControlAutomaticFullOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_interior_lighting_control_automatic_full_off_pass(self):
        points = [
            "o",
            "total_lighting_power",
            "lighted_floor_area",
            "tol_o",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 26, 0),
        ]
        data = [
            [0.5, 1400, 500, 0.1],
            [0.05, 1400, 500, 0.1],
            [0.05, 9, 500, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True])
        verification_obj = run_test_verification_with_data(
            "InteriorLightingControlAutomaticFullOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)
