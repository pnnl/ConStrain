import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReheatTerminalBoxCoolingAirflowSetpoint(unittest.TestCase):
    tolerances = {"coil": {"unit": "%", "types": {"command": 0.05}}}

    def test_g36_reheat_terminal_box_cooling_airflow_setpoint(self):
        points = [
            "mode_system",
            "state_zone",
            "flow_volumetric_air_cool_max",
            "flow_volumetric_air_setpoint_min",
            "flow_volumetric_air_setpoint",
            "command_coil_heat",
            "temperature_air_discharge",
            "temperature_air_discharge_setpoint_min",
        ]

        data = [
            ["occupied", "heating", 100, 10, 90, 0, 14, 15],
            ["occupied", "cooling", 100, 10, 90, 0, 14, 15],
            ["occupied", "cooling", 100, 10, 101, 0, 14, 15],
            ["occupied", "cooling", 100, 10, 8, 0, 14, 15],
            ["cooldown", "cooling", 100, 10, 8, 0, 14, 15],
            ["Setup ", "cooling", 100, 10, 8, 0, 14, 15],
            ["warmup", "cooling", 100, 10, 8, 0, 14, 15],
            ["unoccupied", "cooling", 100, 10, 0, 0, 14, 15],
            ["occupied", "cooling", 100, 10, 90, 0, 16, 15],
            ["occupied", "cooling", 100, 10, 90, 2, 16, 15],
        ]

        expected_results = pd.Series(
            ["Untested", True, False, False, True, True, False, True, True, False]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxCoolingAirflowSetpoint",
                    df,
                    tolerances=self.tolerances,
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
