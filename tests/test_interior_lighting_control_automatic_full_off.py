import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd
import numpy as np


class TestInteriorLightingControlAutomaticFullOff(unittest.TestCase):
    tolerances = {
        "ratio": {
            "unit": "%",
            "types": {
                "occupancy": 0.1,
            },
        }
    }

    def test_interior_lighting_control_automatic_full_off_area_fail(self):
        points = [
            "number_occupants",
            "power_light_total",
            "area_lit",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
        ]
        data = [
            [0.1, 1400, 5000],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([False])
        verification_obj = run_test_verification_with_data(
            "InteriorLightingControlAutomaticFullOff", df, tolerances=self.tolerances
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_interior_lighting_control_automatic_full_off_fail(self):
        points = [
            "number_occupants",
            "power_light_total",
            "area_lit",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 26, 0),
        ]
        data = [
            [0.5, 1400, 500],
            [0.05, 1400, 500],
            [0.05, 50, 500],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", False])
        verification_obj = run_test_verification_with_data(
            "InteriorLightingControlAutomaticFullOff", df, tolerances=self.tolerances
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_interior_lighting_control_automatic_full_off_pass(self):
        points = [
            "number_occupants",
            "power_light_total",
            "area_lit",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 26, 0),
        ]
        data = [
            [0.5, 1400, 500],
            [0.05, 1400, 500],
            [0.05, 9, 500],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", True])
        verification_obj = run_test_verification_with_data(
            "InteriorLightingControlAutomaticFullOff", df, tolerances=self.tolerances
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)
