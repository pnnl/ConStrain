import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *

import pandas as pd


class TestG36SimultaneousHeatingCooling(unittest.TestCase):
    tolerances = {
        "load": {
            "unit": "W",
            "types": {
                "coil": 0.0,
            },
        },
    }

    def test_heating_cooling(self):
        points = ["output_coil_heating", "output_coil_cooling"]
        data = [[1000, 0], [1000, 1000], [0, 1000]]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36SimultaneousHeatingCooling", df, tolerances=self.tolerances
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([True, False, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
