import unittest, sys
import datetime

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36TerminalBoxVAVDamperTracking(unittest.TestCase):
    tolerances = {
        "airflow": {
            "unit": "m3/s",
            "types": {
                "general": 50,
            },
        },
        "damper": {"unit": "%", "types": {"command": 0.01, "general": 0.01}},
    }

    def test_g36_terminal_box_vav_damper_tracking0(self):
        points = ["vav_damper_command", "v", "v_spt"]

        timestamp = [
            datetime(2024, 2, 1, 0, 5, 0),
            datetime(2024, 2, 1, 0, 10, 0),
            datetime(2024, 2, 1, 0, 15, 0),
            datetime(2024, 2, 1, 1, 5, 0),
            datetime(2024, 2, 1, 1, 15, 0),
            datetime(2024, 2, 1, 1, 25, 0),
            datetime(2024, 2, 1, 1, 35, 0),
        ]

        data = [
            [90, 1110, 1100],
            [90, 1060, 1100],
            [95, 1000, 1100],
            [95, 1000, 1100],
            [95, 1000, 1100],
            [95, 1000, 1100],
            [99.5, 1000, 1100],
        ]

        expected_results = pd.Series(
            [True, True, True, "Untested", "Untested", False, True]
        )

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36TerminalBoxVAVDamperTracking", df, tolerances=self.tolerances
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))

    def test_g36_terminal_box_vav_damper_tracking1(self):
        points = ["vav_damper_command", "v", "v_spt"]

        timestamp = [
            datetime(2024, 2, 1, 0, 5, 0),
            datetime(2024, 2, 1, 0, 15, 0),
            datetime(2024, 2, 1, 0, 16, 0),
            datetime(2024, 2, 1, 1, 5, 0),
            datetime(2024, 2, 1, 1, 15, 0),
            datetime(2024, 2, 1, 1, 25, 0),
            datetime(2024, 2, 1, 1, 45, 0),
        ]

        data = [
            [90, 1110, 1100],
            [95, 1200, 1100],
            [95, 1200, 1100],
            [95, 1200, 1100],
            [5, 1200, 1100],
            [5, 1300, 1100],
            [0, 1300, 1100],
        ]

        expected_results = pd.Series(
            [True, True, "Untested", "Untested", "Untested", False, True]
        )

        df = pd.DataFrame(data, columns=points, index=timestamp)

        results = pd.Series(
            list(
                run_test_verification_with_data(
                    "G36TerminalBoxVAVDamperTracking", df, tolerances=self.tolerances
                ).result
            )
        )

        self.assertTrue(results.equals(expected_results))


if __name__ == "__main__":
    unittest.main()
