from constrain.checklib import RuleCheckBase
import numpy as np


class ExteriorLightingControlDaylightOff(RuleCheckBase):
    points = [
        "is_sun_up",
        "daylight_sensed",
        "daylight_setpoint",
        "total_lighting_power",
    ]
    last_sun_up_time = None
    was_sun_up = False

    def daylight_off(self, data):
        # determine the time between now and the last time the sun rose
        if data["is_sun_up"] and not self.was_sun_up:
            self.last_sun_up_time = data.name
        elif self.last_sun_up_time is None:  # initialization
            self.last_sun_up_time = data.name
        diff_since_last_sun_up = data.name - self.last_sun_up_time
        time_since_last_sun_up = diff_since_last_sun_up.total_seconds() / 60
        self.was_sun_up = data["is_sun_up"]

        # determine if enough daylight is sensed
        daylight_setpoint_met = data["daylight_sensed"] / data["daylight_setpoint"]

        # perform verification
        if daylight_setpoint_met >= 1 or time_since_last_sun_up >= 30:
            if data["total_lighting_power"] == 0:
                return True
            else:
                return False
        else:
            return np.nan

    def verify(self):
        self.result = self.df.apply(lambda d: self.daylight_off(d), axis=1)
