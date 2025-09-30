import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterHotWaterPlantSizingChillerBoilerShortCycling(unittest.TestCase):
    def test_chilled_water_plant_sizing_chiller_short_cycling_pass(
        self,
    ):
        points = [
            "status_equipment",
            "cycles_number_maximum",
        ]
        timestamp = [
            datetime(2023, 11, 1, 9, 0),
            datetime(2023, 11, 1, 9, 35),
            datetime(2023, 11, 1, 9, 45),
            datetime(2023, 11, 1, 10, 0),
            datetime(2023, 11, 1, 10, 15),
            datetime(2023, 11, 1, 11, 15),
            datetime(2023, 11, 1, 11, 16),
            datetime(2023, 11, 1, 11, 17),
            datetime(2023, 11, 1, 11, 20),
            datetime(2023, 11, 1, 11, 25),
            datetime(2023, 11, 1, 11, 59),
        ]
        data = [
            [0, 3],
            [1, 3],
            [1, 3],
            [0, 3],
            [1, 3],
            [0, 3],
            [0, 3],
            [1, 3],
            [1, 3],
            [1, 3],
            [0, 3],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingChillerBoilerShortCycling", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chilled_water_plant_sizing_chiller_short_cycling_fail(
        self,
    ):
        points = [
            "status_equipment",
            "cycles_number_maximum",
        ]
        timestamp = [
            datetime(2023, 11, 1, 9, 0),
            datetime(2023, 11, 1, 9, 35),
            datetime(2023, 11, 1, 9, 45),
            datetime(2023, 11, 1, 10, 0),
            datetime(2023, 11, 1, 10, 15),
            datetime(2023, 11, 1, 11, 15),
            datetime(2023, 11, 1, 11, 16),
            datetime(2023, 11, 1, 11, 17),
            datetime(2023, 11, 1, 11, 20),
            datetime(2023, 11, 1, 11, 25),
            datetime(2023, 11, 1, 11, 35),
            datetime(2023, 11, 1, 11, 45),
            datetime(2023, 11, 1, 11, 50),
            datetime(2023, 11, 1, 11, 59),
        ]
        data = [
            [0, 3],
            [1, 3],
            [1, 3],
            [0, 3],
            [1, 3],
            [0, 3],
            [0, 3],
            [1, 3],
            [0, 3],
            [1, 3],
            [0, 3],
            [1, 3],
            [0, 3],
            [0, 3],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingChillerBoilerShortCycling", df
        )

        results = pd.Series(list(verification_obj.result))
        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)
