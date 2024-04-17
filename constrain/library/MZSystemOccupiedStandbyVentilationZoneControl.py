from constrain.checklib import RuleCheckBase
import numpy as np


class MZSystemOccupiedStandbyVentilationZoneControl(RuleCheckBase):
    points = [
        "zone_is_standby_mode",
        "m_oa_requested_by_system",
        "m_oa_zone_requirement",
    ]
    last_non_standby_mode_requested_m_oa = None  # expects kg/s

    def occupied_standby_ventilation_zontrol_control(self, data):
        # initialization
        if self.last_non_standby_mode_requested_m_oa is None:
            self.last_non_standby_mode_requested_m_oa = data["m_oa_requested_by_system"]
        # verification
        if data["zone_is_standby_mode"]:
            if (
                self.last_non_standby_mode_requested_m_oa
                - data["m_oa_requested_by_system"]
            ) >= data["m_oa_zone_requirement"]:
                return True
            else:
                return False
        else:
            self.last_non_standby_mode_requested_m_oa = data["m_oa_requested_by_system"]
            return np.nan

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.occupied_standby_ventilation_zontrol_control(d), axis=1
        )
