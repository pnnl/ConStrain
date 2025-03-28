import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36CoolingOnlyTerminalBoxHeatingAirflowSetpoint(unittest.TestCase):
    def test_cooling_only_terminal_box_heating_airflow_setpoint(self):
        points = [
            "operation_mode",
            "zone_state",
            "v_cool_max",
            "v_heat_max",
            "v_heat_min",
            "v_min",
            "v_spt",
            "v_spt_tol",
            "heating_loop_output",
            "room_temp",
            "space_temp_spt",
            "ahu_sat_spt",
            "dat",
            "dat_spt",
        ]

        data = [
            ["occupied", "cooling", 100, 90, 20, 10, 90, 1, 40, 25, 27, 13, 15, 16],
            ["occupied", "deadband", 100, 90, 20, 10, 90, 1, 40, 25, 27, 13, 15, 16],
            ["occupied", "heating", 100, 90, 20, 10, 90, 1, 40, 25, 27, 13, 15, 16],
            ["occupied", "heating", 100, 90, 20, 10, 8, 1, 40, 25, 27, 13, 15, 16],
            ["occupied", "heating", 100, 90, 20, 10, 98, 1, 40, 25, 27, 13, 15, 16],
            ["cooldown", "cooling", 100, 90, 20, 10, 90, 1, 40, 25, 27, 13, 15, 16],
            ["setup", "heating", 100, 90, 20, 10, 80, 1, 40, 25, 27, 13, 15, 16],
            ["setup", "heating", 100, 90, 20, 10, 0, 1, 40, 25, 27, 13, 15, 16],
            ["setback", "heating", 100, 90, 20, 10, 98, 1, 40, 25, 27, 13, 15, 16],
            ["setback", "heating", 100, 90, 20, 10, 8, 1, 40, 25, 27, 13, 15, 16],
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
                    "G36ReheatTerminalBoxHeatingAirflowSetpoint", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
