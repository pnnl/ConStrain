from constrain.checklib import RuleCheckBase


class ZoneTempControl(RuleCheckBase):
    points = ["T_set_cool", "T_set_heat"]

    def verify(self):
        self.result = (self.df["T_set_cool"] - self.df["T_set_heat"]) > 2.77
