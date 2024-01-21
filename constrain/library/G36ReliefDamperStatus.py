"""
G36 2021

### Description

5.16.8.1. Relief dampers shall be enabled when the associated supply fan is proven ON, and disabled otherwise.

### Verification logic

```python
if relief_damper_command > 0 and supply_fan_status == 'on':
  pass
elif supply_fan_status == 'off' and relief_damper_command == 0:
  pass
else:
  fail

if not ['on', 'off'] in supply_fan_status:
  untested
```

### Data requirements

- relief_damper_command: relief damper opening (0-100)
- supply_fan_status: supply fan status (speed): ['on', 'off'] (can be replaced by binary or numeric variables)

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class G36ReliefDamperStatus(RuleCheckBase):
    points = ["relief_damper_command", "supply_fan_status"]

    def ts_verify_logic(self, t):
        if t["relief_damper_command"] > 0 and bool(t["supply_fan_status"]):
            return True
        elif t["relief_damper_command"] < 1 and (not bool(t["supply_fan_status"])):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            obs_satuses = [bool(s) for s in list(self.df["supply_fan_status"].unique())]
            if (True in obs_satuses) and (False in obs_satuses):
                return True
            else:
                return "Untested"
