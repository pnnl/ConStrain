from constrain.checklib import RuleCheckBase

REHEAT_DETERMINANT_TEMP = 5.56  # deg C ~= 10 deg F


class VAVTurndown(RuleCheckBase):
    points = [
        "T_AHU_discharge",
        "T_VAV_discharge",
        "V_dot_VAV",  # actual VAV volume flow
        "V_dot_VAV_max",  # max VAV volume flow
        "VAV_min_turndown_design",
        "turndown_tol",
    ]

    def vav_turndown_check(self, data):

        if (
            data["T_VAV_discharge"] - data["T_AHU_discharge"] >= REHEAT_DETERMINANT_TEMP
        ):  # determine if VAV operation is in reheat mode
            if (
                data["V_dot_VAV_max"] > 0.0
                and data["V_dot_VAV"] / data["V_dot_VAV_max"]
                > data["VAV_min_turndown_design"] + data["turndown_tol"]
            ):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
