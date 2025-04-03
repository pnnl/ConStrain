import unittest
import numpy as np
import pandas as pd

from constrain.lib_unit_test_runner import *
from constrain.library import *
from scipy.stats import pearsonr


class TestDemandControlVentilation(unittest.TestCase):
    def test_dcv_positive_correlation(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["status_economizer"] = 0
        data["status_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool(), verification_obj.check_detail()["Message"]
        )

    def test_dcv_no_eco_good_time(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["status_economizer"] = 1
        data["status_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() == "Untested",
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_no_ahu_good_time(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["status_economizer"] = 1
        data["status_ahu"] = 0

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() == "Untested",
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_no_good_time(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["status_economizer"] = 0
        data["status_ahu"] = 0

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() == "Untested",
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_high_p(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(3, 4)
            if p < 0.05:
                continue
            break

        data["status_economizer"] = 0
        data["status_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() == "Untested",
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_low_corr(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 1)
            if corr > 0.29 or corr < 0 or p > 0.05:
                continue
            break

        data["status_economizer"] = 0
        data["status_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertFalse(
            verification_obj.check_bool(), verification_obj.check_detail()["Message"]
        )

    def test_dcv_negative_corr(self):
        points = [
            "flow_volumetric_air_outdoor",
            "status_ahu",
            "status_economizer",
            "number_occupants",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, -5)
            if corr > 0 or p > 0.05:
                continue
            break

        data["status_economizer"] = 0
        data["status_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertFalse(
            verification_obj.check_bool(), verification_obj.check_detail()["Message"]
        )

    def generate_correlated_data(self, num_sample, cov):
        cov = np.array([[6, cov], [cov, 6]])
        pts = np.random.multivariate_normal([20, 500], cov, size=num_sample)
        df = pd.DataFrame(
            pts, columns=["number_occupants", "flow_volumetric_air_outdoor"]
        )
        corr, p_value = pearsonr(
            df["number_occupants"], df["flow_volumetric_air_outdoor"]
        )
        return df, corr, p_value


if __name__ == "__main__":
    unittest.main()
