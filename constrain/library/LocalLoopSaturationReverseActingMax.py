"""
### Description

This verification aims to check if a reverse-acting control loop properly saturates its actuator to maximum position when the controlled variable remains consistently below setpoint. This behavior is essential for maintaining proper control response and system stability.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.1.12 Control Loops
- Code Subsection: Loop Saturation Requirements

### Verification Approach

The verification monitors control loop behavior when error persists:
1. Track duration of negative control error (feedback < setpoint)
2. After 1 hour of continuous error:
   - Verify actuator command reaches maximum position
   - Allow small tolerance (1%) from maximum
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
    if feedback_sensor < setpoint:  # Negative error
        error_duration += timestep_size
        if error_duration >= 1_hour:
            if cmd_max - cmd <= 0.01:  # Within 1% of maximum
                pass  # Proper saturation
            else:
                fail  # Should be at maximum
    else:
        error_duration = 0  # Reset duration when error clears
```

### Data requirements

- v_fb: Process variable
  - Data Value Unit: varies by application
  - Data point Description: Feedback value
  - Data Point Affiliation: Control loop input

- sp: Control setpoint
  - Data Value Unit: same as v_fb
  - Data point Description: Setpoint
  - Data Point Affiliation: Control loop configuration

- out: Actuator command
  - Data Value Unit: percent
  - Data point Description: Control output
  - Data Point Affiliation: Control loop output

- out_max: Maximum command
  - Data Value Unit: percent
  - Data point Description: Maximum output
  - Data Point Affiliation: Control loop configuration

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class LocalLoopSaturationReverseActingMax(RuleCheckBase):
    points = ["feedback_sensor", "set_point", "cmd", "cmd_max"]

    def saturation_flag(self, t):
        if 0 <= t["cmd_max"] - t["cmd"] <= 0.01:
            return True
        else:
            return False

    def err_flag(self, t):
        if t["feedback_sensor"] < t["set_point"]:
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
