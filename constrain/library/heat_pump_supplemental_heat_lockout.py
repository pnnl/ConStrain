from constrain.checklib import RuleCheckBase
import numpy as np


class HeatPumpSupplementalHeatLockout(RuleCheckBase):
    points = ["C_ref", "L_op", "P_supp_ht", "C_t_mod", "C_ff_mod", "L_defrost"]

    def heating_coil_verification(self, data):
        if abs(data["P_supp_ht"]) < 0.01:
            data["result"] = 1  # True
        else:
            if data["L_defrost"] > 0.01:
                data["result"] = 1
            else:
                if data["C_op"] > data["L_op"] + (
                    data["L_op"] * self.get_tolerance("ratio", "efficiency")
                ):
                    data["result"] = 0  # False
                else:
                    data["result"] = 1
        return data

    def verify(self):
        self.df["C_op"] = self.df["C_ref"] * self.df["C_t_mod"] * self.df["C_ff_mod"]
        self.df["result"] = "Untested"
        self.df = self.df.apply(lambda r: self.heating_coil_verification(r), axis=1)
        self.result = self.df["result"]
