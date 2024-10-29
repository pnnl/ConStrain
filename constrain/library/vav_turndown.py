from constrain.checklib import RuleCheckBase


class VAVTurndown(RuleCheckBase):
    points = [
        "reheat_coil_flag",  # boolean
        "V_dot_VAV",  # actual VAV volume flow
        "V_dot_VAV_max",  # max VAV volume flow
        "VAV_min_turndown_design",
        "turndown_tol",
    ]

    def vav_turndown_check(self, data):

        if data["reheat_coil_flag"]:
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
