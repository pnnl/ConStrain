from constrain.checklib import RuleCheckBase
from typing import Dict
from sklearn.linear_model import LinearRegression


class HeatRejectionFanVariableFlowControl(RuleCheckBase):
    points = ["ct_P_fan", "ct_m_fan_ratio", "ct_P_fan_dsgn", "ct_m_fan_dsgn"]

    def verify(self):
        self.df["m_ct_fan"] = self.df["ct_m_fan_ratio"] * self.df["ct_m_fan_dsgn"]
        self.df["normalized_m_ct_fan"] = self.df["m_ct_fan"] / self.df["ct_m_fan_dsgn"]
        self.df["normalized_P_ct_fan"] = self.df["ct_P_fan"] / self.df["ct_P_fan_dsgn"]

        self.df = self.df.loc[
            self.df["normalized_P_ct_fan"] > 0.0
        ]  # filter out 0 values
        self.df["normalized_m_ct_fan"] -= 1  # minus 1 to transform the data
        self.df["normalized_P_ct_fan"] -= 1

        self.df = self.df.loc[
            self.df["normalized_m_ct_fan"] > -0.5
        ]  # filter out airflow points > -0.5, since the code requirement is at this point

        # linear regression
        reg = LinearRegression(fit_intercept=False).fit(
            self.df["normalized_m_ct_fan"].values.reshape(-1, 1),
            self.df["normalized_P_ct_fan"],
        )  # fit_intercept=False is for set the intercept to 0

        if reg.coef_[0] >= 1.4:
            self.df["result"] = True
        else:
            self.df["result"] = False

        self.result = self.df["result"]

    def check_detail(self) -> Dict:
        output = {
            "Sample #": 1,
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output

    def all_plot_aio(self, plt_pts):
        pass

    def all_plot_obo(self, plt_pts):
        pass

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
