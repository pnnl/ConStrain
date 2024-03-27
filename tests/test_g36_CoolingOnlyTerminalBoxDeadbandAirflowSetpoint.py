import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint(unittest.TestCase):
    def test_minoa_economizer_pass_untest_fail(self):
        points = ["operation_mode", "zone_state", "v_min*", "v_spt", "v_spt_tol"]

        data = [
            ["occupied", "heating", 10, 90, 0.01],
            ["occupied", "cooling", 10, 90, 0.01],
            ["occupied", "deadband", 10, 10.1, 0.01],
            ["occupied", "deadband", 10, 10.01, 0.01],
            ["occupied", "deadband", 10, 10.001, 0.01],
            ["cooldown", "deadband", 10, 10.001, 0.01],
            ["cooldown", "deadband", 10, 0, 0.01],
            ["occupied", "deadband", 10, 9.9, 0.01],
            ["occupied", "deadband", 10, 9.99, 0.01],
        ]

        expected_results = pd.Series(
            [np.nan, np.nan, False, True, True, False, True, False, True]
        )

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint", df
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
