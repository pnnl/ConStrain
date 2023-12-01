"""
G36 2021

### Description

5.1.9 To avoid abrupt changes in equipment operation, the output of every control loop shall be capable of being limited by a user adjustable maximum rate of change, with a default of 25% per minute.

### Verification logic

```python
if abs(command(current_t) - command(prev_t)) > max_rage_of_change_per_min and (current_t - prev_t <= 1 minute):
  fail
else:
  pass

```

### Data requirements

- command: control command to be verified with command range being (0-100)
- max_rate_of_change_per_min: control loop output maximum rate of change, default to 25.

"""
import pandas as pd
from constrain.checklib import RuleCheckBase
from datetime import datetime
import numpy as np


class G36OutputChangeRateLimit(RuleCheckBase):
    points = [
        "command",
        "max_rate_of_change_per_min",
    ]  # command is expected to have a data range of 100

    def change_rate_check(self, cur, prev, cur_time, prev_time):
        if prev is None:
            return np.nan
        time_delta = cur_time - prev_time
        min_change = time_delta.total_seconds() / 60
        allowable_change = min_change * cur["max_rate_of_change_per_min"]
        actual_change = abs(cur["command"] - prev["command"])
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
                self.result.loc[cur_time] = np.nan
                first_flag = False
            else:
                self.result.loc[cur_time] = self.change_rate_check(
                    cur, prev, cur_time, prev_time
                )
            prev_time = cur_time
            prev = cur
