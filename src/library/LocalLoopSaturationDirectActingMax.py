import pandas as pd
from checklib import RuleCheckBase


class LocalLoopSaturationDirectActingMax(RuleCheckBase):
    points = ["feedback_sensor", "set_point", "cmd", "cmd_max"]

    def saturation_flag(self, t):
        if 0 <= t["cmd_max"] - t["cmd"] <= 0.01:
            return True
        else:
            return False

    def err_flag(self, t):
        if t["feedback_sensor"] > t["set_point"]:
            return True
        else:
            return False

    def verify(self):
        self.saturation = self.df.apply(lambda t: self.saturation_flag(t), axis=1)
        self.err = self.df.apply(lambda t: self.err_flag(t), axis=1)
        self.result = pd.Series(index=self.df.index)
        err_start_time = None
        first_flag = True
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
