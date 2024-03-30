"""
G36 2021
### Description

Section 5.5.5.4

- The VAV damper shall be modulated by a control loop to maintain the measured airflow at the active setpoint.

### Verification logic

'''
if abs(v_spt - v) >= v_tracking_tol (less than 1hr):
    pass
elif abs(v_spt - v) < v_tracking_tol:
    pass
if v - v_spt >= v_tracking_tol (continously) and vav_damper_command <= 1:
    pass
elif v_spt - v >= v_tracking_tol (continuously) and vav_damper_command >= 99:
    pass
else:
    fail
end
'''

### Data requirements

- vav_damper_command: Terminal box VAV damper command
- v: Terminal box discharge airflow rate
- v_spt: Active airflow setpoint
- v_tracking_tol: Airflow tracking tolerance
- v_spt_tol: Active airflow setpoint tolerance

"""

from constrain.checklib import RuleCheckBase
import numpy as np
import pandas as pd


class G36TerminalBoxVAVDamperTracking(RuleCheckBase):
    points = ["vav_damper_command", "v", "v_spt", "v_tracking_tol"]

    def err_flag(self, t):
        if abs(t["v_spt"] - t["v"]) >= t["v_tracking_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.err = self.df.apply(lambda t: self.err_flag(t), axis=1)
        err_start_time = None
        err_time = 0

        self.result = pd.Series(index=self.df.index)
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

            if err_time == 0:
                result_flag = True
            elif err_time <= 1:
                result_flag = np.nan
            elif err_time > 1:
                if (
                    cur["v"] - cur["v_spt"] >= cur["v_tracking_tol"]
                    and cur["vav_damper_command"] <= 1
                ):
                    result_flag = True
                elif (
                    cur["v_spt"] - cur["v"] >= cur["v_tracking_tol"]
                    and cur["vav_damper_command"] >= 99
                ):
                    result_flag = True
                else:
                    result_flag = False
            else:
                print("invalid error time")
                return False

            self.result.loc[cur_time] = result_flag
