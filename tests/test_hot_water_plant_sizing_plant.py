import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestHotWaterPlantSizingWholePlant(unittest.TestCase):
    def test_hot_water_plant_sizing_plant_pass(self):
        points = [
            "load_plant_water_hot",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_hot",
            "temperature_drybulb_day_design_heating",
            "factor_oversizing",
        ]

        timestamp = [
            datetime(2023, 12, 1, 11, 0, 0),
            datetime(2023, 12, 1, 12, 0, 0),
            datetime(2023, 12, 1, 13, 0, 0),
            datetime(2023, 12, 1, 14, 0, 0),
            datetime(2023, 12, 1, 15, 0, 0),
        ]
        data = [
            [1000, 3, 1200, 4, 1.1],
            [1000, 2, 1200, 4, 1.1],
            [1000, 2, 1200, 4, 1.1],
            [1000, 3, 1200, 4, 1.1],
            [1500, 4, 1200, 4, 1.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        # Perform verification using run_test_verification_with_data
        verification_obj = run_test_verification_with_data(
            "HotWaterPlantSizingWholePlant", df
        )

        # Check results
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_hot_water_plant_sizing_plant_fail(self):
        points = [
            "load_plant_water_hot",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_hot",
            "temperature_drybulb_day_design_heating",
            "factor_oversizing",
        ]

        timestamp = [
            datetime(2023, 12, 1, 11, 0, 0),
            datetime(2023, 12, 1, 12, 0, 0),
            datetime(2023, 12, 1, 13, 0, 0),
            datetime(2023, 12, 1, 14, 0, 0),
            datetime(2023, 12, 1, 15, 0, 0),
        ]
        data = [
            [1000, 3, 3000, 5, 1.1],
            [1000, 2, 3000, 4, 1.1],
            [1000, 2, 3000, 4, 1.1],
            [1000, 3, 3000, 4, 1.1],
            [2500, 4, 3000, 4, 1.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        # Perform verification using run_test_verification_with_data
        verification_obj = run_test_verification_with_data(
            "HotWaterPlantSizingWholePlant", df
        )

        # Check results
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_hot_water_plant_sizing_plant_untested(self):
        points = [
            "load_plant_water_hot",
            "temperature_air_outdoor",
            "capacity_nominal_plant_water_hot",
            "temperature_drybulb_day_design_heating",
            "factor_oversizing",
        ]

        timestamp = [
            datetime(2023, 12, 1, 11, 0, 0),
            datetime(2023, 12, 1, 12, 0, 0),
            datetime(2023, 12, 1, 13, 0, 0),
            datetime(2023, 12, 1, 14, 0, 0),
            datetime(2023, 12, 1, 15, 0, 0),
        ]
        data = [
            [1000, 3, 1200, 1, 1.1],
            [1000, 2, 1200, 1, 1.1],
            [1000, 2, 1200, 1, 1.1],
            [1000, 3, 1200, 1, 1.1],
            [2500, 4, 1200, 1, 1.1],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)

        # Perform verification using run_test_verification_with_data
        verification_obj = run_test_verification_with_data(
            "HotWaterPlantSizingWholePlant", df
        )

        # Check results
        results = list(verification_obj.result)
        self.assertTrue(
            results == ["Untested", "Untested", "Untested", "Untested", "Untested"]
        )
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)
