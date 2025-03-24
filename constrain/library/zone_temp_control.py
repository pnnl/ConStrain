from constrain.checklib import RuleCheckBase


class ZoneTempControl(RuleCheckBase):
    points = ["T_cool_set", "T_heat_set"]

    def verify(self):
        self.result = (self.df["T_cool_set"] - self.df["T_heat_set"]) > (
            2.77 - self.get_tolerance("temperature", "zone")
        )
