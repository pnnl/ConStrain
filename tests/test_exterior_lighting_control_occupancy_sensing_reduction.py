import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd
import numpy as np


class TestExteriorLightingControlOccupancySensingReduction(unittest.TestCase):
    tolerances = {"ratio": {"unit": "%", "types": {"occupancy": 0.25, "general": 0.25}}}

    def test_exterior_lighting_control_occupancy_sensing_reduction_power_too_high(self):
        points = [
            "o",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 10, 0),
        ]
        data = [[0.05, 1650], [0.1, 100], [0.05, 100]]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlOccupancySensingReduction",
            df,
            tolerances=self.tolerances,
        )
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_exterior_lighting_control_occupancy_sensing_reduction_pass(self):
        points = [
            "o",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 30, 0),
        ]
        data = [[0.1, 1400], [0.1, 1300], [0.05, 300]]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", True])
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlOccupancySensingReduction",
            df,
            tolerances=self.tolerances,
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_exterior_lighting_control_occupancy_sensing_reduction_fail(self):
        points = [
            "o",
            "total_lighting_power",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 30, 0),
        ]
        data = [[0.1, 1400], [0.1, 1300], [0.05, 701]]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", "Untested", False])
        verification_obj = run_test_verification_with_data(
            "ExteriorLightingControlOccupancySensingReduction",
            df,
            tolerances=self.tolerances,
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)
