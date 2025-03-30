"""
### Description

- This verification checks that a reverse acting control loop would saturate its actuator to maximum when the error is consistently below the set point.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A

### Verification Approach

The verification monitors control loop behavior when error persists:
1. Track duration of negative control error (feedback < setpoint)
2. After 1 hour of continuous error:
   - Verify actuator command reaches maximum position
   - Allow small tolerance from maximum
3. Pass if actuator saturates, fail if it doesn't respond properly

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): any control loop with reverse-acting response
- Climate Zone(s): any
- Component(s): actuators, sensors, controllers

### Verification Algorithm Pseudo Code

```python
error_duration = 0
for each timestep:
    if value_sensor < value_setpoint:  # Negative error
        error_duration += timestep_size
        if error_duration >= 1_hour:
            if command_max - command_control <= 0:
                pass  # Proper saturation
            else:
                fail  # Should be at maximum
    else:
        error_duration = 0  # Reset duration when error clears
```

### Data requirements

- value_sensor: Process variable
  - Data Value Unit: varies by application
  - Data Point Affiliation: Control loop input

- value_setpoint: Control setpoint
  - Data Value Unit: same as value_sensor
  - Data Point Affiliation: Control loop configuration

- command_control: Actuator command
  - Data Value Unit: percent
  - Data Point Affiliation: Control loop output

- command_max: Maximum command
  - Data Value Unit: percent
  - Data Point Affiliation: Control loop configuration

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class LocalLoopSaturationReverseActingMax(RuleCheckBase):
    points = ["value_sensor", "value_setpoint", "command_control", "command_max"]

    def saturation_flag(self, t):
        if (
            0
            <= t["command_max"] - t["command_control"]
            <= self.get_tolerance("command", "general")
        ):
            return True
        else:
            return False

    def err_flag(self, t):
        if t["value_sensor"] < t["value_setpoint"]:
            return True
        else:
            return False

    def verify(self):
        self.saturation = self.df.apply(lambda t: self.saturation_flag(t), axis=1)
        self.err = self.df.apply(lambda t: self.err_flag(t), axis=1)
        self.result = pd.Series(index=self.df.index)
        err_start_time = None
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
