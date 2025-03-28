"""
### Description

This verification aims to check if the terminal box heating coil properly tracks its discharge air temperature setpoint during heating mode. The control should modulate the heating coil to maintain the discharge temperature while the VAV damper maintains airflow.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.6.5 Terminal Box Airflow Control with Reheat
- Code Subsection: 5.6.5.3 (c) Heating Coil Temperature Control

### Verification Approach

The verification monitors discharge air temperature tracking performance:
1. Brief deviations from setpoint (less than 1 hour) are acceptable
2. For sustained deviations:
   - If temperature is too high, heating coil should be at minimum
   - If temperature is too low, heating coil should be at maximum
3. When within tolerance, control is considered successful

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV terminal boxes with reheat
- Climate Zone(s): any
- Component(s): terminal box controllers, heating coils, temperature sensors

### Verification Algorithm Pseudo Code

```python
# Only check when in heating mode
if abs(t_discharge_sp - t_discharge) >= tol_t_tracking:
    if tracking_error_duration < 1_hour:
        pass  # Brief deviation acceptable
    else:
        if (t_discharge - t_discharge_sp >= tol_t_tracking) and cmd_coil_heat <= 1:
            pass  # Too hot, coil at minimum
        elif (t_discharge_sp - t_discharge >= tol_t_tracking) and cmd_coil_heat >= 99:
            pass  # Too cold, coil at maximum
        else:
            fail  # Sustained deviation without appropriate response
else:
    pass  # Within tolerance
```

### Data requirements

- mode_system: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System mode
  - Data Point Affiliation: System control

- cmd_coil_heat: Heating coil command
  - Data Value Unit: percent
  - Data point Description: Heating coil command
  - Data Point Affiliation: Terminal box control

- t_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data point Description: Discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

- t_discharge_sp: Discharge air temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Discharge air temperature setpoint
  - Data Point Affiliation: Terminal box control

- tol_t_tracking: Temperature tracking tolerance
  - Data Value Unit: temperature
  - Data point Description: Temperature tracking tolerance
  - Data Point Affiliation: Terminal box control
"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxHeatingCoilTracking(RuleCheckBase):
    points = [
        "mode_system",
        "command_coil_heat",
        "temperature_air_discharge",
        "temperature_air_discharge_setpoint",
    ]

    def err_flag(self, t):
        if abs(
            t["temperature_air_discharge_setpoint"] - t["temperature_air_discharge"]
        ) >= self.get_tolerance("temperature", "discharge_air"):
            return True
        else:
            return False

    def verify(self):
        self.err = self.df.apply(lambda t: self.err_flag(t), axis=1)
        err_start_time = None
        err_time = 0

        self.result = pd.Series(index=self.df.index)
        for cur_time, cur in self.df.iterrows():
            if cur["mode_system"].strip().lower() != "heating":
                result_flag = "Untested"
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
                    result_flag = "Untested"
                elif err_time > 1:
                    if (
                        cur["temperature_air_discharge"]
                        - cur["temperature_air_discharge_setpoint"]
                        >= self.get_tolerance("temperature", "discharge_air")
                        and cur["command_coil_heat"]
                        <= self.get_tolerance("damper", "command") * 100
                    ):
                        result_flag = True
                    elif (
                        cur["temperature_air_discharge_setpoint"]
                        - cur["temperature_air_discharge"]
                        >= self.get_tolerance("temperature", "discharge_air")
                        and cur["command_coil_heat"]
                        >= 100 - self.get_tolerance("damper", "command") * 100
                    ):
                        result_flag = True
                    else:
                        result_flag = False
                else:
                    print("invalid error time")
                    return False

            self.result.loc[cur_time] = result_flag
