from constrain.checklib import RuleCheckBase


class VAVTurndown_Using_Average(RuleCheckBase):
    points = [
        "reheat_coil_flag",  # boolean
        "V_dot_VAV",  # actual VAV volume flow
        "V_dot_VAV_max",  # max VAV volume flow
    ]

    def verify(self):
        # Make sure every value in `V_dot_VAV_max` is greater than 0
        assert (
            self.df["V_dot_VAV_max"] > 0
        ).all(), "Not all `V_dot_VAV_max` values are greater than 0"

        self.df["V_dot_VAV_ratio"] = self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]

        # Calculate the mean ratios for reheat and no reheat conditions
        mean_reheat_ratio = float(
            self.df.loc[self.df["reheat_coil_flag"], "V_dot_VAV_ratio"].mean()
        )
        mean_no_reheat_ratio = float(
            self.df.loc[~self.df["reheat_coil_flag"], "V_dot_VAV_ratio"].mean()
        )
        self.df["result"] = mean_reheat_ratio <= mean_no_reheat_ratio

        self.result = self.df["result"]

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
