import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36CoolingOnlyTerminalBoxCoolingAirflowSetpoint(unittest.TestCase):
    def test_minoa_economizer_pass_untest_fail(self):
        points = ["operation_mode", "zone_state", "v_cool_max", "v_min*", "v_spt"]

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
            [np.nan, True, False, False, True, True, False, True]
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
