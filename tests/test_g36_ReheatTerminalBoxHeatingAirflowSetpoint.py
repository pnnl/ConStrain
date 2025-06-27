import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReheatTerminalBoxHeatingAirflowSetpoint(unittest.TestCase):
    tolerances = {"airflow": {"unit": "%", "types": {"general": 1}}}

    def test_reheat_terminal_box_heating_airflow_setpoint(self):
        points = [
            "mode_operation",
            "state_zone",
            "flow_volumetric_air_cool_max",
            "flow_volumetric_air_heat_max",
            "flow_volumetric_air_heat_min",
            "flow_volumetric_air_setpoint_min",
            "flow_volumetric_air_setpoint",
            "signal_heat",
            "temperature_air_room",
            "temperature_air_space_setpoint",
            "temperature_air_supply",
            "temperature_air_discharge",
            "temperature_air_discharge_setpoint",
        ]

        data = [
            ["occupied", "cooling", 100, 90, 20, 10, 90, 40, 25, 27, 13, 15, 16],
            ["occupied", "deadband", 100, 90, 20, 10, 90, 40, 25, 27, 13, 15, 16],
            ["occupied", "heating", 100, 90, 20, 10, 90, 40, 25, 27, 13, 15, 16],
            ["occupied", "heating", 100, 90, 20, 10, 8, 40, 25, 27, 13, 15, 16],
            ["occupied", "heating", 100, 90, 20, 10, 98, 40, 25, 27, 13, 15, 16],
            ["cooldown", "cooling", 100, 90, 20, 10, 90, 40, 25, 27, 13, 15, 16],
            ["setup", "heating", 100, 90, 20, 10, 80, 40, 25, 27, 13, 15, 16],
            ["setup", "heating", 100, 90, 20, 10, 0, 40, 25, 27, 13, 15, 16],
            ["setback", "heating", 100, 90, 20, 10, 98, 40, 25, 27, 13, 15, 16],
            ["setback", "heating", 100, 90, 20, 10, 8, 40, 25, 27, 13, 15, 16],
        ]

        expected_results = pd.Series(
            [
                "Untested",
                "Untested",
                False,
                False,
                False,
                "Untested",
                False,
                True,
                False,
                False,
            ]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxHeatingAirflowSetpoint",
                    df,
                    tolerances=self.tolerances,
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
