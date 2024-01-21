"""
G36 2021

### Description

Section 5.16 interpretation:

- With Relief damper or relief fan
  - when economizer control is not in lockout, and actual damper positions are controlled by the SAT control loop. Above only set the lower limit for OA damper. Track MinOAsp with a reverse-acting loop and map output to
    - OA (economizer) damper minimum position MinOA-P
    - return air damper maximum position MaxRA-P
  - when economizer is in lockout for more than 10 minutes (exceeding economizer high limit conditions in Section 5.1.17), the dampers are controlled to meet minimum OA requirements
    - fully open RA damper
    - set MaxOA-P = MinOA-P, control OA damper to meet MinOAsp
    - modulate RA damper to maintain MinOAsp (return air damper position equals to MaxRA-P)

Verification Item 1:

- when economizer condition okay and occupied, check OA beyond minOA, leave actual control of dampers to SAT control

### Verification logic

```python
if not economizer_lockout(outdoor_air_temp, economizer_high_limit_sp) and sys_mode == 'occupied':
  if oudoor_damper_command >= MinOA-P and outdoor_air_flow >= MinOAsp:
    pass
  else:
    fail
else:
  untested
```

### Data requirements

- outdoor_air_temp: outdoor air temperature
- economizer_high_limit_sp: economizer lockout high limit set point
- outdoor_damper_command: outdoor air damper command
- min_oa_p: minimum outdoor air damper position set point
- min_oa_sp: minimum outdoor air flow rate setpoint
- outdoor_air_flow: outdoor air flow rate
- sys_mode: AHU system mode mode, enumeration of ['occupied', 'unoccupied', 'cooldown', 'warmup', 'setback', 'setup']

"""

import pandas as pd
from constrain.checklib import RuleCheckBase
from datetime import datetime
import numpy as np


class G36MinOAwEconomizer(RuleCheckBase):
    points = [
        "outdoor_air_temp",
        "economizer_high_limit_sp",
        "outdoor_damper_command",
        "min_oa_p",
        "outdoor_air_flow",
        "min_oa_sp",
        "sys_mode",
    ]

    def economizer_lockout(self, outdoor_air_temp, economizer_high_limit_sp):
        if outdoor_air_temp > economizer_high_limit_sp:
            return True
        else:
            return False

    def ts_verify_logic(self, t):
        if (
            not self.economizer_lockout(
                t["outdoor_air_temp"], t["economizer_high_limit_sp"]
            )
        ) and (t["sys_mode"].strip().lower() == "occupied"):
            if (t["outdoor_damper_command"] >= t["min_oa_p"]) and (
                t["outdoor_air_flow"] >= t["min_oa_sp"]
            ):
                return True
            else:
                return False
        else:
            return np.nan

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)
