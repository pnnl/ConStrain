import datetime
import sys
import os
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterPlantSizingWholePlant(unittest.TestCase):
    def test_chilled_water_plant_sizing_plant_pass(self):
        points = [
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
            "temperature_drybulb_day_design_cooling",
            "factor_oversizing",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [1000, 32, 1200, 30.75, 1.1],
            [1000, 31, 1200, 30.75, 1.1],
            [1000, 29, 1200, 30.75, 1.1],
            [1000, 28, 1200, 30.75, 1.1],
            [1500, 35, 1200, 30.75, 1.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        # Perform verification using run_test_verification_with_data
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        # Check results
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_plant_fail(self):
        points = [
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
            "temperature_drybulb_day_design_cooling",
            "factor_oversizing",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [1000, 32, 1200, 30.75, 1.1],
            [1000, 31, 1200, 30.75, 1.1],
            [1000, 29, 1200, 30.75, 1.1],
            [1000, 28, 1200, 30.75, 1.1],
            [2500, 35, 1200, 30.75, 1.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        # Perform verification using run_test_verification_with_data
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        # Check results
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_plant_untested(self):
        points = [
            "load_plant_water_chilled",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_chilled",
            "temperature_drybulb_day_design_cooling",
            "factor_oversizing",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [1000, 32, 1200, 38, 1.1],
            [1000, 31, 1200, 38, 1.1],
            [1000, 29, 1200, 38, 1.1],
            [1000, 28, 1200, 38, 1.1],
            [2500, 35, 1200, 38, 1.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        # Perform verification using run_test_verification_with_data
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingWholePlant", df
        )

        # Check results
        results = list(verification_obj.result)
        self.assertTrue(
            results == ["Untested", "Untested", "Untested", "Untested", "Untested"]
        )
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)
