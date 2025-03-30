import unittest, sys

sys.path.append("./constrain")
from lib_unit_test_runner import *
from library import *

import pandas as pd


class TestAutomaticOADamperControl(unittest.TestCase):
    def test_automatic_oa_damper_control(self):
        tolerances = {
            "airflow": {
                "unit": "m3/s",
                "types": {"exhaust_air": 50, "outdoor_air": 50, "general": 50},
            },
            "ratio": {"unit": "%", "types": {"occupancy": 0.001, "general": 0.001}},
        }
        points = [
            "number_occupants",
            "status_economizer",
            "flow_volumetric_air_outdoor",
            "flow_volumetric_air_exhaust",
        ]
        data = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1000],
            [0, 0, 0, 1000],
            [0, 0, 1000, 1000],
            [1, 1, 0, 0],
            [1, 0, 1, 0],
            [1, 1, 1000, 0],
        ]
        df = pd.DataFrame(data, columns=points)

        results = list(
            run_test_verification_with_data(
                "AutomaticOADamperControl", df, tolerances=tolerances
            ).result
        )
        expected_results = [
            "Untested",
            True,
            False,
            False,
            False,
            "Untested",
            "Untested",
            "Untested",
        ]

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
