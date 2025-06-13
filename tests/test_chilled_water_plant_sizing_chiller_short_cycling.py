import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterPlantSizingChillerShortCycling(unittest.TestCase):
    def test_chilled_water_plant_sizing_chiller_short_cycling_power_input_pass(
        self,
    ):
        points = [
            "status_chiller",
            "cycles_number_maximum",
        ]
        timestamp = [
            datetime(2023, 11, 1, 8, 0),
            datetime(2023, 11, 1, 8, 15),
            datetime(2023, 11, 1, 8, 30),
            datetime(2023, 11, 1, 8, 45),
            datetime(2023, 11, 1, 9, 0),
            datetime(2023, 11, 1, 9, 15),
            datetime(2023, 11, 1, 9, 30),
            datetime(2023, 11, 1, 9, 45),
            datetime(2023, 11, 1, 10, 0),
            datetime(2023, 11, 1, 10, 15),
            datetime(2023, 11, 1, 10, 30),
            datetime(2023, 11, 1, 10, 45),
            datetime(2023, 11, 1, 11, 00),
        ]
        data = [
            [0, 2],
            [0, 2],
            [0, 2],
            [0, 2],
            [0, 2],
            [0, 2],
            [0, 2],
            [5.0, 2],
            [5.0, 2],
            [4.8, 2],
            [4.7, 2],
            [4.5, 2],
            [5.0, 2],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingChillerShortCycling", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_chiller_short_cycling_all_hours_less_than_max_cycling_pass(
        self,
    ):
        points = [
            "status_chiller",
            "cycles_number_maximum",
        ]
        timestamp = [
            datetime(2023, 11, 1, 8, 0),
            datetime(2023, 11, 1, 8, 15),
            datetime(2023, 11, 1, 8, 30),
            datetime(2023, 11, 1, 8, 45),
            datetime(2023, 11, 1, 9, 0),
            datetime(2023, 11, 1, 9, 15),
            datetime(2023, 11, 1, 9, 30),
            datetime(2023, 11, 1, 9, 45),
            datetime(2023, 11, 1, 10, 0),
            datetime(2023, 11, 1, 10, 15),
            datetime(2023, 11, 1, 10, 30),
            datetime(2023, 11, 1, 10, 45),
            datetime(2023, 11, 1, 11, 00),
        ]
        data = [
            # 8
            [0, 2],
            [0, 2],
            [0, 2],
            [0, 2],
            # 9
            [0, 2],
            [0, 2],
            [0, 2],
            [1, 2],
            # 10
            [1, 2],
            [1, 2],
            [1, 2],
            [1, 2],
            # 11
            [1, 2],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingChillerShortCycling", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_chiller_short_cycling_some_hours_less_than_max_cycling_fail(
        self,
    ):
        points = [
            "status_chiller",
            "cycles_number_maximum",
        ]
        timestamp = [
            datetime(2023, 11, 1, 8, 0),
            datetime(2023, 11, 1, 8, 15),
            datetime(2023, 11, 1, 8, 30),
            datetime(2023, 11, 1, 8, 45),
            datetime(2023, 11, 1, 9, 0),
            datetime(2023, 11, 1, 9, 15),
            datetime(2023, 11, 1, 9, 30),
            datetime(2023, 11, 1, 9, 45),
            datetime(2023, 11, 1, 10, 0),
            datetime(2023, 11, 1, 10, 15),
            datetime(2023, 11, 1, 10, 30),
            datetime(2023, 11, 1, 10, 45),
            datetime(2023, 11, 1, 11, 00),
        ]
        data = [
            # 8
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            # 9
            [0, 1],
            [1, 1],
            [0, 1],
            [1, 1],
            # 10
            [1, 1],
            [1, 1],
            [1, 1],
            [1, 1],
            # 11
            [1, 1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, False, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingChillerShortCycling", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)
