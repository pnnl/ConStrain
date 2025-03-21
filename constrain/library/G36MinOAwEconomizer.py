"""
### Description

This verification aims to check if the minimum outdoor air control operates correctly when the economizer is active. The system should maintain outdoor air flow above minimum requirements while allowing the economizer to modulate for free cooling.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16 Air Handling Unit and Relief Fan Control Sequences
- Code Subsection: Minimum Outdoor Air Control with Economizer

### Verification Approach

The verification checks that during occupied periods when economizer is not in lockout, the outdoor air damper position and flow rate remain at or above their minimum setpoints. The actual damper modulation for temperature control is handled by the supply air temperature control loop.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with economizers
- Climate Zone(s): any
- Component(s): outdoor air dampers, airflow sensors

### Verification Algorithm Pseudo Code

```python
if not economizer_lockout(outdoor_air_temp, economizer_high_limit_sp) and sys_mode == 'occupied':
    if outdoor_damper_command >= MinOA-P and outdoor_air_flow >= MinOAsp:
        pass
    else:
        fail
else:
    untested
```

### Data requirements

- outdoor_air_temp: Outdoor air temperature
  - Data Value Unit: °C
  - Data point Description: Current outdoor air temperature
  - Data Point Affiliation: Environmental conditions

- economizer_high_limit_sp: Economizer high limit
  - Data Value Unit: °C
  - Data point Description: Temperature above which economizer is locked out
  - Data Point Affiliation: Economizer control

- outdoor_damper_command: Outdoor air damper position
  - Data Value Unit: fraction (0-1)
  - Data point Description: Current position command to outdoor air damper
  - Data Point Affiliation: Air handling unit

- min_oa_p: Minimum damper position
  - Data Value Unit: fraction (0-1)
  - Data point Description: Minimum outdoor air damper position setpoint
  - Data Point Affiliation: Air handling unit

- min_oa_sp: Minimum outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum outdoor air flow rate setpoint
  - Data Point Affiliation: Air handling unit

- outdoor_air_flow: Outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current outdoor air flow rate
  - Data Point Affiliation: Air handling unit

- sys_mode: System mode
  - Data Value Unit: enumeration
  - Data point Description: Current AHU operation mode
  - Data Point Affiliation: System control

"""

from datetime import datetime

import numpy as np
import pandas as pd
from constrain.checklib import RuleCheckBase


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
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)
