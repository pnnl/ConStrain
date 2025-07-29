import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd


class TestG36ReheatTerminalBoxDeadbandAirflowSetpoint(unittest.TestCase):
    tolerances = {
        "airflow": {"unit": "m3/s", "types": {"general": 0.01}},
        "damper": {"unit": "%", "general": 0.01, "types": {"command": 0.01}},
    }

    def test_g36_cooling_only_terminal_box_deadband_airflow_setpoint(self):
        points = [
            "mode_operation",
            "state_zone",
            "flow_volumetric_air_setpoint_min",
            "flow_volumetric_air_setpoint",
            "command_coil_heat",
            "temperature_air_discharge",
            "temperature_air_discharge_setpoint_min",
        ]

        data = [
            ["occupied", "heating", 10, 90, 0, 14, 15],
            ["occupied", "cooling", 10, 90, 0, 14, 15],
            ["occupied", "deadband", 10, 10.1, 0, 14, 15],
            ["occupied", "deadband", 10, 10.01, 0, 14, 15],
            ["occupied", "deadband", 10, 10.001, 0, 14, 15],
            ["cooldown", "deadband", 10, 10.001, 0, 14, 15],
            ["cooldown", "deadband", 10, 0, 0, 14, 15],
            ["occupied", "deadband", 10, 9.9, 0, 14, 15],
            ["occupied", "deadband", 10, 9.99, 0, 14, 15],
            ["occupied", "deadband", 10, 10.01, 0, 16, 15],
            ["occupied", "deadband", 10, 10.01, 2, 16, 15],
        ]

        expected_results = pd.Series(
            [
                "Untested",
                "Untested",
                False,
                True,
                True,
                False,
                True,
                False,
                True,
                True,
                False,
            ]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxDeadbandAirflowSetpoint",
                    df,
                    tolerances=self.tolerances,
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
