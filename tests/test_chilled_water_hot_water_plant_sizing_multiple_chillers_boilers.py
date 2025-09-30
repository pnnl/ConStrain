import datetime
import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *
from library import *


class TestChilledWaterHotWaterPlantSizingMultipleChillersBoilers(unittest.TestCase):
    def test_chilled_water_hot_water_plant_sizing_multiple_chiller_boiler_pass_chiller(
        self,
    ):
        points = [
            "status_equipment",
            "load_plant_water",
            "system_type",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [0, 80, "Chiller"],
            [1, 85, "Chiller"],
            [1, 90, "Chiller"],
            [1, 90, "Chiller"],
            [1, 95, "Chiller"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingMultipleChillersBoilers", df
        )

        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chilled_water_hot_water_plant_sizing_multiple_chiller_boiler_fail_chiller(
        self,
    ):
        points = [
            "status_equipment",
            "load_plant_water",
            "system_type",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [0, 80, "Chiller"],
            [0, 85, "Chiller"],
            [0, 90, "Chiller"],
            [0, 90, "Chiller"],
            [1, 95, "Chiller"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingMultipleChillersBoilers", df
        )

        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)

    def test_chilled_water_hot_water_plant_sizing_multiple_chiller_boiler_pass_boiler(
        self,
    ):
        points = [
            "status_equipment",
            "load_plant_water",
            "system_type",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [0, 80, "Boiler"],
            [1, 85, "Boiler"],
            [1, 90, "Boiler"],
            [1, 90, "Boiler"],
            [1, 95, "Boiler"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingMultipleChillersBoilers", df
        )

        binaryflag = verification_obj.check_bool()
        self.assertTrue(binaryflag)

    def test_chilled_water_hot_water_plant_sizing_multiple_chiller_boiler_fail_boiler(
        self,
    ):
        points = [
            "status_equipment",
            "load_plant_water",
            "system_type",
        ]

        timestamp = [
            datetime(2023, 8, 1, 11, 0, 0),
            datetime(2023, 8, 1, 12, 0, 0),
            datetime(2023, 8, 1, 13, 0, 0),
            datetime(2023, 8, 1, 14, 0, 0),
            datetime(2023, 8, 1, 15, 0, 0),
        ]
        data = [
            [0, 80, "Boiler"],
            [0, 85, "Boiler"],
            [0, 90, "Boiler"],
            [0, 90, "Boiler"],
            [1, 95, "Boiler"],
        ]
        df = pd.DataFrame(data, columns=points, index=timestamp)
        verification_obj = run_test_verification_with_data(
            "ChilledWaterHotWaterPlantSizingMultipleChillersBoilers", df
        )

        binaryflag = verification_obj.check_bool()
        self.assertFalse(binaryflag)
