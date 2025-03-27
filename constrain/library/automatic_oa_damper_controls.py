from constrain.checklib import RuleCheckBase
import numpy as np


class AutomaticOADamperControl(RuleCheckBase):
    points = ["o", "eco_onoff", "m_oa", "m_ea"]

    def automatic_oa_damper_check(self, data):
        if data["o"] < self.get_tolerance("ratio", "occupancy"):
            if data["eco_onoff"] == 0 and (
                float(data["m_oa"]) >= self.get_tolerance("airflow", "outdoor_air")
                or float(data["m_ea"]) >= self.get_tolerance("airflow", "exhaust_air")
            ):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.automatic_oa_damper_check(d), axis=1)
