"""
### Description

This verification aims to check if the VAV terminal box damper properly tracks its airflow setpoint. The damper should modulate to maintain measured airflow at the active setpoint within acceptable tolerances.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.5.5 Terminal Box Control
- Code Subsection: 5.5.5.4 VAV Damper Control

### Verification Approach

The verification monitors airflow tracking performance:
1. Brief deviations from setpoint (less than 1 hour) are acceptable
2. For sustained deviations:
   - If flow is too high, damper should be at minimum position
   - If flow is too low, damper should be at maximum position
3. When within tolerance, control is considered successful

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV terminal boxes
- Climate Zone(s): any
- Component(s): VAV dampers, airflow sensors, damper actuators

### Verification Algorithm Pseudo Code

```python
if abs(v_spt - v) >= v_tracking_tol:
    if tracking_error_duration < 1_hour:
        pass  # Brief deviation acceptable
    else:
        if (v - v_spt >= v_tracking_tol) and vav_damper_command <= 1:
            pass  # Flow too high, damper at minimum
        elif (v_spt - v >= v_tracking_tol) and vav_damper_command >= 99:
            pass  # Flow too low, damper at maximum
        else:
            fail  # Sustained deviation without appropriate response
else:
    pass  # Within tolerance
```

### Data requirements

- vav_damper_command: Damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current VAV damper position command
  - Data Point Affiliation: Terminal box control

- v: Airflow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Measured terminal box discharge airflow
  - Data Point Affiliation: Terminal box monitoring

- v_spt: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current active airflow setpoint
  - Data Point Affiliation: Terminal box control

- v_tracking_tol: Airflow tolerance
  - Data Value Unit: volumetric flow rate
  - Data point Description: Allowable deviation from airflow setpoint
  - Data Point Affiliation: Terminal box control

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


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
                result_flag = "Untested"
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
