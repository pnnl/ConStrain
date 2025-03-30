import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36SupplyAirTemperatureSetpointg(unittest.TestCase):
    tolerances = {
        "temperature": {
            "unit": "deg. C",
            "types": {
                "supply_air": 0.2,
                "general": 0.2,
            },
        }
    }

    def test_heating_cooling(self):
        points = [
            "mode_operation",
            "temperature_air_supply_max",
            "temperature_air_supply_setpoint_cool_max",
            "temperature_air_supply_setpoint_cool_min",
            "temperature_air_outdoor",
            "temperature_air_outdoor_supply_min",
            "temperature_air_outdoor_supply_max",
            "temperature_air_supply_setpoint",
        ]
        data = [
            ["cooldown", 14, 13, 12, 9, 10, 21, 12],  # False
            ["cooldown", 14, 16, 12, 9, 10, 21, 11.9],  # True
            ["warmup", 14, 16, 12, 9, 10, 21, 35.1],  # True
            ["setback", 14, 16, 12, 9, 10, 21, 34.9],  # True
            ["warmup", 14, 16, 12, 9, 10, 21, 32],  # False
            ["setback", 14, 16, 12, 9, 10, 21, 42],  # False
            ["occupied", 14, 16, 12, 9, 10, 21, 14],  # True
            ["occupied", 14, 16, 12, 9, 10, 21, 15],  # False
            ["occupied", 14, 16, 12, 22, 10, 21, 11.9],  # True
            ["occupied", 14, 16, 12, 22, 10, 21, 15],  # False
            ["occupied", 14, 16, 12, 16, 10, 21, 12.9],  # True
            ["occupied", 14, 16, 12, 16, 10, 21, 12.5],  # False
            ["setup", 14, 16, 12, 9, 10, 21, 14],  # True
            ["setup", 14, 16, 12, 9, 10, 21, 15],  # False
            ["setup", 14, 16, 12, 22, 10, 21, 11.9],  # True
            ["setup", 14, 16, 12, 22, 10, 21, 15],  # True
            ["setup", 14, 16, 12, 16, 10, 21, 12.9],  # True
            ["setup", 14, 16, 12, 16, 10, 21, 12.5],  # False
            ["wrong", 14, 16, 12, 16, 10, 21, 12.5],  # Untested
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36SupplyAirTemperatureSetpoint", df, tolerances=self.tolerances
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series(
            [
                False,
                True,
                True,
                True,
                False,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                True,
                False,
                "Untested",
            ]
        )
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
