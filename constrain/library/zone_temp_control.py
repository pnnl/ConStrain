from constrain.checklib import RuleCheckBase


class ZoneTempControl(RuleCheckBase):
    points = ["T_z_cool_sp", "T_z_heat_sp"]

    def verify(self):
        self.result = (self.df["T_z_cool_sp"] - self.df["T_z_heat_sp"]) > 2.77
