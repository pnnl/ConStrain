from constrain.checklib import RuleCheckBase
import numpy as np

TEMP_TOLERANCE = 0.5  # deg C


class HPWH_sizing(RuleCheckBase):
    points = [
        "T_amb",
        "HeatingRate_dx_coil",
        "HeatingRate_waterheater1",
        "HeatingRate_waterheater2",
        "T_amb_parameter",
        "HPWH_output_target_percent",
    ]

    def verify(self):
        self.df["total_hpwh_load"] = (
            self.df["HeatingRate_dx_coil"]
            + self.df["HeatingRate_waterheater1"]
            + self.df["HeatingRate_waterheater2"]
        )

        self.df["HPWH_output"] = np.where(
            self.df["total_hpwh_load"] != 0.0,
            self.df["HeatingRate_dx_coil"] / self.df["total_hpwh_load"] * 100,
            0.0,
        )

        min_hpwh_output = self.df[
            (self.df["T_amb"] > self.df["T_amb_parameter"])
            & (self.df["HPWH_output"] > 0.0)
        ]["HPWH_output"].min()
        min_hpwh_output = 0.0 if min_hpwh_output is np.nan else min_hpwh_output

        HPWH_output_target_percent = self.df["HPWH_output_target_percent"].iloc[0]

        if min_hpwh_output >= HPWH_output_target_percent:
            self.df["result"] = True
        else:
            self.df["result"] = False

        self.result = self.df["result"]

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
