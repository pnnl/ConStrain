import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterPlantSizingWholePlant(unittest.TestCase):
    def test_chilled_water_plant_sizing_whole_plant_missing_load_plant_water_chilled(
        self,
    ):
        points = [
            "temperature_water_supply",
            "temperature_water_return",
            "flow_mass_water",
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
        ]
        timestamp = [
            datetime(2023, 8, 1, 10, 0, 0),
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
        ]
        data = [
            [7.0, 13.0, 20.0, None, 28.0, 80],
            [7.0, 13.0, 20.0, None, 30.0, 80],
            [7.0, 13.0, 20.0, None, 32.0, 80],
            [7.0, 13.0, 20.0, None, 34.0, 80],
            [7.0, 13.0, 20.0, None, 35.0, 80],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_whole_plant_high_temp_air_outdoor(self):
        points = [
            "temperature_water_supply",
            "temperature_water_return",
            "flow_mass_water",
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
        ]
        timestamp = [
            datetime(2023, 8, 1, 10, 0, 0),
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
        ]
        data = [
            [7.0, 13.0, 20.0, 85.4, 50.0, 86],
            [7.0, 13.0, 20.0, 80, 30.0, 86],
            [7.0, 13.0, 20.0, 77.4, 32.0, 86],
            [7.0, 13.0, 20.0, 77.6, 34.0, 86],
            [7.0, 13.0, 20.0, 80, 35.0, 86],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([False, False, False, False, False])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)

    def test_chilled_water_plant_sizing_whole_plant_linear_model(self):
        points = [
            "temperature_water_supply",
            "temperature_water_return",
            "flow_mass_water",
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
        ]
        timestamp = [
            datetime(2023, 8, 1, 10, 0, 0),
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
        ]
        data = [
            [7.0, 13.0, 20.0, 66, 28.0, 80],
            [7.0, 13.0, 20.0, 70, 30.0, 80],
            [7.0, 13.0, 20.0, 74, 32.0, 80],
            [7.0, 13.0, 20.0, 78, 34.0, 80],
            [7.0, 13.0, 20.0, 80, 35.0, 80],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([True, True, True, True, True])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_whole_plant_cubic_model(self):
        points = [
            "temperature_water_supply",
            "temperature_water_return",
            "flow_mass_water",
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
        ]
        timestamp = [
            datetime(2023, 8, 1, 10, 0, 0),
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
        ]
        data = [
            [7.0, 13.0, 20.0, 85.4, 28.0, 86],
            [7.0, 13.0, 20.0, 80, 30.0, 86],
            [7.0, 13.0, 20.0, 77.4, 32.0, 86],
            [7.0, 13.0, 20.0, 77.6, 34.0, 86],
            [7.0, 13.0, 20.0, 80, 35.0, 86],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        expected_results = pd.Series([False, False, False, False, False])
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(results.equals(expected_results))
        self.assertFalse(binaryflag)
