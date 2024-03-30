"""
G36 2021
### Description

Section 5.6.5.3.

- When the Zone State is heating, the Heating Loop shall maintain space temperature at the heating setpoint as follows:
    c.The heating coil shall be modulated to maintain the discharge temperature at setpoint. The VAV damper shall be modulated by a control loop to maintain the measured airflow at the active setpoint.

### Verification logic

'''
only check the following if operation_mode is heating
if abs(dat_spt - dat) >= dat_tracking_tol (less than 1hr):
    pass
elif abs(dat_spt - dat) < dat_tracking_tol:
    pass
if dat - dat_spt >= dat_tracking_tol (continously) and heating_coil_command <= 1:
    pass
elif dat_spt - dat >= dat_tracking_tol (continuously) and vav_damper_command >= 99:
    pass
else:
    fail
end
'''

### Data requirements

- operation_mode: System operation mode
- heating_coil_command: Heating coil command
- dat: Discharge air temperature
- dat_spt: Discharge air temperature setpoint
- dat_tracking_tol: Temperature tracking tolerance

"""

from constrain.checklib import RuleCheckBase
import numpy as np
import pandas as pd


class G36ReheatTerminalBoxHeatingCoilTracking(RuleCheckBase):
    points = [
        "operation_mode",
        "heating_coil_command",
        "dat",
        "dat_spt",
        "dat_tracking_tol",
    ]

    def err_flag(self, t):
        if abs(t["dat_spt"] - t["dat"]) >= t["dat_tracking_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.err = self.df.apply(lambda t: self.err_flag(t), axis=1)
        err_start_time = None
        err_time = 0

        self.result = pd.Series(index=self.df.index)
        for cur_time, cur in self.df.iterrows():
            if cur["operation_mode"].strip().lower() != "heating":
                result_flag = np.nan
                err_start_time = None
                err_time = 0
            else:
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
                        cur["dat"] - cur["dat_spt"] >= cur["dat_tracking_tol"]
                        and cur["heating_coil_command"] <= 1
                    ):
                        result_flag = True
                    elif (
                        cur["dat_spt"] - cur["dat"] >= cur["dat_tracking_tol"]
                        and cur["heating_coil_command"] >= 99
                    ):
                        result_flag = True
                    else:
                        result_flag = False
                else:
                    print("invalid error time")
                    return False

            self.result.loc[cur_time] = result_flag
