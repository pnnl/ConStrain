import pandas as pd
from checklib import RulesCheckBase

class LocalLoopSaturationDirectActingMax(RuleCheckBase):
    points = ["feedback_senosr", "set_point", "cmd_max"]

    def saturation_flag(self, t):
        if 0 <= t['cmd_max'] - t['feedback_sensor'] < 0.01:
            return True
        else:
            return False

    def err_above_flag(self, t):
        if t['feedback_sensor'] - t['set_point'] > 0:
            return True
        else:
            return False

    def verify(self):
        self.saturation = self.df.apply(lambda t: self.saturation_flag(t), axis=1)
        self.err_above = self.df.apply(lambda t: self.err_above_flag(t), axis=1)
        self.consistent_err_flag = pd.Series(index=self.df.index)
        prev_time = None
        prev = None
        err_start_time = None
        first_flag = True
        err_time = 0
        for cur_time, cur in self.df.iterrows():
            if self.err_above.loc[cur_time]:
                if err_start_time is None:
                    err_start_time = cur_time
                else:
                    err_time = (cur_time - err_start_time).total_seconds() / 3600 # in hours
            else:
                err_start_time = None
                err_time = 0

            if first_flag:
                self.consistent_err_flag.loc[cur_time] = False
                first_flag = False
            else:
                pass

            prev_time = cur_time
            prev = cur
