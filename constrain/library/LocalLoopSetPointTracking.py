"""
## Local Loop Performance Verification - Set Point Tracking

### Description

This verification checks the set point tracking ability of local control loops.

### Verification logic

With a threshold of 5% of abs(set_point) (if the set point is 0, then the threshold is default to be 0.01), if the number of samples of which the error is larger than this threshold is beyond 5% of number of all samples, then this verification fails; Otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value

"""

from constrain.checklib import RuleCheckBase


class LocalLoopSetPointTracking(RuleCheckBase):
    points = ["feedback_sensor", "set_point"]

    def error_below_5percent(self, t):
        # this method checks each sample, and returns true if the error is within 5 percent of absolute setpoint value
        # if the set point is 0, a default error threshold of 0.01 is used
        err_abs = abs(t["feedback_sensor"] - t["set_point"])
        if t["set_point"] == 0:
            if err_abs > 0.01:
                return False
            else:
                return True
        if err_abs / abs(t["set_point"]) > 0.05:
            return False
        else:
            return True

    def verify(self):
        self.result = self.df.apply(lambda t: self.error_below_5percent(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False]) / len(self.result) > 0.05:
            return False
        else:
            return True
