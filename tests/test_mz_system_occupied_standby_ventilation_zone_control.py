import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *
import pandas as pd


class TestMZSystemOccupiedStandbyVentilationZoneControl(unittest.TestCase):
    def test_occupied_standby_ventilation_zontrol_control_fail(self):
        points = [
            "flag_zone_standby",
            "flow_volumetric_air_outdoor_system_setpoint",
            "flow_volumetric_air_outdoor_zone_req",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 10, 0),
        ]
        data = [
            [False, 1, 0.5],
            [True, 1, 0.5],
            [True, 0.5, 0.5],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", False, True])
        verification_obj = run_test_verification_with_data(
            "MZSystemOccupiedStandbyVentilationZoneControl", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_occupied_standby_ventilation_zontrol_control_pass(self):
        points = [
            "flag_zone_standby",
            "flow_volumetric_air_outdoor_system_setpoint",
            "flow_volumetric_air_outdoor_zone_req",
        ]
        timestamp = [
            datetime(2023, 3, 1, 2, 0, 0),
            datetime(2023, 3, 1, 2, 5, 0),
            datetime(2023, 3, 1, 2, 10, 0),
        ]
        data = [
            [False, 1, 0.5],
            [True, 0.5, 0.5],
            [True, 0.5, 0.25],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series(["Untested", True, True])
        verification_obj = run_test_verification_with_data(
            "MZSystemOccupiedStandbyVentilationZoneControl", df
        )
        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)
