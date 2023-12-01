"""
## Local Loop Performance Verification - Set Point Unmet Hours

### Description

This verification checks the set point tracking ability of local control loops.

### Verification logic

Instead of checking the number of samples among the whole data set for which the set points are not met, this verification checks the total accumulated time that the set points are not met within a threshold of 5% of abs(set_point) (if the set point is 0, then the threshold is default to be 0.01).

If the accumulated time of unmet set point is beyond 5% of the whole duration the data covers, then this verification fails; otherwise, it passes.

### Data requirements

- feedback_sensor: feedback sensor reading of the subject to be controlled towards a set point
- set_point: set point value

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class LocalLoopUnmetHours(RuleCheckBase):
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

    def time_error_below_5percent(self, cur, prev, cur_time, prev_time):
        if prev is None:
            return 0

        if (not self.error_below_5percent(cur)) and (
            not self.error_below_5percent(prev)
        ):
            time_delta = cur_time - prev_time
            hour_change = time_delta.total_seconds() / 3600
            return hour_change
        else:
            return 0

    def verify(self):
        self.result = self.df.apply(lambda t: self.error_below_5percent(t), axis=1)
        self.unmethours_ts = pd.Series(index=self.df.index)
        prev_time = None
        prev = None
        first_flag = True
        for cur_time, cur in self.df.iterrows():
            if first_flag:
                self.unmethours_ts.loc[cur_time] = 0
                first_flag = False
            else:
                self.unmethours_ts.loc[cur_time] = self.time_error_below_5percent(
                    cur, prev, cur_time, prev_time
                )
            prev_time = cur_time
            prev = cur

        self.total_unmet_hours = sum(self.unmethours_ts)
        self.total_hours = (
            self.unmethours_ts.index[-1] - self.unmethours_ts.index[0]
        ).total_seconds() / 3600

    def check_bool(self):
        if self.total_unmet_hours / self.total_hours > 0.05:
            return False
        else:
            return True

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
            "Total Data Duration Hours": self.total_hours,
            "Total Unmet Hours": self.total_unmet_hours,
            "Total Unmet Hours Ratio": self.total_unmet_hours / self.total_hours,
        }
        print(output)
        return output
