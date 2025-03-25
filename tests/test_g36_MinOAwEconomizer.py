import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36MinOAwEconomizer(unittest.TestCase):
    def test_minoa_economizer_pass_untest_fail(self):
        points = [
            "t_oa",
            "t_economizer_limit",
            "pos_damper_oa",
            "pos_damper_oa_min",
            "v_oa",
            "v_oa_min_sp",
            "mode_system",
        ]

        data = [
            [20, 24, 25, 20, 2000, 1500, "occupied"],
            [20, 24, 25, 20, 2000, 1500, "unoccupied"],
            [25, 24, 25, 20, 2000, 1500, "unoccupied"],
            [20, 24, 19, 20, 2000, 1500, "occupied"],
            [20, 24, 25, 20, 1400, 1500, "occupied"],
            [20, 24, 15, 20, 1000, 1500, "occupied"],
        ]

        df = pd.DataFrame(data, columns=points)

        results = pd.Series(
            list(run_test_verification_with_data("G36MinOAwEconomizer", df).result)
        )

        expected_results = pd.Series(
            [True, "Untested", "Untested", False, False, False]
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
