import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36CoolingOnlyTerminalBoxHeatingAirflowSetpoint(unittest.TestCase):
    def test_cooling_only_terminal_box_heating_airflow_setpoint(self):
        points = [
            "mode_system",
            "state_zone",
            "v_cool_max",
            "v_heat_max",
            "v_min",
            "v_sp",
        ]

        data = [
            ["occupied", "cooling", 100, 90, 10, 90],
            ["occupied", "deadband", 100, 100, 110, 90],
            ["occupied", "heating", 100, 90, 10, 80],
            ["occupied", "heating", 100, 90, 10, 8],
            ["occupied", "heating", 100, 90, 10, 98],
            ["cooldown", "cooling", 100, 90, 10, 90],
            ["setup", "heating", 100, 90, 10, 80],
            ["setup", "heating", 100, 90, 10, 0],
            ["setback", "heating", 100, 90, 10, 98],
            ["setback", "heating", 100, 90, 10, 8],
            ["wrong operation mode", "heating", 100, 90, 10, 8],
        ]

        expected_results = pd.Series(
            [
                "Untested",
                "Untested",
                True,
                False,
                False,
                "Untested",
                False,
                True,
                True,
                True,
                "Untested",
            ]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36CoolingOnlyTerminalBoxHeatingAirflowSetpoint", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
