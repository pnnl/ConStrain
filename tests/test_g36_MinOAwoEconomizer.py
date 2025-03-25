import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36MinOAwEconomizer(unittest.TestCase):
    def test_minoa_wo_economizer_pass_untested_low(self):
        points = [
            "t_oa",
            "t_oa_economizer_high_limit",
            "pos_damper_oa",
            "pos_damper_ra",
            "v_oa",
            "v_oa_min_sp",
            "mode_system",
        ]

        timestamp = [
            datetime(2023, 2, 1, 10, 30, 30),
            datetime(2023, 2, 1, 11, 0, 30),
            datetime(2023, 2, 1, 11, 35, 0),
            datetime(2023, 2, 1, 11, 45, 0),
            datetime(2023, 2, 1, 12, 45, 0),
        ]
        data = [
            [25, 24, 0, 20, 1500, 2000, "occupied"],
            [26, 24, 0, 20, 1900, 2000, "occupied"],
            [27, 24, 99.2, 0.5, 1500, 2000, "occupied"],
            [27, 24, 100, 0, 1600, 2000, "occupied"],
            [20, 24, 100, 0, 1600, 2000, "occupied"],
        ]

        expected_results = pd.Series(["Untested", "Untested", True, True, "Untested"])

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(run_test_verification_with_data("G36MinOAwoEconomizer", df).result)
        )

        self.assertTrue(results.equals(expected_results))

    def test_minoa_wo_economizer_fail_untested_low(self):
        points = [
            "t_oa",
            "t_oa_economizer_high_limit",
            "pos_damper_oa",
            "pos_damper_ra",
            "v_oa",
            "v_oa_min_sp",
            "mode_system",
        ]

        timestamp = [
            datetime(2023, 2, 1, 10, 30, 30),
            datetime(2023, 2, 1, 11, 0, 30),
            datetime(2023, 2, 1, 11, 35, 0),
            datetime(2023, 2, 1, 11, 45, 0),
            datetime(2023, 2, 1, 12, 45, 0),
        ]
        data = [
            [25, 24, 0, 20, 1500, 2000, "occupied"],
            [26, 24, 0, 20, 1900, 2000, "occupied"],
            [27, 24, 0, 20, 1500, 2000, "occupied"],
            [27, 24, 0, 20, 1600, 2000, "occupied"],
            [20, 24, 0, 20, 1600, 2000, "occupied"],
        ]

        expected_results = pd.Series(["Untested", "Untested", False, False, "Untested"])

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(run_test_verification_with_data("G36MinOAwoEconomizer", df).result)
        )

        self.assertTrue(results.equals(expected_results))

    def test_minoa_wo_economizer_pass_untested_high(self):
        points = [
            "t_oa",
            "t_oa_economizer_high_limit",
            "pos_damper_oa",
            "pos_damper_ra",
            "v_oa",
            "v_oa_min_sp",
            "mode_system",
        ]

        timestamp = [
            datetime(2023, 2, 1, 10, 30, 30),
            datetime(2023, 2, 1, 11, 0, 30),
            datetime(2023, 2, 1, 11, 35, 0),
            datetime(2023, 2, 1, 11, 45, 0),
            datetime(2023, 2, 1, 12, 45, 0),
        ]
        data = [
            [25, 24, 0, 20, 2500, 2000, "occupied"],
            [26, 24, 0, 20, 2900, 2000, "occupied"],
            [27, 24, 0, 100, 2500, 2000, "occupied"],
            [27, 24, 0.5, 99.5, 2600, 2000, "occupied"],
            [20, 24, 100, 0, 2600, 2000, "occupied"],
        ]

        expected_results = pd.Series(["Untested", "Untested", True, True, "Untested"])

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(run_test_verification_with_data("G36MinOAwoEconomizer", df).result)
        )

        self.assertTrue(results.equals(expected_results))

    def test_minoa_wo_economizer_fail_untested_high(self):
        points = [
            "t_oa",
            "t_oa_economizer_high_limit",
            "pos_damper_oa",
            "pos_damper_ra",
            "v_oa",
            "v_oa_min_sp",
            "mode_system",
        ]

        timestamp = [
            datetime(2023, 2, 1, 10, 30, 30),
            datetime(2023, 2, 1, 11, 0, 30),
            datetime(2023, 2, 1, 11, 35, 0),
            datetime(2023, 2, 1, 11, 45, 0),
            datetime(2023, 2, 1, 12, 45, 0),
        ]
        data = [
            [25, 24, 0, 20, 2500, 2000, "occupied"],
            [26, 24, 0, 20, 2900, 2000, "occupied"],
            [27, 24, 0, 100, 2500, 2000, "occupied"],
            [27, 24, 0, 20, 2600, 2000, "occupied"],
            [20, 24, 0, 20, 2600, 2000, "occupied"],
        ]

        expected_results = pd.Series(["Untested", "Untested", True, False, "Untested"])

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(run_test_verification_with_data("G36MinOAwoEconomizer", df).result)
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
