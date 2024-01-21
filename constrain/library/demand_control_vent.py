import numpy as np
import pandas as pd

from constrain.checklib import CheckLibBase
from scipy.stats import pearsonr


class DemandControlVentilation(CheckLibBase):
    points = [
        "v_oa",
        "s_ahu",
        "s_eco",
        "no_of_occ",
    ]

    def verify(self):
        self.bool_result = None
        df_filtered = self.df.loc[
            (self.df["s_eco"] == 0.0) & (self.df["s_ahu"] != 0.0)
        ]  # filter out data when economizer isn't enabled

        if len(df_filtered) == 0:
            self.bool_result = np.nan
            self.msg = (
                "There is no samples with economizer off and AHU on, result: untested"
            )
        else:
            corr, p_value = pearsonr(df_filtered["no_of_occ"], df_filtered["v_oa"])
            if p_value > 0.05:
                self.bool_result = np.nan
                self.msg = "correlation p value too large, result: untested"
            else:
                if corr >= 0.3:
                    self.bool_result = True
                    self.msg = "positive correlation between v_oa and no_of_occ observed, result: pass"
                elif corr < 0.3 and corr > 0:
                    self.bool_result = False
                    self.msg = "positive correlation between v_oa and no_of_occ is too small, result: fail"
                else:
                    self.bool_result = False
                    self.msg = "negative correlation between v_oa and no_of_occ observed, result: fail"

        self.result = pd.Series(data=self.bool_result, index=self.df.index)

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
            "Message": self.msg,
        }
        print(output)
        return output

    def check_bool(self):
        return self.bool_result

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
