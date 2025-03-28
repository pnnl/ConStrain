import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReheatTerminalBoxCoolingAirflowSetpoint(unittest.TestCase):
    def test_g36_reheat_terminal_box_cooling_airflow_setpoint(self):
        points = [
            "operation_mode",
            "zone_state",
            "v_cool_max",
            "v_min",
            "v_spt",
            "heating_coil_command",
            "heating_coil_command_tol",
            "dat",
            "dat_min_spt",
        ]

        data = [
            ["occupied", "heating", 100, 10, 90, 0, 1, 14, 15],
            ["occupied", "cooling", 100, 10, 90, 0, 1, 14, 15],
            ["occupied", "cooling", 100, 10, 101, 0, 1, 14, 15],
            ["occupied", "cooling", 100, 10, 8, 0, 1, 14, 15],
            ["cooldown", "cooling", 100, 10, 8, 0, 1, 14, 15],
            ["Setup ", "cooling", 100, 10, 8, 0, 1, 14, 15],
            ["warmup", "cooling", 100, 10, 8, 0, 1, 14, 15],
            ["unoccupied", "cooling", 100, 10, 0, 0, 1, 14, 15],
            ["occupied", "cooling", 100, 10, 90, 0, 1, 16, 15],
            ["occupied", "cooling", 100, 10, 90, 2, 1, 16, 15],
        ]

        expected_results = pd.Series(
            ["Untested", True, False, False, True, True, False, True, True, False]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxCoolingAirflowSetpoint", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
