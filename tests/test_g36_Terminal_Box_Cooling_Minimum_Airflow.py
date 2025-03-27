import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36TerminalBoxCoolingMinimumAirflow(unittest.TestCase):
    def test_g36_terminal_box_cooling_minimum_airflow(self):
        points = [
            "mode_system",
            "state_zone",
            "flow_volumetric_air_setpoint_min",
            "temperature_air_supply_setpoint",
            "flow_volumetric_air_setpoint",
            "tol_v",
            "temperature_air_room",
        ]

        data = [
            ["occupied", "heating", 10, 13, 90, 0.01, 10],
            ["occupied", "cooling", 10, 13, 90, 0.01, 15],
            ["occupied", "cooling", 10, 13, 10.1, 0.01, 10],
            ["occupied", "cooling", 10, 13, 10.01, 0.01, 10],
            ["occupied", "cooling", 10, 13, 10.001, 0.01, 10],
            ["cooldown", "cooling", 10, 13, 10.001, 0.01, 10],
            ["cooldown", "cooling", 10, 13, 0, 0.01, 10],
            ["occupied", "cooling", 10, 13, 11.9, 0.01, 10],
            ["occupied", "cooling", 10, 13, 9.99, 0.01, 10],
        ]

        expected_results = pd.Series(
            ["Untested", "Untested", False, True, True, False, True, False, True]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36TerminalBoxCoolingMinimumAirflow", df
                ).result
            )
        )
        print(results)
        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
