import unittest
import numpy as np
import pandas as pd

from constrain.lib_unit_test_runner import *
from constrain.library import *
from scipy.stats import pearsonr


class TestDemandControlVentilation(unittest.TestCase):
    def test_dcv_positive_correlation(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["s_eco"] = 0
        data["s_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool(), verification_obj.check_detail()["Message"]
        )

    def test_dcv_no_eco_good_time(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["s_eco"] = 1
        data["s_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() is np.nan,
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_no_ahu_good_time(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["s_eco"] = 1
        data["s_ahu"] = 0

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() is np.nan,
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_no_good_time(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 5)
            if corr < 0.4 or p > 0.04:
                continue
            break

        data["s_eco"] = 0
        data["s_ahu"] = 0

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() is np.nan,
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_high_p(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(3, 4)
            if p < 0.05:
                continue
            break

        data["s_eco"] = 0
        data["s_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertTrue(
            verification_obj.check_bool() is np.nan,
            verification_obj.check_detail()["Message"],
        )

    def test_dcv_low_corr(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, 1)
            if corr > 0.29 or corr < 0 or p > 0.05:
                continue
            break

        data["s_eco"] = 0
        data["s_ahu"] = 1

        df = pd.DataFrame(data, columns=points)

        verification_obj = run_test_verification_with_data(
            "DemandControlVentilation", df
        )
        self.assertFalse(
            verification_obj.check_bool(), verification_obj.check_detail()["Message"]
        )

    def test_dcv_negative_corr(self):
        points = [
            "v_oa",
            "s_ahu",
            "s_eco",
            "no_of_occ",
        ]
        while True:
            data, corr, p = self.generate_correlated_data(50, -5)
            if corr > 0 or p > 0.05:
                continue
            break

        data["s_eco"] = 0
        data["s_ahu"] = 1

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
        df = pd.DataFrame(pts, columns=["no_of_occ", "v_oa"])
        corr, p_value = pearsonr(df["no_of_occ"], df["v_oa"])
        return df, corr, p_value


if __name__ == "__main__":
    unittest.main()
