import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterHotWaterPlantSizingChillerBoilerMaxLoading(unittest.TestCase):
    def test_chilled_water_hot_water_plant_sizing_chiller_boiler_max_loading_pass_chiller(
        self,
    ):
        points = [
            "ratio_loading",
            "ratio_loading_max_min",
            "ratio_loading_average_min",
            "system_type",
        ]
        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
        ]
        data = [
            [0.8, 0.5, 0.2, "Chiller"],
            [0.6, 0.5, 0.2, "Chiller"],
            [0.6, 0.5, 0.2, "Chiller"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingChillerBoilerMaxLoading", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_chilled_water_hot_water_plant_sizing_chiller_boiler_max_loading_fail_chiller(
        self,
    ):
        points = [
            "ratio_loading",
            "ratio_loading_max_min",
            "ratio_loading_average_min",
            "system_type",
        ]
        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
        ]
        data = [
            [0.8, 0.8, 0.7, "Chiller"],
            [0.6, 0.8, 0.7, "Chiller"],
            [0.6, 0.8, 0.7, "Chiller"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([False, False, False])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingChillerBoilerMaxLoading", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_chilled_water_hot_water_plant_sizing_chiller_boiler_max_loading_boiler(
        self,
    ):
        points = [
            "ratio_loading",
            "ratio_loading_max_min",
            "ratio_loading_average_min",
            "system_type",
        ]
        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
        ]
        data = [
            [0.8, 0.5, 0.2, "Boiler"],
            [0.6, 0.5, 0.2, "Boiler"],
            [0.6, 0.5, 0.2, "Boiler"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingChillerBoilerMaxLoading", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_chilled_water_hot_water_plant_sizing_chiller_boiler_max_loading_fail_boiler(
        self,
    ):
        points = [
            "ratio_loading",
            "ratio_loading_max_min",
            "ratio_loading_average_min",
            "system_type",
        ]
        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
        ]
        data = [
            [0.8, 0.8, 0.7, "Boiler"],
            [0.6, 0.8, 0.7, "Boiler"],
            [0.6, 0.8, 0.7, "Boiler"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([False, False, False])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingChillerBoilerMaxLoading", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)
