"""
### Description

Section 5.6.5.3.
- When the Zone State is heating, the Heating Loop shall maintain space temperature at the heating setpoint as follows:
    c.The heating coil shall be modulated to maintain the discharge temperature at setpoint. The VAV damper shall be modulated by a control loop to maintain the measured airflow at the active setpoint.

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
if abs(temperature_air_discharge_setpoint - temperature_air_discharge) >= 0:
    if tracking_error_duration < 1_hour:
        pass  # Brief deviation acceptable
    else:
        if (temperature_air_discharge - temperature_air_discharge_setpoint >= 0) and command_coil_heat <= 1:
            pass  # Too hot, coil at minimum
        elif (temperature_air_discharge_setpoint - temperature_air_discharge >= 0) and command_coil_heat >= 100:
            pass  # Too cold, coil at maximum
        else:
            fail  # Sustained deviation without appropriate response
else:
    pass
```

### Data requirements

- mode_system: System operation mode (if mode_system is not "heating", this verification item falls into the "untested" result)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- command_coil_heat: Heating coil command
  - Data Value Unit: percent
  - Data Point Affiliation: Terminal box control

- temperature_air_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: Terminal box monitoring

- temperature_air_discharge_setpoint: Discharge air temperature setpoint
  - Data Value Unit: temperature
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
