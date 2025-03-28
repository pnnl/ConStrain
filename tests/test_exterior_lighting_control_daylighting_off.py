import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd
import numpy as np


class TestExteriorLightingControlDaylightOff(unittest.TestCase):
    def test_exterior_lighting_control_occupancy_sensing_reduction_fail(self):
        points = [
            "is_sun_up",
            "daylight_sensed",
            "daylight_setpoint",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 35, 0),
        ]
        data = [
            [False, 0.1, 1, 1],
            [True, 0.1, 1, 1],
            [True, 0.1, 1, 1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", False])
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlDaylightOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_exterior_lighting_control_occupancy_sensing_reduction_pass(self):
        points = [
            "is_sun_up",
            "daylight_sensed",
            "daylight_setpoint",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 35, 0),
        ]
        data = [
            [False, 0.1, 1, 1],
            [True, 0.1, 1, 1],
            [True, 0.1, 1, 0],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", True])
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlDaylightOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_exterior_lighting_control_occupancy_sensing_reduction_fail_daylight(self):
        points = [
            "is_sun_up",
            "daylight_sensed",
            "daylight_setpoint",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 35, 0),
        ]
        data = [
            [False, 0.1, 1, 1],
            [False, 0.1, 1, 1],
            [False, 1, 1, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", False])
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlDaylightOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_exterior_lighting_control_occupancy_sensing_reduction_pass_daylight(self):
        points = [
            "is_sun_up",
            "daylight_sensed",
            "daylight_setpoint",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 35, 0),
        ]
        data = [
            [False, 0.1, 1, 1],
            [False, 0.1, 1, 1],
            [False, 1, 1, 0],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", True])
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlDaylightOff", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)
