import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36CoolingOnlyTerminalBoxCoolingAirflowSetpoint(unittest.TestCase):
    def test_g36_cooling_only_terminal_box_cooling_airflow_setpoint(self):
        points = [
            "mode_operation",
            "state_zone",
            "flow_volumetric_air_cool_max",
            "flow_volumetric_air_setpoint_min",
            "flow_volumetric_air_setpoint",
        ]

        data = [
            ["occupied", "heating", 100, 10, 90],
            ["occupied", "cooling", 100, 10, 90],
            ["occupied", "cooling", 100, 10, 101],
            ["occupied", "cooling", 100, 10, 8],
            ["cooldown", "cooling", 100, 10, 8],
            ["Setup ", "cooling", 100, 10, 8],
            ["warmup", "cooling", 100, 10, 8],
            ["unoccupied", "cooling", 100, 10, 0],
        ]

        expected_results = pd.Series(
            ["Untested", True, False, False, True, True, False, True]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36CoolingOnlyTerminalBoxCoolingAirflowSetpoint", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
