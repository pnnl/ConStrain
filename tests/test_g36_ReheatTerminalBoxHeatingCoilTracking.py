import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36ReheatTerminalBoxHeatingCoilTracking(unittest.TestCase):

    def test_g36_reheat_terminal_box_heating_coil_tracking0(self):

        points = [
            "operation_mode",
            "heating_coil_command",
            "dat",
            "dat_spt",
            "dat_tracking_tol",
        ]

        timestamp = [
            datetime(2024, 3, 10, 0, 5, 0),
            datetime(2024, 3, 10, 0, 10, 0),
            datetime(2024, 3, 10, 0, 15, 0),
            datetime(2024, 3, 10, 1, 5, 0),
            datetime(2024, 3, 10, 1, 15, 0),
            datetime(2024, 3, 10, 1, 25, 0),
            datetime(2024, 3, 10, 1, 35, 0),
            datetime(2024, 3, 10, 1, 45, 0),
            datetime(2024, 3, 10, 2, 45, 0),
        ]

        data = [
            ["heating", 90, 22, 22, 1.5],
            ["heating", 90, 21, 22, 1.5],
            ["heating", 95, 20, 22, 1.5],
            ["heating", 95, 20, 22, 1.5],
            ["heating", 95, 19, 22, 1.5],
            ["heating", 95, 20, 22, 1.5],
            ["heating", 99.5, 20, 22, 1.5],
            ["cooling", 95, 19, 22, 1.5],
            ["deadband", 95, 20, 22, 1.5],
        ]

        expected_results = pd.Series(
            [
                True,
                True,
                True,
                "Untested",
                "Untested",
                False,
                True,
                "Untested",
                "Untested",
            ]
        )

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxHeatingCoilTracking", df
                ).result
            )
        )
        print(results)

        self.assertTrue(results.equals(expected_results))

    def test_g36_reheat_terminal_box_heating_coil_tracking1(self):
        points = [
            "operation_mode",
            "heating_coil_command",
            "dat",
            "dat_spt",
            "dat_tracking_tol",
        ]

        timestamp = [
            datetime(2024, 3, 10, 0, 5, 0),
            datetime(2024, 3, 10, 0, 10, 0),
            datetime(2024, 3, 10, 0, 15, 0),
            datetime(2024, 3, 10, 1, 5, 0),
            datetime(2024, 3, 10, 1, 15, 0),
            datetime(2024, 3, 10, 1, 25, 0),
            datetime(2024, 3, 10, 1, 35, 0),
            datetime(2024, 3, 10, 1, 45, 0),
            datetime(2024, 3, 10, 2, 45, 0),
        ]

        data = [
            ["heating", 90, 22, 22, 1.5],
            ["heating", 90, 24, 22, 1.5],
            ["heating", 95, 24, 22, 1.5],
            ["heating", 95, 24, 22, 1.5],
            ["heating", 90, 24, 22, 1.5],
            ["heating", 5, 24, 22, 1.5],
            ["heating", 0.5, 24, 22, 1.5],
            ["cooling", 95, 19, 22, 1.5],
            ["deadband", 95, 20, 22, 1.5],
        ]

        expected_results = pd.Series(
            [
                True,
                True,
                "Untested",
                "Untested",
                False,
                False,
                True,
                "Untested",
                "Untested",
            ]
        )

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36ReheatTerminalBoxHeatingCoilTracking", df
                ).result
            )
        )
        print(results)

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
