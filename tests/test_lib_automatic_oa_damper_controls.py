import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestAutomaticOADamperControl(unittest.TestCase):
    def test_automatic_oa_damper_control(self):
        points = ["o", "eco_onoff", "m_oa", "m_ea", "tol_o", "tol_m_oa", "tol_m_ea"]
        data = [
            [1, 0, 0, 0, 0.001, 50, 50],
            [0, 1, 0, 0, 0.001, 50, 50],
            [0, 0, 1000, 0, 0.001, 50, 50],
            [0, 0, 0, 1000, 0.001, 50, 50],
            [0, 0, 1000, 1000, 0.001, 50, 50],
            [1, 1, 0, 0, 0.001, 50, 50],
            [1, 0, 1, 0, 0.001, 50, 50],
            [1, 1, 1000, 0, 0.001, 50, 50],
        ]
        df = pd.DataFrame(data, columns=points)

        results = list(
            run_test_verification_with_data("AutomaticOADamperControl", df).result
        )
        expected_results = [np.nan, True, False, False, False, np.nan, np.nan, np.nan]

        # Perform verification
        for i in range(len(data[0])):
            self.assertTrue(results[i] is expected_results[i])

        # Print out results
        df["results"] = results
        df["expected_results"] = expected_results
        df.to_csv(
            "./tests/outputs/TestAutomaticOADamperControl_test_automatic_oa_damper_control.csv"
        )


if __name__ == "__main__":
    unittest.main()
