"""
### Description

Section 5.1.9 
- To avoid abrupt changes in equipment operation, the output of every control loop shall be capable of being limited by a user adjustable maximum rate of change, with a default of 25% per minute.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.1 General
- Code Subsection: 5.1.9 Control Loop Output Rate Limiting

### Verification Approach

The verification monitors the rate of change in control loop outputs by comparing consecutive values and their timestamps. It verifies that changes do not exceed the maximum allowed rate (default 25% per minute) when normalized to a per-minute basis.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): any control loops
- Climate Zone(s): any
- Component(s): controllers, actuators, control loops

### Verification Algorithm Pseudo Code

```python
time_delta = current_time - previous_time
allowed_change = rate_change_max * (time_delta_in_minutes)
actual_change = abs(command_control(current_t) - command_control(prev_t))

if actual_change > allowed_change:
    fail
else:
    pass
```

### Data requirements

- command_control: Control loop output
  - Data Value Unit: percent
  - Data Point Affiliation: Control loop

- rate_change_max: Maximum rate of change per minute
  - Data Value Unit: percent per minute
  - Data Point Affiliation: Control loop configuration

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class G36OutputChangeRateLimit(RuleCheckBase):
    points = [
        "command_control",
        "rate_change_max",
    ]  # command_control is expected to have a data range of 100

    def change_rate_check(self, cur, prev, cur_time, prev_time):
        if prev is None:
            return "Untested"
        time_delta = cur_time - prev_time
        min_change = time_delta.total_seconds() / 60
        allowable_change = min_change * cur["rate_change_max"]
        actual_change = abs(cur["command_control"] - prev["command_control"])
        if actual_change > allowable_change:
            return False
        else:
            return True

    def verify(self):
        self.result = pd.Series(index=self.df.index)
        prev_time = None
        prev = None
        first_flag = True
        for cur_time, cur in self.df.iterrows():
            if first_flag:
                self.result.loc[cur_time] = "Untested"
                first_flag = False
            else:
                self.result.loc[cur_time] = self.change_rate_check(
                    cur, prev, cur_time, prev_time
                )
            prev_time = cur_time
            prev = cur
