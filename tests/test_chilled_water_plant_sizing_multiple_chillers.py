import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterPlantSizingMultipleChillers(unittest.TestCase):
    def test_chilled_water_plant_sizing_multiple_chiller_pass(self):
        points = [
            "status_chiller",
            "load_plant_water_chilled",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [0, 80],
            [1, 85],
            [1, 90],
            [1, 90],
            [1, 95],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingMultipleChillers", df
        )

        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_multiple_chiller_fail(self):
        points = [
            "status_chiller",
            "load_plant_water_chilled",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [0, 80],
            [0, 85],
            [0, 90],
            [0, 90],
            [1, 95],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterPlantSizingMultipleChillers", df
        )

        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)
