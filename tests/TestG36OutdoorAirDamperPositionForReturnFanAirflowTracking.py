import unittest, sys

sys.path.append("./src")
from lib_unit_test_runner import *
from library import *

import pandas as pd
import numpy as np


class TestG36OutdoorAirDamperPositionForReliefDamperOrFanConfig(unittest.TestCase):
    def test_return_air_damper_positiong(self):
        points = [
            "oa_p",
            "max_oa_p",
            "oa_p_tol",
        ]
        data = [
            [0.1, 1, 0.05],  # False
            [0.98, 1, 0.05],  # True
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "G36OutdoorAirDamperPositionForReturnFanAirflowTracking", df
        )

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([False, True])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
