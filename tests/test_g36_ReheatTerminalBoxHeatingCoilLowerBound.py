import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReheatTerminalBoxHeatingCoilLowerBound(unittest.TestCase):
    def test_g36_reheat_terminal_box_heating_coil_lower_bound(self):
        points = [
            "mode_operation",
            "command_coil_heat",
            "temperature_air_discharge",
        ]

        data = [
            ["occupied", 50, 10],
            ["occupied", 0, 11],
            ["occupied", 95, 9],
            ["occupied", 100, 9],
            ["cooldown", 90, 11],
            ["cooldown", 90, 8],
            ["setup", 50, 8],
            ["unoccupied", 0, 20],
        ]

        expected_results = pd.Series(
            [True, True, False, True, "Untested", "Untested", "Untested", "Untested"]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxHeatingCoilLowerBound", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
