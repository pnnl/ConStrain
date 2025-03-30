"""
### Description

Section 5.5.5.4
- The VAV damper shall be modulated by a control loop to maintain the measured airflow at the active setpoint.

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
if abs(flow_volumetric_air_setpoint - flow_volumetric_air_discharge) >= 0:
    if tracking_error_duration < 1_hour:
        pass  # Brief deviation acceptable
    else:
        if (flow_volumetric_air_discharge - flow_volumetric_air_setpoint >= 0) and command_damper_vav = 0:
            pass  # Flow too high, damper at minimum
        elif (flow_volumetric_air_setpoint - flow_volumetric_air_discharge >= 0) and command_damper_vav = 100:
            pass  # Flow too low, damper at maximum
        else:
            fail  # Sustained deviation without appropriate response
else:
    pass
```

### Data requirements

- command_damper_vav: Damper command
  - Data Value Unit: percent
  - Data Point Affiliation: Terminal box control

- flow_volumetric_air_discharge: Airflow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Terminal box monitoring

- flow_volumetric_air_setpoint: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Terminal box control

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class G36TerminalBoxVAVDamperTracking(RuleCheckBase):
    points = [
        "command_damper_vav",
        "flow_volumetric_air_discharge",
        "flow_volumetric_air_setpoint",
    ]

    def err_flag(self, t):
        if abs(
            t["flow_volumetric_air_setpoint"] - t["flow_volumetric_air_discharge"]
        ) >= self.get_tolerance("airflow", "general"):
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
                    cur["flow_volumetric_air_discharge"]
                    - cur["flow_volumetric_air_setpoint"]
                    >= self.get_tolerance("airflow", "general")
                    and cur["command_damper_vav"]
                    <= self.get_tolerance("damper", "command") * 100
                ):
                    result_flag = True
                elif (
                    cur["flow_volumetric_air_setpoint"]
                    - cur["flow_volumetric_air_discharge"]
                    >= self.get_tolerance("airflow", "general")
                    and cur["command_damper_vav"]
                    >= (1 - self.get_tolerance("damper", "command")) * 100
                ):
                    result_flag = True
                else:
                    result_flag = False
            else:
                print("invalid error time")
                return False

            self.result.loc[cur_time] = result_flag
