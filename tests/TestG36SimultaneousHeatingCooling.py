import unittest, sys
import datetime

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import json
import pandas as pd
import numpy as np


class TestG36SimultaneousHeatingCooling(unittest.TestCase):
    def test_heating_cooling(self):
        points = ["heating_output", "cooling_output"]
        data = [[1000, 0], [1000, 1000], [0, 1000]]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36SimultaneousHeatingCooling", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([True, False, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
