"""
### Description
When a VAV box is in reheat mode, the ratio of VAV airflow rate to VAV max airflow rate must not be greater than the min design turndown ratio

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2 Simultaneous Heating and Cooling Limitation
- Code Subsection: 6.5.2.1 Zone Controls

### Verification Approach
- We aim to identify how VAV airflow rate varies when the VAV box is and isn't in reheat mode.

### Verification logic
```
if reheat_coil_flag:
  if V_dot_VAV_max == 0
     Untested
  if V_dot_VAV_max > 0.0 and V_dot_VAV / V_dot_VAV_max > VAV_min_turndown_design + turndown_tol
     if P_set_prev is None:
        return Untested
    elif abs(P_set - P_set_prev) > P_set_tol:
        return Untested
    else:
        return False
else
    Untested
```
### Data requirements
- reheat_coil_flag: VAV box reheat coil operation status
- V_dot_VAV: actual VAV volume flow
- V_dot_VAV_max: max VAV volume flow
- VAV_min_turndown_design: design VAV box min turndown ratio
- P_set: duct pressure setpoint
- turndown_tol: VAV turndown tolerance
- P_set_tol: pressure setpoint tolerance

"""

import numpy as np
from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheatPressureReset(RuleCheckBase):
    points = [
        "reheat_coil_flag",
        "V_dot_VAV",
        "V_dot_VAV_max",
        "VAV_min_turndown_design",
        "P_set",
        "turndown_tol",
        "P_set_tol",
    ]

    def vav_turndown_check(self, data):
        if data["reheat_coil_flag"]:
            if data["V_dot_VAV_max"] == 0:
                return "Untested"
            elif (
                data["V_dot_VAV"] / data["V_dot_VAV_max"]
                > data["VAV_min_turndown_design"] + data["turndown_tol"]
            ):
                if data["P_set_prev"] is None:
                    return "Untested"
                elif abs(data["P_set"] - data["P_set_prev"]) > data["P_set_tol"]:
                    return "Untested"
                else:
                    return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        # Copy the previous row's value in 'P_set' column to the current row
        self.df["P_set_prev"] = self.df["P_set"].shift(1).replace({np.nan: None})
        if (self.df["V_dot_VAV_max"] != 0).all():
            self.df["V_dot_ratio"] = (
                self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]
            )  # for plotting
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)
