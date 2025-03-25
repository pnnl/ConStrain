import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReheatTerminalBoxDeadbandAirflowSetpoint(unittest.TestCase):
    def test_g36_reheat_terminal_box_deadband_airflow_setpoint(self):
        points = [
            "mode_system",
            "state_zone",
            "v_min",
            "v_sp",
            "tol_v",
            "cmd_coil_heat",
            "tol_cmd_coil_heat",
            "t_discharge",
            "t_discharge_min_sp",
        ]

        data = [
            ["occupied", "heating", 10, 90, 0.01, 0, 1, 14, 15],
            ["occupied", "cooling", 10, 90, 0.01, 0, 1, 14, 15],
            ["occupied", "deadband", 10, 10.1, 0.01, 0, 1, 14, 15],
            ["occupied", "deadband", 10, 10.01, 0.01, 0, 1, 14, 15],
            ["occupied", "deadband", 10, 10.001, 0.01, 0, 1, 14, 15],
            ["cooldown", "deadband", 10, 10.001, 0.01, 0, 1, 14, 15],
            ["cooldown", "deadband", 10, 0, 0.01, 0, 1, 14, 15],
            ["occupied", "deadband", 10, 9.9, 0.01, 0, 1, 14, 15],
            ["occupied", "deadband", 10, 9.99, 0.01, 0, 1, 14, 15],
            ["occupied", "deadband", 10, 10.01, 0.01, 0, 1, 16, 15],
            ["occupied", "deadband", 10, 10.01, 0.01, 2, 1, 16, 15],
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
                    "G36ReheatTerminalBoxDeadbandAirflowSetpoint", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
