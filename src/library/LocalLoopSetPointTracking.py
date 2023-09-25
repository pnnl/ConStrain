from checklib import RuleCheckBase


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
