import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd


class TestAppendixGHVACSystemFanOperation(unittest.TestCase):
    def test_hvac_system_fan_operation_no_oa_untested(self):
        points = [
            "number_occupants",
            "fraction_runtime_fan",
            "flow_volumetric_air_outdoor",
            "tol_occupants",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
        ]
        data = [
            [0.05, 1, 0, 0.1],
            [0.15, 0, 0, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "AppendixGHVACSystemFanOperation", df
        )
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag is None)

    def test_hvac_system_fan_operation_oa_fail(self):
        points = [
            "number_occupants",
            "fraction_runtime_fan",
            "flow_volumetric_air_outdoor",
            "tol_occupants",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 2),
        ]
        data = [
            [0.1, 1, 0.5, 0.1],
            [0.1, 0.5, 0, 0.1],
            [0.05, 1, 0.5, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, False, True])
        verification_obj = run_test_verification_with_data(
            "AppendixGHVACSystemFanOperation", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_hvac_system_fan_operation_oa_pass(self):
        points = [
            "number_occupants",
            "fraction_runtime_fan",
            "flow_volumetric_air_outdoor",
            "tol_occupants",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 2),
            datetime(2023, 3, 1, 2, 10, 2),
        ]
        data = [
            [0.1, 1, 0.5, 0.1],
            [0.1, 0.5, 0, 0.1],
            [0.05, 0, 0.5, 0.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, False, True])
        verification_obj = run_test_verification_with_data(
            "AppendixGHVACSystemFanOperation", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)
