"""
## Local Loop Performance Verification - Direct Acting Loop Actuator Minimum Saturation

### Description

This verification checks that a direct acting control loop would saturate its actuator to minimum when the error is consistently below the set point.

### Verification logic

If the sensed data values are consistently below its set point, and after a default of 1 hour, the control command is still not saturated to minimum, then the verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value
- cmd: control command
- cmd_min: control command range minimum value

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class LocalLoopSaturationDirectActingMin(RuleCheckBase):
    points = ["feedback_sensor", "set_point", "cmd", "cmd_min"]

    def saturation_flag(self, t):
        if 0 <= t["cmd"] - t["cmd_min"] <= 0.01:
            return True
        else:
            return False

    def err_flag(self, t):
        if t["feedback_sensor"] < t["set_point"]:
            return True
        else:
            return False

    def verify(self):
        self.saturation = self.df.apply(lambda t: self.saturation_flag(t), axis=1)
        self.err = self.df.apply(lambda t: self.err_flag(t), axis=1)
        self.result = pd.Series(index=self.df.index)
        err_start_time = None
        err_time = 0
        for cur_time, cur in self.df.iterrows():
            if self.err.loc[cur_time]:
                if err_start_time is None:
                    err_start_time = cur_time
                else:
                    err_time = (
                        cur_time - err_start_time
                    ).total_seconds() / 3600  # in hours
            else:  # reset
                err_start_time = None
                err_time = 0

            if err_time > 1 and (not self.saturation.loc[cur_time]):
                result_flag = False
            else:
                result_flag = True

            self.result.loc[cur_time] = result_flag
