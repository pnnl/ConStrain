import sys
import unittest

sys.path.append("./constrain")
import pandas as pd
from lib_unit_test_runner import *


class TestDHWTankTemperature(unittest.TestCase):
    def test_dhw_tank_temperature(self):
        points = [
            "T_dhw",
            "T_dhw_deadband",
            "T_dhw_design_parameter",
        ]

        data = [
            [50, 2.0, 49],  # Pass - dhw tank temp is within the deadband range
            [50, 2.0, 51],  # Pass - dhw tank temp is within the deadband range
            [50, 2.0, 47],  # Fail - dhw tank temp is out of the deadband range
            [50, 2.0, 53],  # Fail - dhw tank temp is out of the deadband range
        ]

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data("DHW_tank_temperature", df)

        results = pd.Series(list(verification_obj.result))
        expected_results = pd.Series([True, True, False, False])
        self.assertTrue(results.equals(expected_results))

        binary_result = verification_obj.check_bool()
        self.assertFalse(binary_result)
