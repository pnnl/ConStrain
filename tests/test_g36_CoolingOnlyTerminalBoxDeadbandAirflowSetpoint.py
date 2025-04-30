import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint(unittest.TestCase):
    tolerances = {
        "airflow": {"unit": "m3/s", "types": {"general": 0.01}},
    }

    def test_g36_cooling_only_terminal_box_deadband_airflow_setpoint(self):
        points = [
            "mode_system",
            "state_zone",
            "flow_volumetric_air_setpoint_min",
            "flow_volumetric_air_setpoint",
        ]

        data = [
            ["occupied", "heating", 10, 90],
            ["occupied", "cooling", 10, 90],
            ["occupied", "deadband", 10, 10.1],
            ["occupied", "deadband", 10, 10.01],
            ["occupied", "deadband", 10, 10.001],
            ["cooldown", "deadband", 10, 10.001],
            ["cooldown", "deadband", 10, 0],
            ["occupied", "deadband", 10, 9.9],
            ["occupied", "deadband", 10, 9.99],
        ]

        expected_results = pd.Series(
            ["Untested", "Untested", False, True, True, False, True, False, True]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint",
                    df,
                    tolerances=self.tolerances,
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
