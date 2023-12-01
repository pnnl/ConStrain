from constrain.checklib import RuleCheckBase

import numpy as np


class AutomaticOADamperControl(RuleCheckBase):
    points = ["o", "eco_onoff", "m_oa", "m_ea", "tol_o", "tol_m_oa", "tol_m_ea"]

    def automatic_oa_damper_check(self, data):
        if data["o"] < data["tol_o"]:
            if data["eco_onoff"] == 0 and (
                data["m_oa"] >= data["tol_m_oa"] or data["m_ea"] >= data["tol_m_ea"]
            ):
                return False
            else:
                return True
        else:
            return np.nan

    def verify(self):
        self.result = self.df.apply(lambda d: self.automatic_oa_damper_check(d), axis=1)
