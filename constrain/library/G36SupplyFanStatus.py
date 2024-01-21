"""
G36 2021

### Description

Section 5.16.1.1,

- a. Supply fan shall run when system is in the Cooldown Mode, Setup Mode, or Occupied Mode.
- b. If there are any VAV-reheat boxes on perimeter zones, supply fan shall also run when system is in Setback Mode or Warmup Mode (i.e., all modes except unoccupied).

### Verification logic

```python
if has_reheat_box_on_perimeter_zones == True:
    if sys_mode != 'unoccupied' and supply_fan_status == 'off':
        fail

else:
    if sys_mode in ['occupied', 'setup', 'cooldown'] and supply_fan_staus == 'off':
        fail

if ['occupied', 'unoccupied'] in sys_mode:
  pass
else:
  untested
```

### Data requirements

- sys_mode: AHU system mode mode, enumeration of ['occupied', 'unoccupied', 'cooldown', 'warmup', 'setback', 'setup']
- has_reheat_box_on_perimeter_zones: binary flag of If there are any VAV-reheat boxes on perimeter zones.
- supply_fan_status: supply fan status (speed): ['on', 'off'] (can be replaced by binary or numeric variables)

"""
import pandas as pd
from constrain.checklib import RuleCheckBase
import numpy as np


class G36SupplyFanStatus(RuleCheckBase):
    points = ["sys_mode", "supply_fan_status", "has_reheat_box_on_perimeter_zones"]

    def ts_verify_logic(self, t):
        if bool(t["has_reheat_box_on_perimeter_zones"]):
            if (t["sys_mode"].strip().lower() != "unoccupied") and (
                not bool(t["supply_fan_status"])
            ):
                return False
            return True
        else:
            if (
                t["sys_mode"].strip().lower() in ["occupied", "setup", "cooldown"]
            ) and (not bool(t["supply_fan_status"])):
                return False
            return True

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            obs_modes = [s.lower().strip() for s in list(self.df["sys_mode"].unique())]
            if ("occupied" in obs_modes) and ("unoccupied" in obs_modes):
                return True
            else:
                return "Untested"
