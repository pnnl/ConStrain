from constrain.checklib import RuleCheckBase


class ZoneTempControl(RuleCheckBase):
    points = ["T_z_coo_set", "T_z_hea_set"]

    def verify(self):
        self.result = (self.df["T_z_coo_set"] - self.df["T_z_hea_set"]) > (
            2.77 - self.get_tolerance("temperature", "zone")
        )
